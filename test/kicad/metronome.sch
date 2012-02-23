EESchema Schematic File Version 2
LIBS:power,device,conn,linear,regul,74xx,cmos4000,adc-dac,memory,xilinx,special,microcontrollers,dsp,microchip,analog_switches,motorola,texas,intel,audio,interface,digital-audio,philips,display,cypress,siliconi,contrib,valves,./metronome.cache
EELAYER 24  0
EELAYER END
$Descr A4 11700 8267
Sheet 1 1
Title "Tactile Metronome"
Date "12 jul 2009"
Rev "1.0a"
Comp "http://wayneandlayne.com/metronome"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L PWR_FLAG #FLG01
U 1 1 4A5A31A6
P 1950 2550
F 0 "#FLG01" H 1950 2820 30  0001 C C
F 1 "PWR_FLAG" H 1950 2780 30  0000 C C
	1    1950 2550
	1    0    0    -1  
$EndComp
Text Label 7950 1850 0    60   ~
d2en
Text Label 7950 1750 0    60   ~
d3en
Wire Wire Line
	7800 1700 7800 1650
Wire Wire Line
	7800 1650 8200 1650
Wire Wire Line
	8200 1850 7900 1850
Wire Wire Line
	8200 1450 7900 1450
Wire Wire Line
	7850 3850 9600 3850
Wire Wire Line
	7850 3950 8800 3950
Wire Wire Line
	9600 3850 9600 3950
Wire Wire Line
	2150 5600 2450 5600
Wire Wire Line
	7350 5750 7600 5750
Wire Wire Line
	8450 6200 8950 6200
Wire Wire Line
	5750 4350 5250 4350
Wire Wire Line
	3700 3500 5250 3500
Wire Wire Line
	8150 4250 7850 4250
Connection ~ 8700 2650
Wire Wire Line
	8700 2650 8700 3650
Wire Wire Line
	8700 3650 7850 3650
Wire Wire Line
	8900 3150 9050 3150
Wire Wire Line
	7850 2650 9250 2650
Wire Wire Line
	1950 3300 1950 3500
Wire Wire Line
	4350 3500 4350 3550
Wire Wire Line
	2550 2200 2550 2550
Wire Wire Line
	7850 3450 8150 3450
Wire Wire Line
	7850 3550 8150 3550
Wire Wire Line
	9550 5700 9550 6000
Wire Wire Line
	5250 5450 5250 5250
Connection ~ 7900 6050
Wire Wire Line
	7900 5950 7900 6150
Wire Wire Line
	5250 5850 5250 6150
Wire Wire Line
	5250 6150 5100 6150
Connection ~ 2750 6000
Wire Wire Line
	2750 5800 2750 6100
Wire Wire Line
	7850 3050 8150 3050
Wire Wire Line
	7850 2850 8150 2850
Wire Wire Line
	7850 2550 8150 2550
Wire Wire Line
	5100 6750 5300 6750
Connection ~ 4600 3500
Connection ~ 4150 3500
Wire Wire Line
	6500 6700 6350 6700
Wire Wire Line
	6500 6500 6350 6500
Wire Wire Line
	6500 6300 6350 6300
Wire Wire Line
	6500 6200 6350 6200
Wire Wire Line
	6500 6100 6350 6100
Wire Wire Line
	6500 6400 6350 6400
Wire Wire Line
	6500 6600 6350 6600
Wire Wire Line
	3900 6700 3750 6700
Wire Wire Line
	3900 6500 3750 6500
Wire Wire Line
	3900 6300 3750 6300
Wire Wire Line
	3900 6200 3750 6200
Wire Wire Line
	3900 6100 3750 6100
Wire Wire Line
	3900 6400 3750 6400
Wire Wire Line
	3900 6600 3750 6600
Wire Wire Line
	1350 6650 1200 6650
Wire Wire Line
	1350 6450 1200 6450
Wire Wire Line
	1350 6250 1200 6250
Wire Wire Line
	1350 6150 1200 6150
Wire Wire Line
	4150 3500 4150 3150
Wire Wire Line
	4150 2450 4150 2750
Wire Wire Line
	4600 3500 4600 3150
Connection ~ 4350 3500
Wire Wire Line
	1350 6050 1200 6050
Wire Wire Line
	1350 6350 1200 6350
Wire Wire Line
	1350 6550 1200 6550
Connection ~ 4150 2450
Wire Wire Line
	2550 6000 2750 6000
Wire Wire Line
	2750 6100 2550 6100
