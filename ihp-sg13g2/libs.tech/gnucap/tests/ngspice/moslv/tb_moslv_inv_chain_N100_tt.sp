* CMOS inverter chain with 100 stages
* Corner: tt

.LIB "cornerMOSlv.lib" mos_tt

.option reltol=1e-4

VDD vdd 0 1.2
VIN in 0 PWL(0 0 10n 0 11n 1.2 100.0n 1.2)

* Inverter subcircuit
.subckt inv in out vdd gnd
X1 out in vdd vdd sg13_lv_pmos w=2.8e-07 l=3.4e-07 rfmode=0
X2 out in gnd gnd sg13_lv_nmos w=3.5e-07 l=3.4e-07 rfmode=0
.ends

* Inverter chain instances
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
X50 n49 n50 vdd 0 inv
X51 n50 n51 vdd 0 inv
X52 n51 n52 vdd 0 inv
X53 n52 n53 vdd 0 inv
X54 n53 n54 vdd 0 inv
X55 n54 n55 vdd 0 inv
X56 n55 n56 vdd 0 inv
X57 n56 n57 vdd 0 inv
X58 n57 n58 vdd 0 inv
X59 n58 n59 vdd 0 inv
X60 n59 n60 vdd 0 inv
X61 n60 n61 vdd 0 inv
X62 n61 n62 vdd 0 inv
X63 n62 n63 vdd 0 inv
X64 n63 n64 vdd 0 inv
X65 n64 n65 vdd 0 inv
X66 n65 n66 vdd 0 inv
X67 n66 n67 vdd 0 inv
X68 n67 n68 vdd 0 inv
X69 n68 n69 vdd 0 inv
X70 n69 n70 vdd 0 inv
X71 n70 n71 vdd 0 inv
X72 n71 n72 vdd 0 inv
X73 n72 n73 vdd 0 inv
X74 n73 n74 vdd 0 inv
X75 n74 n75 vdd 0 inv
X76 n75 n76 vdd 0 inv
X77 n76 n77 vdd 0 inv
X78 n77 n78 vdd 0 inv
X79 n78 n79 vdd 0 inv
X80 n79 n80 vdd 0 inv
X81 n80 n81 vdd 0 inv
X82 n81 n82 vdd 0 inv
X83 n82 n83 vdd 0 inv
X84 n83 n84 vdd 0 inv
X85 n84 n85 vdd 0 inv
X86 n85 n86 vdd 0 inv
X87 n86 n87 vdd 0 inv
X88 n87 n88 vdd 0 inv
X89 n88 n89 vdd 0 inv
X90 n89 n90 vdd 0 inv
X91 n90 n91 vdd 0 inv
X92 n91 n92 vdd 0 inv
X93 n92 n93 vdd 0 inv
X94 n93 n94 vdd 0 inv
X95 n94 n95 vdd 0 inv
X96 n95 n96 vdd 0 inv
X97 n96 n97 vdd 0 inv
X98 n97 n98 vdd 0 inv
X99 n98 n99 vdd 0 inv
X100 n99 out vdd 0 inv

* Load capacitance
CL out 0 1e-14

.control
set wr_vecnames
set wr_singlescale
tran 1e-10 1e-07
wrdata check/tb_moslv_inv_chain_N100_tt.sp.out v(in) v(out) i(VDD)
.endc
.end
