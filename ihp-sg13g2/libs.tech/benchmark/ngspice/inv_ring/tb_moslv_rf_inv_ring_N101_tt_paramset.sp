* CMOS ring oscillator with 101 stages

.include "../models/sg13g2_moslv_rf_mod_osdi.lib"

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
xu51 51 52 vdd 0 inverter
xu52 52 53 vdd 0 inverter
xu53 53 54 vdd 0 inverter
xu54 54 55 vdd 0 inverter
xu55 55 56 vdd 0 inverter
xu56 56 57 vdd 0 inverter
xu57 57 58 vdd 0 inverter
xu58 58 59 vdd 0 inverter
xu59 59 60 vdd 0 inverter
xu60 60 61 vdd 0 inverter
xu61 61 62 vdd 0 inverter
xu62 62 63 vdd 0 inverter
xu63 63 64 vdd 0 inverter
xu64 64 65 vdd 0 inverter
xu65 65 66 vdd 0 inverter
xu66 66 67 vdd 0 inverter
xu67 67 68 vdd 0 inverter
xu68 68 69 vdd 0 inverter
xu69 69 70 vdd 0 inverter
xu70 70 71 vdd 0 inverter
xu71 71 72 vdd 0 inverter
xu72 72 73 vdd 0 inverter
xu73 73 74 vdd 0 inverter
xu74 74 75 vdd 0 inverter
xu75 75 76 vdd 0 inverter
xu76 76 77 vdd 0 inverter
xu77 77 78 vdd 0 inverter
xu78 78 79 vdd 0 inverter
xu79 79 80 vdd 0 inverter
xu80 80 81 vdd 0 inverter
xu81 81 82 vdd 0 inverter
xu82 82 83 vdd 0 inverter
xu83 83 84 vdd 0 inverter
xu84 84 85 vdd 0 inverter
xu85 85 86 vdd 0 inverter
xu86 86 87 vdd 0 inverter
xu87 87 88 vdd 0 inverter
xu88 88 89 vdd 0 inverter
xu89 89 90 vdd 0 inverter
xu90 90 91 vdd 0 inverter
xu91 91 92 vdd 0 inverter
xu92 92 93 vdd 0 inverter
xu93 93 94 vdd 0 inverter
xu94 94 95 vdd 0 inverter
xu95 95 96 vdd 0 inverter
xu96 96 97 vdd 0 inverter
xu97 97 98 vdd 0 inverter
xu98 98 99 vdd 0 inverter
xu99 99 100 vdd 0 inverter
xu100 100 101 vdd 0 inverter
xu101 101 1 vdd 0 inverter

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
.ic v(51)=0.0 v(52)=0.0 v(53)=0.0 v(54)=0.0 v(55)=0.0
.ic v(56)=0.0 v(57)=0.0 v(58)=0.0 v(59)=0.0 v(60)=0.0
.ic v(61)=0.0 v(62)=0.0 v(63)=0.0 v(64)=0.0 v(65)=0.0
.ic v(66)=0.0 v(67)=0.0 v(68)=0.0 v(69)=0.0 v(70)=0.0
.ic v(71)=0.0 v(72)=0.0 v(73)=0.0 v(74)=0.0 v(75)=0.0
.ic v(76)=0.0 v(77)=0.0 v(78)=0.0 v(79)=0.0 v(80)=0.0
.ic v(81)=0.0 v(82)=0.0 v(83)=0.0 v(84)=0.0 v(85)=0.0
.ic v(86)=0.0 v(87)=0.0 v(88)=0.0 v(89)=0.0 v(90)=0.0
.ic v(91)=0.0 v(92)=0.0 v(93)=0.0 v(94)=0.0 v(95)=0.0
.ic v(96)=0.0 v(97)=0.0 v(98)=0.0 v(99)=0.0 v(100)=0.0
.ic v(101)=0.0

.control
  set num_threads = 1

  * load osdi files
  pre_osdi ../../osdi/sg13g2_moslv_rf.osdi

  * save only so that storage does not scale with chain size
  save v(1)

  tran 3.1672736731526385e-10 3.1672736731526385e-07 0 3.1672736731526385e-10 uic

  * print performance and resource usage
  rusage all

  * write output to file
  set wr_vecnames
  set wr_singlescale
  wrdata check/tb_moslv_rf_inv_ring_N101_tt_paramset.sp.out v(1)
  * clean exit after simulation
  set noaskquit
  quit
.endc

.end