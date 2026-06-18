* CMOS ring oscillator with 51 stages

.lib "../models/cornerMOSlv.lib" mos_tt

.options noacct
.options nomod
.options nopage
.options klu
.options reltol=1e-4


* Inverter subcircuit
.subckt inverter in out vdd gnd
Xpm out in vdd vdd sg13_lv_pmos w=1.0u l=0.2u
Xmn out in gnd gnd sg13_lv_nmos w=0.5u l=0.2u
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
xu11 11 12 vdd 0 inverter
xu12 12 13 vdd 0 inverter
xu13 13 14 vdd 0 inverter
xu14 14 15 vdd 0 inverter
xu15 15 16 vdd 0 inverter
xu16 16 17 vdd 0 inverter
xu17 17 18 vdd 0 inverter
xu18 18 19 vdd 0 inverter
xu19 19 20 vdd 0 inverter
xu20 20 21 vdd 0 inverter
xu21 21 22 vdd 0 inverter
xu22 22 23 vdd 0 inverter
xu23 23 24 vdd 0 inverter
xu24 24 25 vdd 0 inverter
xu25 25 26 vdd 0 inverter
xu26 26 27 vdd 0 inverter
xu27 27 28 vdd 0 inverter
xu28 28 29 vdd 0 inverter
xu29 29 30 vdd 0 inverter
xu30 30 31 vdd 0 inverter
xu31 31 32 vdd 0 inverter
xu32 32 33 vdd 0 inverter
xu33 33 34 vdd 0 inverter
xu34 34 35 vdd 0 inverter
xu35 35 36 vdd 0 inverter
xu36 36 37 vdd 0 inverter
xu37 37 38 vdd 0 inverter
xu38 38 39 vdd 0 inverter
xu39 39 40 vdd 0 inverter
xu40 40 41 vdd 0 inverter
xu41 41 42 vdd 0 inverter
xu42 42 43 vdd 0 inverter
xu43 43 44 vdd 0 inverter
xu44 44 45 vdd 0 inverter
xu45 45 46 vdd 0 inverter
xu46 46 47 vdd 0 inverter
xu47 47 48 vdd 0 inverter
xu48 48 49 vdd 0 inverter
xu49 49 50 vdd 0 inverter
xu50 50 51 vdd 0 inverter
xu51 51 1 vdd 0 inverter

* Supply voltage
vdd vdd 0 1.2
* Load capacitance
Cdecap vdd 0 1p

.ic v(1)=0.0 v(2)=0.0 v(3)=0.0 v(4)=0.0 v(5)=0.0
.ic v(6)=0.0 v(7)=0.0 v(8)=0.0 v(9)=0.0 v(10)=0.0
.ic v(11)=0.0 v(12)=0.0 v(13)=0.0 v(14)=0.0 v(15)=0.0
.ic v(16)=0.0 v(17)=0.0 v(18)=0.0 v(19)=0.0 v(20)=0.0
.ic v(21)=0.0 v(22)=0.0 v(23)=0.0 v(24)=0.0 v(25)=0.0
.ic v(26)=0.0 v(27)=0.0 v(28)=0.0 v(29)=0.0 v(30)=0.0
.ic v(31)=0.0 v(32)=0.0 v(33)=0.0 v(34)=0.0 v(35)=0.0
.ic v(36)=0.0 v(37)=0.0 v(38)=0.0 v(39)=0.0 v(40)=0.0
.ic v(41)=0.0 v(42)=0.0 v(43)=0.0 v(44)=0.0 v(45)=0.0
.ic v(46)=0.0 v(47)=0.0 v(48)=0.0 v(49)=0.0 v(50)=0.0
.ic v(51)=0.0

.control
  set num_threads = 1

  * load osdi files
  pre_osdi ../../osdi/psp103.osdi

  * save only so that storage does not scale with chain size
  save v(1)

  tran 1.599316409215689e-10 1.5993164092156888e-07 0 1.599316409215689e-10 uic

  * print performance and resource usage
  rusage all

  * write output to file
  set wr_vecnames
  set wr_singlescale
  wrdata check/tb_moslv_inv_ring_N51_tt_generic.sp.out v(1)
  * clean exit after simulation
  set noaskquit
  quit
.endc

.end