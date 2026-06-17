#!/usr/bin/env python3
"""
Generate inverter chain testbench for ngspice
"""
from base_generator import BaseNetlistGenerator

class InverterChainGenerator(BaseNetlistGenerator):

    def __init__(self,
        wrdata: bool = False,
        # device parameters
        w_nmos: float = 0.5e-6,
        w_pmos: float = 1.0e-6,
        l_nmos: float = 0.2e-6,
        l_pmos: float = 0.2e-6,
        cload: float = 1e-14,
        # input parameters
        vdd: float = 1.2,
        input: str = "step",
        pulse_delay: float = "10n",
        pulse_rise: float = "100p",
        pulse_fall: float = "100p",
        pulse_width: float = "10n",
        pulse_period: float = "20n",
        # transient
        tran_stop: float = "110n",
        tran_step: float = "0.1n",
        tran_max: float = "0.1n",
    ):
        self.wrdata = wrdata

        self.w_nmos = w_nmos
        self.w_pmos = w_pmos
        self.l_nmos = l_nmos
        self.l_pmos = l_pmos
        self.cload = cload

        self.input = input
        self.vdd = vdd
        self.pulse_delay = pulse_delay
        self.pulse_rise = pulse_rise
        self.pulse_fall = pulse_fall
        self.pulse_width = pulse_width
        self.pulse_period = pulse_period

        # single-step PWL parameters
        self.pwl_delay: float = 10e-9
        self.pwl_edge_time: float = 100e-12

        # trans parameters
        self.tran_stop = tran_stop
        self.tran_step = tran_step
        self.tran_max = tran_max

        super().__init__(build_dir="inv_chain")

    @property
    def title(self) -> str:
        return "* CMOS inverter chain"

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


    def input_source_line(self) -> str:

        if self.input == "step":
            return (
                f"VIN in 0 PWL("
                f"0 0 "
                f"10n 0 "
                f"11n {self.vdd} "
                f"{self.tran_stop * 1e9}n {self.vdd})"
            )

        if self.input == "pulse":
            # PULSE(VLOW VHIGH DELAY RISE FALL WIDTH PERIOD)
            return (
                f"VIN in 0 PULSE(0 {self.vdd} "
                f"{self.pulse_delay} "
                f"{self.pulse_rise} "
                f"{self.pulse_fall} "
                f"{self.pulse_width} "
                f"{self.pulse_period})"
            )

    def add_netlist(self) -> None:

        self.lines.append(f"VDD vdd 0 {self.vdd}")
        self.lines.append(self.input_source_line())
        self.lines.append("")
        self.lines.append("* Inverter subcircuit")
        self.lines.append(".subckt inv in out vdd gnd")

        if self.model_type in [ModelType.GENERIC, ModelType.PARAMSET]:
            self.lines.append(f"X1 out in vdd vdd sg13_lv_pmos w={self.w_pmos} l={self.l_pmos}")
            self.lines.append(f"X2 out in gnd gnd sg13_lv_nmos w={self.w_nmos} l={self.l_nmos}")
        elif self.model_type == ModelType.TAILORED_PARAMSET:
            self.lines.append(f"N1 out in vdd vdd sg13_lv_pmos")
            self.lines.append(f"N2 out in gnd gnd sg13_lv_nmos")
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

        self.lines.append("  * load osdi files")
        for osdi_file in self.osdi_files:
            self.lines.append(f"  pre_osdi {osdi_file}")

        self.lines.append("")
        # Transient analysis
        tran_cmd = f"tran {self.tran_step} {self.tran_stop} 0 {self.tran_max}"
        self.lines.append(f"  {tran_cmd}")
        self.lines.append("")
        self.lines.append("  * print performance and resource usage")
        self.lines.append("  rusage all")
        self.lines.append("")

        if self.wrdata:
            self.lines.append("  * write output to file")
            self.lines.append("  set wr_vecnames")
            self.lines.append("  set wr_singlescale")
            self.lines.append(f"  wrdata check/{self.net_name}.sp.out v(in) v(out) i(VDD)")

        self.lines.append("  * clean exit after simulation")
        self.lines.append("  set noaskquit")
        self.lines.append("  quit")

        self.lines.append(".endc")

    def generate_netlist(self, num_inv: int, rf_mode: int) -> str:

        self.num_inv = num_inv
        self.rf_mode = rf_mode

        if self.rf_mode == 0:
            name = f"tb_moslv_inv_chain_N{num_inv}_tt"
        else:
            name = f"tb_moslv_rf_inv_chain_N{num_inv}_tt"

        return super().generate_netlist(name)

if __name__ == "__main__":

    from base_generator import ModelType

    # num_inv_list = [500, 1000, 2000, 4000]
    num_inv_list = [10, 50, 100] # , 2000, 4000]
    gen = InverterChainGenerator(wrdata=False, input="pulse")
    #gen.clean_build()

    for rf_mode in [0, 1]:
        for model_type in [ModelType.GENERIC, ModelType.PARAMSET, ModelType.TAILORED_PARAMSET]:
            gen.set_model_type(model_type)
            for num_inv in num_inv_list:
                gen.generate_netlist(num_inv, rf_mode)


