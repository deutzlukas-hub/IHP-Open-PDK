
from base_generator import BaseNetlistGenerator
from base_generator import ModelType

class C6288Generator(BaseNetlistGenerator):
    def __init__(self,
        wrdata: bool = False,
        vdd: float = 1.2,
        vin_period: float = 100,
        vin_rise: float = 0.1,
        vin_fall: float = 0.1,
        tran_stop: float = 1,
    ):
        self.wrdata = wrdata
        self.vdd = vdd
        self.vin_period = vin_period
        self.vin_rise = vin_rise
        self.vin_fall = vin_fall
        self.tran_stop = tran_stop

        super().__init__(build_dir="multiplier")

    @property
    def title(self) -> str:
        return  (
        "* C6288 16x16 multiplier"  
        "* ISCAS-85 benchmark circuit"
        )

    @property
    def osdi_files(self) -> list[str]:

        if self.model_type == ModelType.GENERIC:
            osdi_files = ["../../osdi/psp103.osdi"]
        elif self.model_type == ModelType.PARAMSET:
            osdi_files = ["../../osdi/sg13g2_moslv.osdi"]
        else:
            raise ValueError(f"Unknown model type {self.model_type}")

        return osdi_files

    @property
    def includes(self) -> list[str]:

        includes = []

        if self.model_type == ModelType.GENERIC:
            includes.append('.lib "../models/cornerMOSlv.lib" mos_tt')
        elif self.model_type == ModelType.PARAMSET:
            includes.append('.include "../models/sg13g2_moslv_mod_osdi.lib"')

        includes.append(f'.include "multiplier.inc"')

        return includes

    @property
    def options(self) -> dict[str, str | None]:

        return {
            "noacct": None,
            "nomod": None,
            "nopage": None,
            "klu": None}

    def add_netlist(self) -> None:

        self.lines.append(f"vdd vdd 0 {self.vdd}")
        self.lines.append(f"vss vss 0 0")
        self.lines.append("")

        self.lines.append("* instantiate the multiplier")
        self.lines.append("x1  a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11 a12 a13 a14 a15")
        self.lines.append("+   b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 b14 b15")
        self.lines.append("+   p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15")
        self.lines.append("+   p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31")
        self.lines.append("+ c6288")
        self.lines.append("")

        self.lines.append("* each input receives same pulse waveform ")
        self.lines.append(".subckt v01 out ref")
        self.lines.append(f"  vdrv int 0 pulse(0 {self.vdd} 0.1n {self.vin_rise}n {self.vin_fall}n {self.vin_period}n)")
        self.lines.append("  rdrv int out r=1")
        self.lines.append(".ends")
        self.lines.append("")

        self.lines.append("xa0  a0  0 v01")
        self.lines.append("xa1  a1  0 v01")
        self.lines.append("xa2  a2  0 v01")
        self.lines.append("xa3  a3  0 v01")
        self.lines.append("xa4  a4  0 v01")
        self.lines.append("xa5  a5  0 v01")
        self.lines.append("xa6  a6  0 v01")
        self.lines.append("xa7  a7  0 v01")
        self.lines.append("xa8  a8  0 v01")
        self.lines.append("xa9  a9  0 v01")
        self.lines.append("xa10 a10 0 v01")
        self.lines.append("xa11 a11 0 v01")
        self.lines.append("xa12 a12 0 v01")
        self.lines.append("xa13 a13 0 v01")
        self.lines.append("xa14 a14 0 v01")
        self.lines.append("xa15 a15 0 v01")
        self.lines.append("")
        self.lines.append("xvb0  b0  0 v01")
        self.lines.append("xvb1  b1  0 v01")
        self.lines.append("xvb2  b2  0 v01")
        self.lines.append("xvb3  b3  0 v01")
        self.lines.append("xvb4  b4  0 v01")
        self.lines.append("xvb5  b5  0 v01")
        self.lines.append("xvb6  b6  0 v01")
        self.lines.append("xvb7  b7  0 v01")
        self.lines.append("xvb8  b8  0 v01")
        self.lines.append("xvb9  b9  0 v01")
        self.lines.append("xvb10 b10 0 v01")
        self.lines.append("xvb11 b11 0 v01")
        self.lines.append("xvb12 b12 0 v01")
        self.lines.append("xvb13 b13 0 v01")
        self.lines.append("xvb14 b14 0 v01")
        self.lines.append("xvb15 b15 0 v01")
        self.lines.append("")

    def add_control_block(self) -> None:

        self.lines.append(".control")

        self.lines.append("  * load osdi files")
        for osdi_file in self.osdi_files:
            self.lines.append(f"  pre_osdi {osdi_file}")


        self.lines.append("")
        self.lines.append("  *save only")
        self.lines.append("  save v(a0) v(a1) v(a2)  v(a3)  v(a4)  v(a5)  v(a6)  v(a7)")
        self.lines.append("  save v(a8) v(a9) v(a10) v(a11) v(a12) v(a13) v(a14) v(a15)")

        self.lines.append("  save v(b0) v(b1) v(b2)  v(b3)  v(b4)  v(b5)  v(b6)  v(b7)")
        self.lines.append("  save v(b8) v(b9) v(b10) v(b11) v(b12) v(b13) v(b14) v(b15)")

        self.lines.append("  save v(p0)  v(p1)  v(p2)  v(p3)  v(p4)  v(p5)  v(p6)  v(p7)")
        self.lines.append("  save v(p8)  v(p9)  v(p10) v(p11) v(p12) v(p13) v(p14) v(p15)")
        self.lines.append("  save v(p16) v(p17) v(p18) v(p19) v(p20) v(p21) v(p22) v(p23)")
        self.lines.append("  save v(p24) v(p25) v(p26) v(p27) v(p28) v(p29) v(p30) v(p31)")
        self.lines.append("")

        self.lines.append(f"  tran 2p {self.tran_stop}n")
        self.lines.append("")
        self.lines.append("  * print performance and resource usage")
        self.lines.append("  rusage all")
        self.lines.append("")

        if self.wrdata:
            self.lines.append( "  * write output to file")
            self.lines.append( "  set wr_vecnames")
            self.lines.append( "  set wr_singlescale")
            self.lines.append(f"  wrdata check/{self.net_name}.sp.out")
            self.lines.append(  "+    v(a0) v(a1) v(a2) v(a3) v(a4) v(a5) v(a6) v(a7)")
            self.lines.append(  "+    v(a8) v(a9) v(a10) v(a11) v(a12) v(a13) v(a14) v(a15)")
            self.lines.append(  "+    v(b0) v(b1) v(b2) v(b3) v(b4) v(b5) v(b6) v(b7)")
            self.lines.append(  "+    v(b8) v(b9) v(b10) v(b11) v(b12) v(b13) v(b14) v(b15)")
            self.lines.append(  "+    v(p0) v(p1) v(p2) v(p3) v(p4) v(p5) v(p6) v(p7)")
            self.lines.append(  "+    v(p8) v(p9) v(p10) v(p11) v(p12) v(p13) v(p14) v(p15)")
            self.lines.append(  "+    v(p16) v(p17) v(p18) v(p19) v(p20) v(p21) v(p22) v(p23)")
            self.lines.append(  "+    v(p24) v(p25) v(p26) v(p27) v(p28) v(p29) v(p30) v(p31)")

        self.lines.append("  * clean exit after simulation")
        self.lines.append("  set noaskquit")
        self.lines.append("  quit")

        self.lines.append(".endc")

    def generate_netlist(self):
        # Fixed netlist name
        return super().generate_netlist("tb_moslv_c6288_tt")


if __name__ == "__main__":

    gen = C6288Generator(wrdata=True)
    for model_type in [ModelType.GENERIC, ModelType.PARAMSET]:
        gen.set_model_type(model_type)
        netlist_filename = gen.generate_netlist()





