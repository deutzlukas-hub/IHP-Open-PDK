* CMOS inverter

* bind osdi to spice model
.model sg13_lv_nmos sg13g2_lv_nmos_psp
.model sg13_lv_pmos sg13g2_lv_pmos_psp

.option reltol=1e-4

VDD vdd 0 1.2
VIN in 0 1.2

N1 out in vdd vdd sg13_lv_pmos w=0.28u l=0.34u rfmode=0
N2 out in 0 0 sg13_lv_nmos w=0.35u l=0.34u rfmode=0

.control
pre_osdi sg13g2_moslv_paramset_openvaf_nolocalparam_instance.osdi
set wr_vecnames
set wr_singlescale
dc VIN 0.0 1.2 0.02
wrdata check/tb_moslv_inv_tt.sp.out v(out) i(VDD)
.endc
.end
