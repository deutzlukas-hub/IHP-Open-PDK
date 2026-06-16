import warnings
import ctypes
import os
from pathlib import Path

import osdi

PARA_TY_MASK = 3
PARA_TY_REAL = 0
PARA_TY_INT = 1
PARA_TY_STR = 2

PARA_KIND_MASK = 3 << 30
PARA_KIND_MODEL = 0 << 30
PARA_KIND_INST = 1 << 30
PARA_KIND_OPVAR = 2 << 30

class OsdiFile():

    def __init__(self, osdi_file_path: Path):
        self.osdi_file_path = osdi_file_path
        self.osdi_filename = osdi_file_path.name
        self.load_file()

    # ==========================================================================
    # Primitive types
    # ==========================================================================
    @staticmethod
    def cstr(value):
        return ctypes.cast(value, ctypes.c_char_p).value.decode("utf-8", errors="replace")

    def uint32(self, name: str):
        return ctypes.c_uint32.in_dll(self.osdi_lib, name).value

    # ==========================================================================
    # Load osdi file
    # ==========================================================================
    def load_file(self):

        self.Descriptor = osdi.struct_OsdiDescriptor

        mode = os.RTLD_LOCAL
        if hasattr(os, "RTLD_NOW"):
            mode |= os.RTLD_NOW
        else:
            assert False

        # load osdi
        path = self.osdi_file_path.resolve(strict=True)
        self.osdi_lib = ctypes.CDLL(str(path), mode=mode)
        # OSDI 0.4 should have this
        self.OSDI_VERSION_MAJOR = self.uint32("OSDI_VERSION_MAJOR")
        self.OSDI_VERSION_MINOR = self.uint32("OSDI_VERSION_MINOR")
        self.num_desc = self.uint32("OSDI_NUM_DESCRIPTORS")

        osdi_desc_size = self.uint32("OSDI_DESCRIPTOR_SIZE")
        py_desc_size = ctypes.sizeof(self.Descriptor)

        if py_desc_size > osdi_desc_size:
            warnings.warn(
                f"Python OsdiDescriptor is larger than OSDI_DESCRIPTOR_SIZE: "
                f"python={py_desc_size}, library={osdi_desc_size}",
                RuntimeWarning,
                stacklevel=2,
            )

        desc_size = py_desc_size

        first_desc = self.Descriptor.in_dll(self.osdi_lib, "OSDI_DESCRIPTORS")
        base_addr = ctypes.addressof(first_desc)

        self.descriptors = []
        for i in range(self.num_desc):
            desc = self.Descriptor.from_address(base_addr + i * osdi_desc_size)
            self.descriptors.append(self.parse_descriptor(desc, i))

        return

    # ==========================================================================
    # Parse data structures
    # ==========================================================================
    def parse_descriptor(self, desc, index: int):

        num_params = int(desc.num_params)
        num_instance_params = int(desc.num_instance_params)
        num_model_params = num_params - num_instance_params
        num_opvars = int(desc.num_opvars)

        assert num_model_params >= 0, "num_model_params must be positive"

        desc_dict = {
            "index": index,
            "name": OsdiFile.cstr(desc.name),
            "num_nodes": int(desc.num_nodes),
            "num_terminals": int(desc.num_terminals),
            "num_jacobian_entries": int(desc.num_jacobian_entries),
            "num_noise_sources": int(desc.num_noise_src),
            "num_states": int(desc.num_states),
            "instance_size": int(desc.instance_size),
            "model_size": int(desc.model_size),
            "num_params_total": num_params,
            "num_instance_params": num_instance_params,
            "num_model_params": num_model_params,
            "num_opvars": num_opvars,
            "nodes": self.parse_nodes(desc),
            "opvars": [],
            "instance_parameters": [],
            "model_parameters": [],
        }

        if num_params or num_opvars:
            assert desc.param_opvar, "expected param_opvar to be non-null"

        # OSDI ordering:
        #   instance parameters next
        #   model parameters last
        #   opvars first
        #
        # num_params includes both instance and model parameters.
        base = desc.param_opvar

        start = 0
        stop = start + num_instance_params
        for j in range(start, stop):
            desc_dict["instance_parameters"].append(self.parse_param(base[j], "instance"))

        start = stop
        stop = start + num_model_params
        for j in range(start, stop):
            desc_dict["model_parameters"].append(self.parse_param(base[j], "model"))

        start = stop
        stop = start + num_opvars
        for j in range(start, stop):
            desc_dict["opvars"].append(self.parse_param(base[j], "opvar"))

        return desc_dict

    def parse_nodes(self, desc):

        nodes = []

        if not desc.nodes:
            return nodes

        for i in range(int(desc.num_nodes)):
            node = desc.nodes[i]
            nodes.append(
                {
                    "index": i,
                    "name": self.cstr(node.name),
                    "units": self.cstr(node.units),
                    "residual_units": self.cstr(node.residual_units),
                    "is_flow": bool(node.is_flow),
                }
            )

        return nodes

    def parse_param(self, param, expected_kind: str):

        names = []
        # OSDI stores canonical name + aliases.
        for i in range(param.num_alias + 1):
            names.append(self.cstr(param.name[i]))

        flags = int(param.flags)

        type_flag = flags & PARA_TY_MASK
        if  type_flag == PARA_TY_REAL:
            ty = "real"
        elif type_flag == PARA_TY_INT:
            ty = "integer"
        elif type_flag == PARA_TY_STR:
            ty = "string"
        else:
            assert False, f"unknown parameter kind"

        kind_flag = flags & PARA_KIND_MASK
        if kind_flag == PARA_KIND_MODEL:
            actual_kind = "model"
        elif kind_flag == PARA_KIND_INST:
            actual_kind = "instance"
        elif kind_flag == PARA_KIND_OPVAR:
            actual_kind = "opvar"
        else:
            assert False, f"unknown parameter kind"

        assert actual_kind == expected_kind, f"expected {expected_kind} but got {actual_kind}"

        return {
            "name": names[0],
            "aliases": names[1:],
            "type": ty,
            "kind": actual_kind,
            "description": self.cstr(param.description),
            "units": self.cstr(param.units),
            "flags": flags,
            "len": int(param.len),
        }

    # ==========================================================================
    # Print data
    # ==========================================================================
    def print_descriptors(self):

        print(f"Osdi descriptors in {self.osdi_filename}:")
        for idx, desc in enumerate(self.descriptors):
            print(f'descriptor {idx}: {desc["name"]}')

    def print_memory_footprint(self, idx):
        desc = self.descriptors[idx]
        print(f"Memory footprint of descriptor {desc["name"]}:")
        print(f'instance_size: {desc['instance_size']} bytes')
        print(f'model size: {desc['model_size']} bytes')

    def print_param_meta_data(self, idx):
        desc = self.descriptors[idx]
        print(f'Param meta data of descriptor {idx}: {desc["name"]:}')
        print(f'num_params_total: {desc["num_params_total"]}')
        print(f'num_instance_params: {desc["num_instance_params"]}')
        print(f'num_model_params: {desc["num_model_params"]}')
        print(f'num_opvars: {desc["num_opvars"]}')

    def print_params(self, idx, kind: str = "model", type=None):
        desc = self.descriptors[idx]
        print(f'{kind} parameters of descriptor {idx}: {desc["name"]:} \n')

        if kind == "instance":
            params = desc["instance_parameters"]
        elif kind == "model":
            params = desc["model_parameters"]
        elif kind == "opvars":
            params = desc["opvars"]

        for param in params:
            if type is not None:
                if param["type"] != type:
                    continue

            print(f'  {param["name"]}: {param["type"]} {param["kind"]}')


