EESchema Schematic File Version 1
LIBS:power,./myparts,device,conn,linear,regul,74xx,cmos4000,adc-dac,memory,xilinx,special,microcontrollers,dsp,microchip,analog_switches,motorola,texas,intel,audio,interface,digital-audio,philips,display,cypress,siliconi,contrib,valves,./receiver.cache
EELAYER 23  0
EELAYER END
$Descr A 11000 8500
Sheet 3 5
Title "pp2pp @ STAR: Trigger Receiver board - serializer"
Date "23 jul 2007"
Rev "2.0"
Comp "BNL & ITEP"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text Notes 1500 4700 0    60   ~
Test modes switch
Connection ~ 1500 4300
Wire Wire Line
	1600 4300 1500 4300
Wire Wire Line
	2400 4400 3000 4400
Wire Wire Line
	3000 3900 2500 3900
Wire Wire Line
	3000 3600 2500 3600
Wire Wire Line
	3000 3400 2500 3400
Wire Wire Line
	3000 3200 2500 3200
Wire Wire Line
	3000 3000 2500 3000
Wire Wire Line
	3000 2800 2500 2800
Wire Wire Line
	3000 2600 2500 2600
Wire Wire Line
	3000 2400 2500 2400
Wire Wire Line
	3000 2200 2500 2200
Wire Wire Line
	3000 1900 2500 1900
Connection ~ 5000 4500
Wire Wire Line
	5000 4600 5000 3500
Wire Wire Line
	4900 2600 5400 2600
Wire Bus Line
	6150 700  5400 700 
Wire Bus Line
	5400 700  5400 2200
Wire Wire Line
	4900 2200 5300 2200
Wire Wire Line
	4900 2000 5300 2000
Wire Wire Line
	4900 1800 5300 1800
Wire Wire Line
	4900 1600 5300 1600
Wire Wire Line
	4900 1400 5300 1400
Wire Wire Line
	4900 1200 5300 1200
Wire Wire Line
	4900 1000 5300 1000
Wire Wire Line
	4900 800  5300 800 
Connection ~ 5000 3200
Wire Wire Line
	4900 3200 5000 3200
Connection ~ 5000 3000
Wire Wire Line
	4900 3000 5000 3000
Connection ~ 5000 4400
Wire Wire Line
	4900 4400 5000 4400
Connection ~ 5000 4100
Wire Wire Line
	4900 4100 5000 4100
Connection ~ 5000 3900
Wire Wire Line
	4900 3900 5000 3900
Connection ~ 5000 3700
Wire Wire Line
	4900 3700 5000 3700
Wire Wire Line
	5000 3500 4900 3500
Wire Wire Line
	5000 4500 4900 4500
Wire Wire Line
	2900 1600 2900 1700
Wire Wire Line
	2900 1700 3000 1700
Wire Wire Line
	3000 1200 2250 1200
Wire Wire Line
	2250 900  3000 900 
Wire Wire Line
	2250 800  3000 800 
Wire Wire Line
	3000 1100 2250 1100
Wire Wire Line
	3000 1400 2700 1400
Wire Wire Line
	2700 1400 2700 1350
Wire Wire Line
	2700 1350 2250 1350
Wire Wire Line
	3000 1600 1000 1600
Wire Wire Line
	1000 1600 1000 1350
Wire Wire Line
	1000 1350 1150 1350
Connection ~ 2900 1600
Wire Wire Line
	4900 3600 5000 3600
Connection ~ 5000 3600
Wire Wire Line
	4900 3800 5000 3800
Connection ~ 5000 3800
Wire Wire Line
	4900 4000 5000 4000
Connection ~ 5000 4000
Wire Wire Line
	4900 4300 5000 4300
Connection ~ 5000 4300
Wire Wire Line
	4900 3300 5000 3300
Wire Wire Line
	5000 2900 4900 2900
Wire Wire Line
	4900 3100 5000 3100
Connection ~ 5000 3100
Wire Wire Line
	5000 3300 5000 2850
