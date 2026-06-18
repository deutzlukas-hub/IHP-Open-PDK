* CMOS ring oscillator with 11 stages

.model sg13_lv_nmos sg13g2_lv_nmos_psp_rf_model
.model sg13_lv_pmos sg13g2_lv_pmos_psp_rf_model

.options noacct
.options nomod
.options nopage
.options klu
.options reltol=1e-4


* Inverter subcircuit
.subckt inverter in out vdd gnd
Npm out in vdd vdd sg13_lv_pmos
Nmn out in gnd gnd sg13_lv_nmos
.ends

i0 0 1 dc 0 pulse 0 1e-05 0.1n 0.1n 0.1n 0.3n

* Inverter ring
xu1 1 2 vdd 0 inverter
xu2 2 3 vdd 0 inverter
xu3 3 4 vdd 0 inverter
xu4 4 5 vdd 0 inverter
xu5 5 6 vdd 0 inverter
xu6 6 7 vdd 0 inverter
xu7 7 8 vdd 0 inverter
xu8 8 9 vdd 0 inverter
xu9 9 10 vdd 0 inverter
xu10 10 11 vdd 0 inverter
xu11 11 1 vdd 0 inverter

* Supply voltage
vdd vdd 0 1.2
* Load capacitance
Cdecap vdd 0 1p

.ic v(1)=0.0 v(2)=0.0 v(3)=0.0 v(4)=0.0 v(5)=0.0
.ic v(6)=0.0 v(7)=0.0 v(8)=0.0 v(9)=0.0 v(10)=0.0
.ic v(11)=0.0

.control
  set num_threads = 1

  * load osdi files
  pre_osdi ../../osdi/sg13g2_moslv_rf_tailored.osdi

  * save only so that storage does not scale with chain size
  save v(1)

  tran 3.44950598066129e-11 3.4495059806612893e-08 0 3.44950598066129e-11 uic

  * print performance and resource usage
  rusage all

  * write output to file
  set wr_vecnames
  set wr_singlescale
  wrdata check/tb_moslv_rf_inv_ring_N11_tt_tailored.sp.out v(1)
  * clean exit after simulation
  set noaskquit
  quit
.endc

.end