Wire Wire Line
	7700 6050 7900 6050
Wire Wire Line
	7900 6150 7700 6150
Wire Wire Line
	7700 6750 7950 6750
Wire Wire Line
	2550 6700 2750 6700
Wire Wire Line
	7850 2450 8150 2450
Wire Wire Line
	7850 2750 8150 2750
Wire Wire Line
	7850 2950 8150 2950
Wire Wire Line
	7850 3150 8150 3150
Wire Wire Line
	5100 6050 5250 6050
Connection ~ 5250 6050
Wire Wire Line
	2750 5400 2750 5200
Wire Wire Line
	9550 6200 9550 6500
Wire Wire Line
	7850 3350 8150 3350
Wire Wire Line
	7900 5350 7900 5550
Connection ~ 3800 2450
Wire Wire Line
	9200 4350 9200 4200
Wire Wire Line
	3550 2450 5750 2450
Wire Wire Line
	2550 2550 1950 2550
Wire Wire Line
	1950 2550 1950 2700
Wire Wire Line
	3600 2300 3600 2450
Connection ~ 3600 2450
Wire Wire Line
	4600 2450 4600 2750
Connection ~ 4600 2450
Connection ~ 8900 2650
Wire Wire Line
	8900 3150 8900 3450
Wire Wire Line
	9050 3150 9050 2850
Wire Wire Line
	9050 2850 9250 2850
Wire Wire Line
	8150 4150 7850 4150
Wire Wire Line
	8150 4350 7850 4350
Wire Wire Line
	5250 3500 5250 4350
Wire Wire Line
	8450 5700 8950 5700
Wire Wire Line
	4700 5650 4950 5650
Wire Wire Line
	8100 4050 7850 4050
Wire Wire Line
	8200 1750 7900 1750
Wire Wire Line
	8200 1550 7800 1550
Wire Wire Line
	7800 1550 7800 1500
$Comp
L VCC #PWR02
U 1 1 4A59FC8F
P 7800 1500
F 0 "#PWR02" H 7800 1600 30  0001 C C
F 1 "VCC" H 7800 1600 30  0000 C C
	1    7800 1500
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR03
U 1 1 4A59FC89
P 7800 1700
F 0 "#PWR03" H 7800 1700 30  0001 C C
F 1 "GND" H 7800 1630 30  0001 C C
	1    7800 1700
	1    0    0    -1  
$EndComp
Text Label 7950 1450 0    60   ~
mclr
Text Label 8050 4050 0    60   ~
mclr
$Comp
L CONN_5 P1
U 1 1 4A59FA0E
P 8600 1650
F 0 "P1" V 8550 1650 50  0000 C C
F 1 "ICSP" V 8650 1650 50  0000 C C
	1    8600 1650
	1    0    0    -1  
$EndComp
$Comp
L SW_PUSH SW3
U 1 1 4A57CDCC
P 9250 6200
F 0 "SW3" H 9400 6310 50  0000 C C
F 1 "SW_PUSH" H 9250 6120 50  0000 C C
	1    9250 6200
	1    0    0    -1  
$EndComp
$Comp
L SW_PUSH SW2
U 1 1 4A57CB98
P 9250 5700
F 0 "SW2" H 9400 5810 50  0000 C C
F 1 "SW_PUSH" H 9250 5620 50  0000 C C
	1    9250 5700
	1    0    0    -1  
$EndComp
$Comp
L VCC #PWR04
U 1 1 4A57C95B
P 3600 2300
F 0 "#PWR04" H 3600 2400 30  0001 C C
F 1 "VCC" H 3600 2400 30  0000 C C
	1    3600 2300
	1    0    0    -1  
$EndComp
$Comp
L +BATT #PWR05
U 1 1 4A57C93E
P 2550 2200
F 0 "#PWR05" H 2550 2150 20  0001 C C
F 1 "+BATT" H 2550 2300 30  0000 C C
	1    2550 2200
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR06
U 1 1 4A3D1247
P 1950 3500
F 0 "#PWR06" H 1950 3500 30  0001 C C
F 1 "GND" H 1950 3430 30  0001 C C
	1    1950 3500
	1    0    0    -1  
$EndComp
$Comp
L BATTERY BT1
U 1 1 4A3D1228
P 1950 3000
F 0 "BT1" H 1950 3200 50  0000 C C
F 1 "BATTERY" H 1950 2810 50  0000 C C
F 2 "BATTERY" H 1950 2700 60  0000 C C
	1    1950 3000
	0    1    1    0   
