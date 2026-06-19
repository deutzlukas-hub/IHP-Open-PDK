* CMOS inverter chain

.lib "../models/cornerMOSlv_rf.lib" mos_tt

.options noacct
.options nomod
.options nopage
.options klu
.options reltol=1e-4

VDD vdd 0 1.2
VIN in 0 PULSE(0 1.2 10n 100p 100p 10n 20n)

* Inverter subcircuit
.subckt inv in out vdd gnd
X1 out in vdd vdd sg13_lv_pmos w=1e-06 l=2e-07
X2 out in gnd gnd sg13_lv_nmos w=5e-07 l=2e-07
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
X10 n9 n10 vdd 0 inv
X11 n10 n11 vdd 0 inv
X12 n11 n12 vdd 0 inv
X13 n12 n13 vdd 0 inv
X14 n13 n14 vdd 0 inv
X15 n14 n15 vdd 0 inv
X16 n15 n16 vdd 0 inv
X17 n16 n17 vdd 0 inv
X18 n17 n18 vdd 0 inv
X19 n18 n19 vdd 0 inv
X20 n19 n20 vdd 0 inv
X21 n20 n21 vdd 0 inv
X22 n21 n22 vdd 0 inv
X23 n22 n23 vdd 0 inv
X24 n23 n24 vdd 0 inv
X25 n24 n25 vdd 0 inv
X26 n25 n26 vdd 0 inv
X27 n26 n27 vdd 0 inv
X28 n27 n28 vdd 0 inv
X29 n28 n29 vdd 0 inv
X30 n29 n30 vdd 0 inv
X31 n30 n31 vdd 0 inv
X32 n31 n32 vdd 0 inv
X33 n32 n33 vdd 0 inv
X34 n33 n34 vdd 0 inv
X35 n34 n35 vdd 0 inv
X36 n35 n36 vdd 0 inv
X37 n36 n37 vdd 0 inv
X38 n37 n38 vdd 0 inv
X39 n38 n39 vdd 0 inv
X40 n39 n40 vdd 0 inv
X41 n40 n41 vdd 0 inv
X42 n41 n42 vdd 0 inv
X43 n42 n43 vdd 0 inv
X44 n43 n44 vdd 0 inv
X45 n44 n45 vdd 0 inv
X46 n45 n46 vdd 0 inv
X47 n46 n47 vdd 0 inv
X48 n47 n48 vdd 0 inv
X49 n48 n49 vdd 0 inv
X50 n49 out vdd 0 inv

* Load capacitance
CL out 0 1e-14

.control
  set num_threads = 2

  * load osdi files
  pre_osdi ../../osdi/psp103_nqs.osdi

  * save only so that storage does not scale with chain size
  save v(in) v(out)

  tran 0.1n 110n 0 0.1n

  * print performance and resource usage
  rusage all

  * write output to file
  set wr_vecnames
  set wr_singlescale
  wrdata check/tb_moslv_rf_inv_chain_N50_tt_generic.sp.out v(in) v(out)
  * clean exit after simulation
  set noaskquit
  quit
.endc

.end