Connection ~ 5000 2900
Wire Wire Line
	4900 900  5300 900 
Wire Wire Line
	4900 1100 5300 1100
Wire Wire Line
	4900 1300 5300 1300
Wire Wire Line
	4900 1500 5300 1500
Wire Wire Line
	4900 1700 5300 1700
Wire Wire Line
	4900 1900 5300 1900
Wire Wire Line
	4900 2100 5300 2100
Wire Wire Line
	4900 2300 5300 2300
Wire Wire Line
	4900 2500 5400 2500
Wire Wire Line
	4900 2700 5400 2700
Wire Wire Line
	1000 800  1150 800 
Wire Wire Line
	3000 2100 2500 2100
Wire Wire Line
	3000 2300 2500 2300
Wire Wire Line
	3000 2500 2500 2500
Wire Wire Line
	3000 2700 2500 2700
Wire Wire Line
	3000 2900 2500 2900
Wire Wire Line
	3000 3100 2500 3100
Wire Wire Line
	3000 3300 2500 3300
Wire Wire Line
	3000 3500 2500 3500
Wire Wire Line
	3000 3800 2500 3800
Wire Wire Line
	3000 4100 2500 4100
Wire Bus Line
	2400 2200 2400 3700
Wire Bus Line
	2400 3700 1500 3700
Wire Wire Line
	2400 4300 3000 4300
Wire Wire Line
	3000 4200 1500 4200
Wire Wire Line
	1500 4200 1500 4400
Wire Wire Line
	1500 4400 1600 4400
Connection ~ 1850 4200
$Comp
L CONN_2X2 P6
U 1 1 46A3F7D4
P 2000 4350
F 0 "P6" H 2000 4150 50  0000 C C
F 1 "CONN_2X2" H 2010 4220 40  0000 C C
	1    2000 4350
	1    0    0    -1  
$EndComp
$Comp
L +2.5V #PWR5
U 1 1 46A3F748
P 1850 4200
F 0 "#PWR5" H 1850 4150 20  0001 C C
F 1 "+2.5V" H 1850 4300 30  0000 C C
	1    1850 4200
	1    0    0    -1  
$EndComp
Text GLabel 2500 4100 0    60   Input
ENABLE
Text GLabel 2500 3900 0    60   Input
TX_ERR
Text GLabel 2500 3800 0    60   Input
TX_EN
Text Label 2550 3600 0    60   ~
TXD15
Text Label 2550 3500 0    60   ~
TXD14
Text Label 2550 3400 0    60   ~
TXD13
Text Label 2550 3200 0    60   ~
TXD11
Text Label 2550 3300 0    60   ~
TXD12
Text Label 2550 3100 0    60   ~
TXD10
Text Label 2550 3000 0    60   ~
TXD9
Text Label 2550 2900 0    60   ~
TXD8
Text Label 2550 2800 0    60   ~
TXD7
Text Label 2550 2700 0    60   ~
TXD6
Text Label 2550 2600 0    60   ~
TXD5
Text Label 2550 2500 0    60   ~
TXD4
Text Label 2550 2400 0    60   ~
TXD3
Text Label 2550 2300 0    60   ~
TXD2
Text Label 2550 2200 0    60   ~
TXD1
Text Label 2550 2100 0    60   ~
TXD0
Text Label 1600 3700 0    60   ~
TXD[0..15]
Text GLabel 1500 3700 0    60   Input
TXD[0..15]
Entry Wire Line
	2400 3700 2500 3600
Entry Wire Line
	2400 3600 2500 3500
Entry Wire Line
	2400 3500 2500 3400
Entry Wire Line
	2400 3400 2500 3300
Entry Wire Line
	2400 3300 2500 3200
Entry Wire Line
	2400 3200 2500 3100
Entry Wire Line
	2400 3100 2500 3000
Entry Wire Line
	2400 3000 2500 2900
Entry Wire Line
	2400 2900 2500 2800
Entry Wire Line
	2400 2800 2500 2700
