* CMOS inverter chain

.model sg13_lv_nmos sg13g2_lv_nmos_psp_rf_model
.model sg13_lv_pmos sg13g2_lv_pmos_psp_rf_model

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
X100 n99 n100 vdd 0 inv
X101 n100 n101 vdd 0 inv
X102 n101 n102 vdd 0 inv
X103 n102 n103 vdd 0 inv
X104 n103 n104 vdd 0 inv
X105 n104 n105 vdd 0 inv
X106 n105 n106 vdd 0 inv
X107 n106 n107 vdd 0 inv
X108 n107 n108 vdd 0 inv
X109 n108 n109 vdd 0 inv
X110 n109 n110 vdd 0 inv
X111 n110 n111 vdd 0 inv
X112 n111 n112 vdd 0 inv
X113 n112 n113 vdd 0 inv
X114 n113 n114 vdd 0 inv
X115 n114 n115 vdd 0 inv
X116 n115 n116 vdd 0 inv
X117 n116 n117 vdd 0 inv
X118 n117 n118 vdd 0 inv
X119 n118 n119 vdd 0 inv
X120 n119 n120 vdd 0 inv
X121 n120 n121 vdd 0 inv
X122 n121 n122 vdd 0 inv
X123 n122 n123 vdd 0 inv
X124 n123 n124 vdd 0 inv
X125 n124 n125 vdd 0 inv
X126 n125 n126 vdd 0 inv
X127 n126 n127 vdd 0 inv
X128 n127 n128 vdd 0 inv
X129 n128 n129 vdd 0 inv
X130 n129 n130 vdd 0 inv
X131 n130 n131 vdd 0 inv
X132 n131 n132 vdd 0 inv
X133 n132 n133 vdd 0 inv
X134 n133 n134 vdd 0 inv
X135 n134 n135 vdd 0 inv
X136 n135 n136 vdd 0 inv
X137 n136 n137 vdd 0 inv
X138 n137 n138 vdd 0 inv
X139 n138 n139 vdd 0 inv
X140 n139 n140 vdd 0 inv
X141 n140 n141 vdd 0 inv
X142 n141 n142 vdd 0 inv
X143 n142 n143 vdd 0 inv
X144 n143 n144 vdd 0 inv
X145 n144 n145 vdd 0 inv
X146 n145 n146 vdd 0 inv
X147 n146 n147 vdd 0 inv
X148 n147 n148 vdd 0 inv
X149 n148 n149 vdd 0 inv
X150 n149 n150 vdd 0 inv
X151 n150 n151 vdd 0 inv
X152 n151 n152 vdd 0 inv
X153 n152 n153 vdd 0 inv
X154 n153 n154 vdd 0 inv
X155 n154 n155 vdd 0 inv
X156 n155 n156 vdd 0 inv
X157 n156 n157 vdd 0 inv
X158 n157 n158 vdd 0 inv
X159 n158 n159 vdd 0 inv
X160 n159 n160 vdd 0 inv
X161 n160 n161 vdd 0 inv
X162 n161 n162 vdd 0 inv
X163 n162 n163 vdd 0 inv
X164 n163 n164 vdd 0 inv
X165 n164 n165 vdd 0 inv
X166 n165 n166 vdd 0 inv
X167 n166 n167 vdd 0 inv
X168 n167 n168 vdd 0 inv
X169 n168 n169 vdd 0 inv
X170 n169 n170 vdd 0 inv
X171 n170 n171 vdd 0 inv
X172 n171 n172 vdd 0 inv
X173 n172 n173 vdd 0 inv
X174 n173 n174 vdd 0 inv
X175 n174 n175 vdd 0 inv
X176 n175 n176 vdd 0 inv
X177 n176 n177 vdd 0 inv
X178 n177 n178 vdd 0 inv
X179 n178 n179 vdd 0 inv
X180 n179 n180 vdd 0 inv
X181 n180 n181 vdd 0 inv
X182 n181 n182 vdd 0 inv
X183 n182 n183 vdd 0 inv
X184 n183 n184 vdd 0 inv
X185 n184 n185 vdd 0 inv
X186 n185 n186 vdd 0 inv
X187 n186 n187 vdd 0 inv
X188 n187 n188 vdd 0 inv
X189 n188 n189 vdd 0 inv
X190 n189 n190 vdd 0 inv
X191 n190 n191 vdd 0 inv
X192 n191 n192 vdd 0 inv
X193 n192 n193 vdd 0 inv
X194 n193 n194 vdd 0 inv
X195 n194 n195 vdd 0 inv
X196 n195 n196 vdd 0 inv
X197 n196 n197 vdd 0 inv
X198 n197 n198 vdd 0 inv
X199 n198 n199 vdd 0 inv
X200 n199 out vdd 0 inv

* Load capacitance
CL out 0 1e-14

.control
  set num_threads = 1
  * load osdi files
  pre_osdi ../../osdi/sg13g2_moslv_rf_tailored.osdi

  * save only so that storage does not scale with chain size
  save v(in) v(out)

  tran 0.1n 110n 0 0.1n

  * print performance and resource usage
  rusage all

  * write output to file
  set wr_vecnames
  set wr_singlescale
  wrdata check/tb_moslv_rf_inv_chain_N200_tt_tailored.sp.out v(in) v(out)
  * clean exit after simulation
  set noaskquit
  quit
.endc

.end