#!/usr/bin/env python3
"""
Generate inverter chain testbench for ngspice
"""
from base_generator import BaseNetlistGenerator

class InverterRingGenerator(BaseNetlistGenerator):

    def __init__(self,
        wrdata: bool = False,
        # device parameters
        w_nmos: str = "0.5u",
        w_pmos: str = "1.0u",
        l_nmos: str = "0.2u",
        l_pmos: str = "0.2u",
        Cdecap: str = "1p",
        # voltage
        vdd: float = 1.2,
    ):
        self.wrdata = wrdata

        self.w_nmos = w_nmos
        self.w_pmos = w_pmos
        self.l_nmos = l_nmos
        self.l_pmos = l_pmos

        self.Cdecap = Cdecap

        self.vdd = vdd

        super().__init__(build_dir="inv_ring")

    @property
    def title(self) -> str:
        return f"* CMOS ring oscillator with {self.num_inv} stages"

    @property
    def osdi_files(self) -> list[str]:

        if self.rf_mode == 0:
            if self.model_type == ModelType.GENERIC:
                osdi_files = ["../../osdi/psp103.osdi"]
            elif self.model_type == ModelType.PARAMSET:
                osdi_files = ["../../osdi/sg13g2_moslv.osdi"]
            elif self.model_type == ModelType.TAILORED_PARAMSET:
                osdi_files = ["../../osdi/sg13g2_moslv_tailored.osdi"]
            else:
                raise ValueError(f"Unknown model type {self.model_type}")
        else:
            if self.model_type == ModelType.GENERIC:
                osdi_files = ["../../osdi/psp103_nqs.osdi"]
            elif self.model_type == ModelType.PARAMSET:
                osdi_files = ["../../osdi/sg13g2_moslv_rf.osdi"]
            elif self.model_type == ModelType.TAILORED_PARAMSET:
                osdi_files = ["../../osdi/sg13g2_moslv_rf_tailored.osdi"]
            else:
                raise ValueError(f"Unknown model type {self.model_type}")

        return osdi_files

    @property
    def includes(self) -> list[str]:

        if self.rf_mode == 0:
            if self.model_type == ModelType.GENERIC:
                return ['.lib "../models/cornerMOSlv.lib" mos_tt']
            elif self.model_type == ModelType.PARAMSET:
                return ['.include "../models/sg13g2_moslv_mod_osdi.lib"']
        else:
            if self.model_type == ModelType.GENERIC:
                return ['.lib "../models/cornerMOSlv_rf.lib" mos_tt']
            elif self.model_type == ModelType.PARAMSET:
                return ['.include "../models/sg13g2_moslv_rf_mod_osdi.lib"']

    @property
    def models(self):

        if self.model_type == ModelType.TAILORED_PARAMSET:
            if self.rf_mode == 0:
                return [
                    ".model sg13_lv_nmos sg13g2_lv_nmos_psp_model",
                    ".model sg13_lv_pmos sg13g2_lv_pmos_psp_model"
                ]
            else:
                return [
                    ".model sg13_lv_nmos sg13g2_lv_nmos_psp_rf_model",
                    ".model sg13_lv_pmos sg13g2_lv_pmos_psp_rf_model"
                ]

    @property
    def options(self) -> dict[str, str]:
        return {
            "noacct": None,
            "nomod": None,
            "nopage": None,
            "klu": None,
            "reltol": "1e-4"}

    def add_netlist(self) -> None:

        self.lines.append("")

        self.lines.append("* Inverter subcircuit")
        self.lines.append(".subckt inverter in out vdd gnd")
        if self.model_type in [ModelType.GENERIC, ModelType.PARAMSET]:
            self.lines.append(f"Xpm out in vdd vdd sg13_lv_pmos w={self.w_pmos} l={self.l_pmos}")
            self.lines.append(f"Xmn out in gnd gnd sg13_lv_nmos w={self.w_nmos} l={self.l_nmos}")
        elif self.model_type == ModelType.TAILORED_PARAMSET:
            self.lines.append(f"Npm out in vdd vdd sg13_lv_pmos")
            self.lines.append(f"Nmn out in gnd gnd sg13_lv_nmos")
        self.lines.append(".ends")
        self.lines.append("")

        self.lines.append("i0 0 1 dc 0 pulse 0 1e-05 0.1n 0.1n 0.1n 0.3n")
        self.lines.append("")

        self.lines.append("* Inverter ring")
        for i in range(1, self.num_inv + 1):
            in_node = i
            out_node = i + 1 if i < self.num_inv else 1  # Last inverter feeds back to node 1
            self.lines.append(f"xu{i} {in_node} {out_node} vdd 0 inverter")

        self.lines.append("")
        self.lines.append("* Supply voltage")
        self.lines.append(f"vdd vdd 0 {self.vdd}")
        self.lines.append( "* Load capacitance")
        self.lines.append( f"Cdecap vdd 0 {self.Cdecap}")
        self.lines.append("")

        # Initial conditions
        nodes = list(range(1, self.num_inv + 1))
        per_line = 5
        for i in range(0, len(nodes), per_line):
            chunk = nodes[i:i + per_line]
            terms = " ".join(f"v({node})=0.0" for node in chunk)
            self.lines.append(f".ic {terms}")
        self.lines.append("")

    def add_control_block(self) -> None:

        self.lines.append(".control")
        self.lines.append("  set num_threads = 1")
        self.lines.append("")

        self.lines.append("  * load osdi files")
        for osdi_file in self.osdi_files:
            self.lines.append(f"  pre_osdi {osdi_file}")

        self.lines.append("")

        # Save only fixed nodes for fair benchmark as num_inv increases
        self.lines.append( "  * save only so that storage does not scale with chain size")
        self.lines.append(f"  save v(1)")
        self.lines.append("")

        # Transient analysis
        tran_cmd = f"tran {self.tran_step} {self.tran_stop} 0 {self.tran_max} uic"
        self.lines.append(f"  {tran_cmd}")
        self.lines.append("")
        self.lines.append("  * print performance and resource usage")
        self.lines.append("  rusage all")
        self.lines.append("")

        if self.wrdata:
            self.lines.append("  * write output to file")
            self.lines.append("  set wr_vecnames")
            self.lines.append("  set wr_singlescale")
            self.lines.append(f"  wrdata check/{self.net_name}.sp.out v(1)")

        self.lines.append("  * clean exit after simulation")
        self.lines.append("  set noaskquit")
        self.lines.append("  quit")

        self.lines.append(".endc")

    def generate_netlist(self,
        num_inv: int,
        rf_mode: int,
        tran_stop: float,
        tran_step: float,
        tran_max: float
    ) -> str:

        self.num_inv = num_inv
        self.rf_mode = rf_mode
        self.tran_stop = tran_stop
        self.tran_step = tran_step
        self.tran_max = tran_max

        if self.rf_mode == 0:
            name = f"tb_moslv_inv_ring_N{num_inv}_tt"
        else:
            name = f"tb_moslv_rf_inv_ring_N{num_inv}_tt"

        return super().generate_netlist(name)

if __name__ == "__main__":

    from base_generator import ModelType

    # Average propagation delay of one inverter
    tpd = 0.15679572639369496 * 1e-9  # seconds
    num_cycles = 10
    points_per_cycle = 100

    num_inv_list = [11, 21, 51, 101]
    gen = InverterRingGenerator(wrdata=True)

    for rf_mode in [0, 1]:
        for model_type in [ModelType.GENERIC, ModelType.PARAMSET, ModelType.TAILORED_PARAMSET]:
            gen.set_model_type(model_type)
            for num_inv in num_inv_list:
                # Calculate period and simulation parameters
                T = 2 * num_inv * tpd
                # Update timing parameters for this configuration
                tran_stop = num_cycles * T
                tran_step = T / points_per_cycle
                tran_max = tran_step

                gen.generate_netlist(num_inv, rf_mode, tran_stop, tran_step, tran_max)