Entry Wire Line
	2400 2700 2500 2600
Entry Wire Line
	2400 2600 2500 2500
Entry Wire Line
	2400 2500 2500 2400
Entry Wire Line
	2400 2400 2500 2300
Entry Wire Line
	2400 2300 2500 2200
Entry Wire Line
	2400 2200 2500 2100
Text GLabel 2500 1900 0    60   Input
CLKIN
Text GLabel 1000 800  0    60   Input
DISABLE
Text GLabel 5400 2700 2    60   Output
VALID
Text GLabel 5400 2600 2    60   Output
RERR
Text GLabel 5400 2500 2    60   Output
CLKOUT
$Comp
L GND #PWR30
U 1 1 46A38C6E
P 5000 4600
F 0 "#PWR30" H 5000 4600 30  0001 C C
F 1 "GND" H 5000 4530 30  0001 C C
	1    5000 4600
	1    0    0    -1  
$EndComp
Text Label 5450 700  0    60   ~
RXD[0..15]
Text Label 4950 2300 0    60   ~
RXD15
Text Label 4950 2200 0    60   ~
RXD14
Text Label 4950 2100 0    60   ~
RXD13
Text Label 4950 2000 0    60   ~
RXD12
Text Label 4950 1900 0    60   ~
RXD11
Text Label 4950 1800 0    60   ~
RXD10
Text Label 4950 1700 0    60   ~
RXD9
Text Label 4950 1600 0    60   ~
RXD8
Text Label 4950 1500 0    60   ~
RXD7
Text Label 4950 1400 0    60   ~
RXD6
Text Label 4950 1300 0    60   ~
RXD5
Text Label 4950 1200 0    60   ~
RXD4
Text Label 4950 1100 0    60   ~
RXD3
Text Label 4950 1000 0    60   ~
RXD2
Text Label 4950 900  0    60   ~
RXD1
Text Label 4950 800  0    60   ~
RXD0
Text GLabel 6150 700  2    60   Output
RXD[0..15]
Entry Wire Line
	5300 2300 5400 2200
Entry Wire Line
	5300 2200 5400 2100
Entry Wire Line
	5300 2100 5400 2000
Entry Wire Line
	5300 2000 5400 1900
Entry Wire Line
	5300 1900 5400 1800
Entry Wire Line
	5300 1800 5400 1700
Entry Wire Line
	5300 1700 5400 1600
Entry Wire Line
	5300 1600 5400 1500
Entry Wire Line
	5300 1500 5400 1400
Entry Wire Line
	5300 1400 5400 1300
Entry Wire Line
	5300 1300 5400 1200
Entry Wire Line
	5300 1200 5400 1100
Entry Wire Line
	5300 1100 5400 1000
Entry Wire Line
	5300 1000 5400 900 
Entry Wire Line
	5300 900  5400 800 
Entry Wire Line
	5300 800  5400 700 
$Comp
L +2.5V #PWR4
U 1 1 46A38B0C
P 5000 2850
F 0 "#PWR4" H 5000 2800 20  0001 C C
F 1 "+2.5V" H 5000 2950 30  0000 C C
	1    5000 2850
	1    0    0    -1  
$EndComp
$Comp
L TLK1501 U12
U 1 1 46A38AB2
P 3300 650
F 0 "U12" H 3400 650 60  0000 C C
F 1 "TLK1501" H 4000 -3300 60  0000 C C
	1    3300 650 
	1    0    0    -1  
$EndComp
$Sheet
S 1150 750  1100 650 
F0 "Laser" 60
F1 "rc_laser.sch" 60
F2 "RREF" O R 2250 1350 60 
F3 "RXD-" O R 2250 900 60 
F4 "RXD+" O R 2250 800 60 
F5 "DISABLE" I L 1150 800 60 
F6 "VCCA" O L 1150 1350 60 
F7 "TXD-" I R 2250 1200 60 
F8 "TXD+" I R 2250 1100 60 
$EndSheet
$EndSCHEMATC