$EndComp
NoConn ~ 3550 2650
$Comp
L GND #PWR07
U 1 1 4A3D1047
P 9200 4350
F 0 "#PWR07" H 9200 4350 30  0001 C C
F 1 "GND" H 9200 4280 30  0001 C C
	1    9200 4350
	1    0    0    -1  
$EndComp
$Comp
L CERAMIC_FILTER F1
U 1 1 4A3D0E78
P 9200 4000
F 0 "F1" H 9250 4150 50  0000 C C
F 1 "CERAMIC_FILTER" H 9250 3900 40  0000 L C
	1    9200 4000
	1    0    0    -1  
$EndComp
$Comp
L DUAL_SWITCH_INV SW1
U 1 1 4A3D0E04
P 3050 2550
F 0 "SW1" H 2850 2700 50  0000 C C
F 1 "DUAL_SWITCH_INV" H 2900 2400 50  0000 C C
	1    3050 2550
	1    0    0    -1  
$EndComp
Text Label 8050 4150 0    60   ~
d1en
Text Label 8050 4250 0    60   ~
d2en
Text Label 8050 4350 0    60   ~
d3en
Text Label 8450 6200 0    60   ~
down_sw
Text Label 8450 5700 0    60   ~
up_sw
Text Label 8050 3450 0    60   ~
up_sw
Text Label 8050 3350 0    60   ~
down_sw
Text Label 8050 3550 0    60   ~
dp
$Comp
L GND #PWR08
U 1 1 4A359DE1
P 9550 6500
F 0 "#PWR08" H 9550 6500 30  0001 C C
F 1 "GND" H 9550 6430 30  0001 C C
	1    9550 6500
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR09
U 1 1 4A359DB4
P 9550 6000
F 0 "#PWR09" H 9550 6000 30  0001 C C
F 1 "GND" H 9550 5930 30  0001 C C
	1    9550 6000
	1    0    0    -1  
$EndComp
$Comp
L VCC #PWR010
U 1 1 4A359D97
P 2750 5200
F 0 "#PWR010" H 2750 5300 30  0001 C C
F 1 "VCC" H 2750 5300 30  0000 C C
	1    2750 5200
	1    0    0    -1  
$EndComp
$Comp
L VCC #PWR011
U 1 1 4A359D94
P 5250 5250
F 0 "#PWR011" H 5250 5350 30  0001 C C
F 1 "VCC" H 5250 5350 30  0000 C C
	1    5250 5250
	1    0    0    -1  
$EndComp
$Comp
L VCC #PWR012
U 1 1 4A359D91
P 7900 5350
F 0 "#PWR012" H 7900 5450 30  0001 C C
F 1 "VCC" H 7900 5450 30  0000 C C
	1    7900 5350
	1    0    0    -1  
$EndComp
Text Label 2150 5600 0    60   ~
d1en
Text Label 4700 5650 0    60   ~
d2en
Text Label 7350 5750 0    60   ~
d3en
Text Label 8050 3150 0    60   ~
a
Text Label 8050 3050 0    60   ~
b
Text Label 8050 2950 0    60   ~
c
Text Label 8050 2850 0    60   ~
d
Text Label 8050 2750 0    60   ~
e
Text Label 8050 2550 0    60   ~
f
Text Label 8050 2450 0    60   ~
g
$Comp
L NPN Q3
U 1 1 4A359B80
P 7800 5750
F 0 "Q3" H 7950 5750 50  0000 C C
F 1 "NPN" H 7702 5900 50  0000 C C
	1    7800 5750
	1    0    0    -1  
$EndComp
Text Label 2600 6700 0    60   ~
dp
Text Label 5150 6750 0    60   ~
dp
Text Label 7800 6750 0    60   ~
dp
$Comp
L GND #PWR013
U 1 1 4A3597C2
P 8900 3450
F 0 "#PWR013" H 8900 3450 30  0001 C C
F 1 "GND" H 8900 3380 30  0001 C C
	1    8900 3450
	1    0    0    -1  
$EndComp
Text Label 3850 3500 0    60   ~
GND
$Comp
L PWR_FLAG #FLG014
U 1 1 4A3596D2
P 3700 3500
F 0 "#FLG014" H 3700 3770 30  0001 C C
F 1 "PWR_FLAG" H 3700 3730 30  0000 C C
	1    3700 3500
	1    0    0    -1  
