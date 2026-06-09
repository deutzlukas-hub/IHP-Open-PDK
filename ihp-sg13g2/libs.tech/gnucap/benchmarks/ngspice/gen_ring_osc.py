#!/usr/bin/env python3
"""
Generate ring oscillator testbench for ngspice
"""
from base_generator import BaseNetlistGenerator, ModelType

class RingOscillatorGenerator(BaseNetlistGenerator):

    def __init__(self,
        wrdata: bool = False,
        w: float = 1.0e-6,
        l: float = 0.45e-6,
        pfact: float = 2.0,
        vdd: float = 1.2,
    ):

        self.wrdata = wrdata
        self.w = w
        self.l = l
        self.pfact = pfact
        self.vdd = vdd

        super().__init__()

    @property
    def title(self):
        return f"* CMOS ring oscillator with {self.num_inv} stages"

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
        if self.model_type == ModelType.GENERIC:
            return ['.lib "cornerMOSlv.lib" mos_tt']
        elif self.model_type == ModelType.PARAMSET:
            return ['.include "sg13g2_moslv_mod_osdi.lib"']

    @property
    def options(self) -> dict[str, str]:
        return {
            "method": "trap",
            "klu": None,
        }

    def add_netlist(self) -> None:

        # Inverter subcircuit with parametric W, L, pfact
        self.lines.append(".subckt inverter in out vdd vss")
        self.lines.append(f"  Xpm out in vdd vdd sg13_lv_pmos w={self.w} l={self.l}")
        self.lines.append(f"  Xmn out in vss vss sg13_lv_nmos w={self.pfact * self.w} l={self.l}")
        self.lines.append(".ends")
        self.lines.append("")

        # Kick-start pulse source
        self.lines.append(f"i0 0 1 dc 0 pulse 0 10u 0.1n 0.1n 0.1n 0.3n")
        self.lines.append("")

        # Generate ring oscillator inverter instances
        for i in range(1, self.num_inv + 1):
            in_node = i
            out_node = i + 1 if i < self.num_inv else 1  # Last inverter feeds back to node 1
            self.lines.append(f"xu{i} {in_node} {out_node} vdd 0 inverter")

        self.lines.append("")
        self.lines.append(f"vdd vdd 0 {self.vdd}")
        self.lines.append("Cdecap vdd 0 1p")
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

        # Print resource usage statistics
        self.lines.append("  * print resource usage statistics")
        self.lines.append("  rusage all")
        self.lines.append("  set")
        self.lines.append("")

        # Transient analysis
        tran_cmd = f"tran {self.tran_step} {self.tran_stop} 0 {self.tran_max} uic"
        self.lines.append(f"  {tran_cmd}")
        self.lines.append("")

        # Write output data
        if self.wrdata:
            self.lines.append( "  * write output to file")
            self.lines.append( "  set wr_vecnames")
            self.lines.append( "  set wr_singlescale")
            self.lines.append(f"  wrdata ../check/{self.net_name}_{self.model_type}.sp.out v(1) i(vdd)")
            self.lines.append("")

        # Clean exit after simulation
        self.lines.append("  * clean exit after simulation")
        self.lines.append("  set noaskquit")
        self.lines.append("  quit")

        self.lines.append(".endc")

    def generate_netlist(self,
        num_inv: int,
        tran_stop: float,
        tran_step: float,
        tran_max: float
        ):

        """Generate ring oscillator netlist with specified number of inverters."""
        if num_inv % 2 == 0:
            print(f"Warning: num_inv={num_inv} is even. Ring oscillators typically need odd number of stages.")

        self.num_inv = num_inv
        self.tran_stop = tran_stop
        self.tran_step = tran_step
        self.tran_max = tran_max

        return super().generate_netlist(f"tb_moslv_ring_osc_N{num_inv}_tt")


if __name__ == "__main__":

    # Average propagation delay of one inverter
    tpd = 0.15679572639369496 * 1e-9  # seconds
    num_cycles = 50
    points_per_cycle = 100

    gen = RingOscillatorGenerator(wrdata=True)
    gen.set_model_type(ModelType.PARAMSET)
    gen.clean_build()
    gen.generate_spiceinit()

    for num_inverters in [11, 51, 101]:
        # Calculate period and simulation parameters
        T = 2 * num_inverters * tpd
        # Update timing parameters for this configuration
        gen.tran_stop = num_cycles * T
        gen.tran_step = T / points_per_cycle
        gen.tran_max = gen.tran_step

        gen.generate_netlist(num_inverters)
