* CMOS inverter chain

.model sg13_lv_nmos sg13g2_lv_nmos_psp_model
.model sg13_lv_pmos sg13g2_lv_pmos_psp_model

.options noacct
.options nomod
.options nopage
.options klu
.options reltol=1e-4

VDD vdd 0 1.2
VIN in 0 PULSE(0 1.2 10n 100p 100p 10n 20n)

* Inverter subcircuit
.subckt inv in out vdd gnd
N1 out in vdd vdd sg13_lv_pmos
N2 out in gnd gnd sg13_lv_nmos
.ends

* Inverter instances
X1 in n1 vdd 0 inv
X2 n1 n2 vdd 0 inv
X3 n2 n3 vdd 0 inv
X4 n3 n4 vdd 0 inv
X5 n4 n5 vdd 0 inv
X6 n5 n6 vdd 0 inv
X7 n6 n7 vdd 0 inv
X8 n7 n8 vdd 0 inv
X9 n8 n9 vdd 0 inv
X10 n9 out vdd 0 inv

* Load capacitance
CL out 0 1e-14

.control
  set num_threads = 1
  * load osdi files
  pre_osdi ../../osdi/sg13g2_moslv_tailored.osdi

  * save only so that storage does not scale with chain size
  save v(in) v(out)

  tran 0.1n 110n 0 0.1n

  * print performance and resource usage
  rusage all

  * write output to file
  set wr_vecnames
  set wr_singlescale
  wrdata check/tb_moslv_inv_chain_N10_tt_tailored.sp.out v(in) v(out)
  * clean exit after simulation
  set noaskquit
  quit
.endc

.end