$EndComp
$Comp
L PWR_FLAG #FLG015
U 1 1 4A3596AC
P 3800 2450
F 0 "#FLG015" H 3800 2720 30  0001 C C
F 1 "PWR_FLAG" H 3800 2680 30  0000 C C
	1    3800 2450
	1    0    0    -1  
$EndComp
Text Label 6400 6700 0    60   ~
g
Text Label 6400 6600 0    60   ~
f
Text Label 6400 6500 0    60   ~
e
Text Label 6400 6400 0    60   ~
d
Text Label 6400 6300 0    60   ~
c
Text Label 6400 6200 0    60   ~
b
Text Label 6400 6100 0    60   ~
a
$Comp
L HDSP-7XXX-A AFF3
U 1 1 4A3595C6
P 7100 6500
F 0 "AFF3" H 7000 6000 60  0000 C C
F 1 "HDSP-7XXX-A" H 7050 7100 60  0000 C C
	1    7100 6500
	1    0    0    -1  
$EndComp
Text Label 3800 6700 0    60   ~
g
Text Label 3800 6600 0    60   ~
f
Text Label 3800 6500 0    60   ~
e
Text Label 3800 6400 0    60   ~
d
Text Label 3800 6300 0    60   ~
c
Text Label 3800 6200 0    60   ~
b
Text Label 3800 6100 0    60   ~
a
$Comp
L HDSP-7XXX-A AFF2
U 1 1 4A3595BF
P 4500 6500
F 0 "AFF2" H 4400 6000 60  0000 C C
F 1 "HDSP-7XXX-A" H 4450 7100 60  0000 C C
	1    4500 6500
	1    0    0    -1  
$EndComp
Text Label 1250 6650 0    60   ~
g
Text Label 1250 6550 0    60   ~
f
Text Label 1250 6450 0    60   ~
e
Text Label 1250 6350 0    60   ~
d
Text Label 1250 6250 0    60   ~
c
Text Label 1250 6150 0    60   ~
b
Text Label 1250 6050 0    60   ~
a
$Comp
L SPEAKER SP1
U 1 1 4A359167
P 9550 2750
F 0 "SP1" H 9450 3000 70  0000 C C
F 1 "PIEZO" H 9450 2500 70  0000 C C
	1    9550 2750
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR016
U 1 1 4A35901F
P 4350 3550
F 0 "#PWR016" H 4350 3550 30  0001 C C
F 1 "GND" H 4350 3480 30  0001 C C
	1    4350 3550
	1    0    0    -1  
$EndComp
$Comp
L HDSP-7XXX-A AFF1
U 1 1 4A358F5C
P 1950 6450
F 0 "AFF1" H 1850 5950 60  0000 C C
F 1 "HDSP-7XXX-A" H 1900 7050 60  0000 C C
	1    1950 6450
	1    0    0    -1  
$EndComp
$Comp
L PIC16F685IP J1
U 1 1 4A3588A3
P 5850 4450
F 0 "J1" H 6400 4400 60  0000 C C
F 1 "PIC16F685" H 5850 4400 60  0000 C C
	1    5850 4450
	1    0    0    -1  
$EndComp
$Comp
L R R1
U 1 1 4A358715
P 8900 2900
F 0 "R1" V 8980 2900 50  0000 C C
F 1 "10k" V 8900 2900 50  0000 C C
	1    8900 2900
	1    0    0    -1  
$EndComp
$Comp
L NPN Q2
U 1 1 4A3586FE
P 5150 5650
F 0 "Q2" H 5300 5650 50  0000 C C
F 1 "NPN" H 5052 5800 50  0000 C C
	1    5150 5650
	1    0    0    -1  
$EndComp
$Comp
L NPN Q1
U 1 1 4A3586FA
P 2650 5600
F 0 "Q1" H 2800 5600 50  0000 C C
F 1 "NPN" H 2552 5750 50  0000 C C
	1    2650 5600
	1    0    0    -1  
$EndComp
$Comp
L CP C1
U 1 1 4A3586A0
P 4150 2950
F 0 "C1" H 4200 3050 50  0000 L C
F 1 "10uF" H 4200 2850 50  0000 L C
	1    4150 2950
	1    0    0    -1  
$EndComp
$Comp
L C C2
U 1 1 4A35868B
P 4600 2950
F 0 "C2" H 4650 3050 50  0000 L C
F 1 ".1uF" H 4650 2850 50  0000 L C
	1    4600 2950
	1    0    0    -1  
$EndComp
$EndSCHEMATC
