#!/usr/bin/env python3
"""
Generate inverter chain testbench for ngspice
"""
from base_generator import BaseNetlistGenerator


class InverterChainGenerator(BaseNetlistGenerator):

    def __init__(self,
        wrdata: bool = False,
        w_nmos: float = 0.35e-6,
        w_pmos: float = 0.28e-6,
        l_nmos: float = 0.34e-6,
        l_pmos: float = 0.34e-6,
        vdd: float = 1.2,
        cload: float = 1e-14,
        tran_stop: float = 100e-9,
        tran_step: float = 0.1e-9,
        tran_max: float = 0.1e-9
    ):

        self.wrdata = wrdata
        self.w_nmos = w_nmos
        self.w_pmos = w_pmos
        self.l_nmos = l_nmos
        self.l_pmos = l_pmos
        self.vdd = vdd
        self.cload = cload
        self.tran_stop = tran_stop
        self.tran_step = tran_step
        self.tran_max = tran_max

        super().__init__()

    @property
    def title(self):
        return "* CMOS inverter chain"

    @property
    def osdi_files(self) -> list[str]:

        if self.model_type == "generic":
            osdi_files = ["psp103.osdi", "psp103_nqs.osdi"]
        elif self.model_type == "paramset":
            osdi_files = ["sg13g2_moslv.osdi"]
        else:
            raise ValueError(f"Unknown model type {self.model_type}")

        return osdi_files

    @property
    def includes(self) -> list[str]:
        if self.model_type == "generic":
            return ['.lib "cornerMOSlv.lib" mos_tt']
        elif self.model_type == "paramset":
            return ['.include "sg13g2_moslv_mod_osdi.lib"']

    @property
    def options(self) -> dict[str, str]:
        return {"reltol": "1e-4"}

    def add_netlist(self) -> None:

        self.lines.append(f"VDD vdd 0 {self.vdd}")
        self.lines.append(f"VIN in 0 PWL(0 0 10n 0 11n {self.vdd} {self.tran_stop * 1e9}n {self.vdd})")
        self.lines.append("")
        self.lines.append("* Inverter subcircuit")
        self.lines.append(".subckt inv in out vdd gnd")
        self.lines.append(f"X1 out in vdd vdd sg13_lv_pmos w={self.w_pmos} l={self.l_pmos} rfmode=0")
        self.lines.append(f"X2 out in gnd gnd sg13_lv_nmos w={self.w_nmos} l={self.l_nmos} rfmode=0")
        self.lines.append(".ends")
        self.lines.append("")
        self.lines.append("* Inverter instances")
        for i in range(1, self.num_inv + 1):
            if i == 1:
                in_node = "in"
            else:
                in_node = f"n{i-1}"

            if i == self.num_inv:
                out_node = "out"
            else:
                out_node = f"n{i}"
            self.lines.append(f"X{i} {in_node} {out_node} vdd 0 inv")
        self.lines.append("")
        self.lines.append("* Load capacitance")
        self.lines.append(f"CL out 0 {self.cload}")
        self.lines.append("")

    def add_control_block(self) -> None:

        self.lines.append(".control")

        # Print resource usage statistics
        self.lines.append("  * print resource usage statistics")
        self.lines.append("  rusage all")
        self.lines.append("  set")
        self.lines.append("")

        # Transient analysis
        tran_cmd = f"tran {self.tran_step} {self.tran_stop} 0 {self.tran_max}"
        self.lines.append(f"  {tran_cmd}")
        self.lines.append("")

        if self.wrdata:
            self.lines.append("  * write output to file")
            self.lines.append("  set wr_vecnames")
            self.lines.append("  set wr_singlescale")
            self.lines.append(f"  wrdata ../check/{self.net_name}_{self.model_type}.sp.out v(in) v(out) i(VDD)")

        self.lines.append("  * clean exit after simulation")
        self.lines.append("  set noaskquit")
        self.lines.append("  quit")

        self.lines.append(".endc")

    def generate_netlist(self, num_inv: int) -> str:

        self.num_inv = num_inv
        return super().generate_netlist(f"tb_moslv_inv_chain_N{num_inv}_tt")

if __name__ == "__main__":

    from base_generator import ModelType

    num_inv_list = [10, 50, 100, 500, 1000]
    gen = InverterChainGenerator(wrdata=True)
    gen.set_model_type(ModelType.PARAMSET)
    gen.clean_build()
    gen.generate_spiceinit()

    for num_inv in num_inv_list:
        gen.generate_netlist(num_inv)


