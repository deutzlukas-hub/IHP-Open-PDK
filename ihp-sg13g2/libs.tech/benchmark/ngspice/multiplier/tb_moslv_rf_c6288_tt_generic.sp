* C6288 16x16 multiplier* ISCAS-85 benchmark circuit

.lib "../models/cornerMOSlv_rf.lib" mos_tt
.include "multiplier.inc"

.options noacct
.options nomod
.options nopage
.options klu

vdd vdd 0 1.2
vss vss 0 0

* instantiate the multiplier
x1  a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11 a12 a13 a14 a15
+   b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 b14 b15
+   p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15
+   p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31
+ c6288

* each input receives same pulse waveform 
.subckt v01 out ref
  vdrv int 0 pulse(0 1.2 0.1n 0.1n 0.1n 100n)
  rdrv int out r=1
.ends

xa0  a0  0 v01
xa1  a1  0 v01
xa2  a2  0 v01
xa3  a3  0 v01
xa4  a4  0 v01
xa5  a5  0 v01
xa6  a6  0 v01
xa7  a7  0 v01
xa8  a8  0 v01
xa9  a9  0 v01
xa10 a10 0 v01
xa11 a11 0 v01
xa12 a12 0 v01
xa13 a13 0 v01
xa14 a14 0 v01
xa15 a15 0 v01

xvb0  b0  0 v01
xvb1  b1  0 v01
xvb2  b2  0 v01
xvb3  b3  0 v01
xvb4  b4  0 v01
xvb5  b5  0 v01
xvb6  b6  0 v01
xvb7  b7  0 v01
xvb8  b8  0 v01
xvb9  b9  0 v01
xvb10 b10 0 v01
xvb11 b11 0 v01
xvb12 b12 0 v01
xvb13 b13 0 v01
xvb14 b14 0 v01
xvb15 b15 0 v01

.control
  * load osdi files
  pre_osdi ../../osdi/psp103_nqs.osdi

  *save only
  save v(a0) v(a1) v(a2)  v(a3)  v(a4)  v(a5)  v(a6)  v(a7)
  save v(a8) v(a9) v(a10) v(a11) v(a12) v(a13) v(a14) v(a15)
  save v(b0) v(b1) v(b2)  v(b3)  v(b4)  v(b5)  v(b6)  v(b7)
  save v(b8) v(b9) v(b10) v(b11) v(b12) v(b13) v(b14) v(b15)
  save v(p0)  v(p1)  v(p2)  v(p3)  v(p4)  v(p5)  v(p6)  v(p7)
  save v(p8)  v(p9)  v(p10) v(p11) v(p12) v(p13) v(p14) v(p15)
  save v(p16) v(p17) v(p18) v(p19) v(p20) v(p21) v(p22) v(p23)
  save v(p24) v(p25) v(p26) v(p27) v(p28) v(p29) v(p30) v(p31)

  tran 2p 1n

  * print performance and resource usage
  rusage all

  * write output to file
  set wr_vecnames
  set wr_singlescale
  wrdata check/tb_moslv_c6288_tt_generic.sp.out
+    v(a0) v(a1) v(a2) v(a3) v(a4) v(a5) v(a6) v(a7)
+    v(a8) v(a9) v(a10) v(a11) v(a12) v(a13) v(a14) v(a15)
+    v(b0) v(b1) v(b2) v(b3) v(b4) v(b5) v(b6) v(b7)
+    v(b8) v(b9) v(b10) v(b11) v(b12) v(b13) v(b14) v(b15)
+    v(p0) v(p1) v(p2) v(p3) v(p4) v(p5) v(p6) v(p7)
+    v(p8) v(p9) v(p10) v(p11) v(p12) v(p13) v(p14) v(p15)
+    v(p16) v(p17) v(p18) v(p19) v(p20) v(p21) v(p22) v(p23)
+    v(p24) v(p25) v(p26) v(p27) v(p28) v(p29) v(p30) v(p31)
  * clean exit after simulation
  set noaskquit
  quit
.endc

.end