def inspect_psp103():

    osdi_path = Path("psp103.osdi")
    osdi = OsdiFile(osdi_path)
    osdi.print_descriptors()
    osdi.print_param_meta_data(0)
    osdi.print_memory_footprint(0)

def inspect_paramset():

    osdi_path = Path("sg13g2_moslv.osdi")
    osdi = OsdiFile(osdi_path)
    osdi.print_descriptors()
    osdi.print_param_meta_data(0)
    osdi.print_memory_footprint(0)
    osdi.print_param_meta_data(1)
    osdi.print_memory_footprint(1)

def inspect_paramset_fixed():

    osdi_path = Path("sg13g2_moslv.osdi")
    osdi = OsdiFile(osdi_path)
    osdi.print_descriptors()
    osdi.print_param_meta_data(0)
    osdi.print_memory_footprint(0)
    osdi.print_param_meta_data(1)
    osdi.print_memory_footprint(1)

def inspect_fixed_paramset():

    osdi_path = Path("sg13g2_moslv_fixed.osdi")
    osdi = OsdiFile(osdi_path)
    osdi.print_descriptors()
    osdi.print_param_meta_data(0)
    osdi.print_memory_footprint(0)
    osdi.print_param_meta_data(1)
    osdi.print_memory_footprint(1)


def inspect_taylored():

    osdi_path = Path("sg13g2_moslv_mult.osdi")
    osdi = OsdiFile(osdi_path)
    osdi.print_descriptors()
    osdi.print_param_meta_data(0)
    osdi.print_memory_footprint(0)
    osdi.print_param_meta_data(1)
    osdi.print_memory_footprint(1)

def psp103_params():

    osdi_path = Path("./psp103.osdi")
    osdi = OsdiFile(osdi_path)
    osdi.print_param_meta_data(0)
    osdi.print_params(0, "instance", type="integer")
    osdi.print_params(0, "model", type="integer")

def fixed_paramset_params():

    osdi_path = Path("sg13g2_moslv_fixed.osdi")
    osdi = OsdiFile(osdi_path)
    osdi.print_param_meta_data(0)
    osdi.print_params(0, "instance")
    osdi.print_params(0, "model")



def sg13g2_moslv_paramset_tt_params():

    osdi_path = Path("sg13g2_moslv.osdi")
    osdi = OsdiFile(osdi_path)
    osdi.print_param_meta_data(0)
    osdi.print_params(0, "instance")
    osdi.print_params(0, "model")

def main():

    pass

if __name__ == "__main__":

    # inspect_psp103()
    # inspect_paramset()
    # inspect_paramset_fixed()
    # inspect_taylored()

    # psp103_params()
    # sg13g2_moslv_paramset_tt_params()
    # fixed_paramset_params()

    osdi_path = Path("psp103.osdi")
    osdi_file = OsdiFile(osdi_path)
    osdi_file.print_param_meta_data(0)

    print("")
    print("")

    osdi_path = Path("sg13g2_moslv_fixed.osdi")
    osdi_file = OsdiFile(osdi_path)
    osdi_file.print_param_meta_data(0)

