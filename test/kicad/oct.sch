EESchema Schematic File Version 1
LIBS:power,device,conn,linear,regul,74xx,cmos4000,adc-dac,memory,xilinx,special,microcontrollers,microchip,analog_switches,motorola,intel,audio,interface,digital-audio,philips,display,cypress,siliconi,contrib,./oct.cache
EELAYER 23  0
EELAYER END
$Descr A4 11700 8267
Sheet 1 1
Title "OpenCryptoToken"
Date "18 sep 2007"
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Connection ~ 6400 3600
Wire Wire Line
	2500 4100 2300 4100
Connection ~ 2300 3600
Connection ~ 2300 4100
Wire Wire Line
	2300 4300 2300 3200
Wire Wire Line
	3250 3600 3100 3600
Wire Wire Line
	3100 3600 3100 4100
$Comp
L SW_PUSH SW1
U 1 1 46F026A9
P 2800 4100
F 0 "SW1" H 2950 4210 50  0000 C C
F 1 "SW_PUSH" H 2800 4020 50  0000 C C
	1    2800 4100
	1    0    0    -1  
$EndComp
Kmarq B 3250 3100 "Warning Pin BiDi Unconnected" F=1
Kmarq B 3250 3300 "Warning Pin BiDi Unconnected" F=1
Kmarq B 3250 3400 "Warning Pin BiDi Unconnected" F=1
Kmarq B 3250 3500 "Warning Pin BiDi Unconnected" F=1
Kmarq B 3250 3600 "Warning Pin BiDi Unconnected" F=1
Kmarq B 3250 3700 "Warning Pin BiDi Unconnected" F=1
Kmarq B 3250 4200 "Warning Pin input Unconnected" F=1
Kmarq B 3250 4300 "Warning Pin input Unconnected" F=1
Kmarq B 5650 3200 "Warning Pin BiDi Unconnected" F=1
Kmarq B 5650 4000 "Warning Pin BiDi Unconnected" F=1
Kmarq B 5650 4100 "Warning Pin BiDi Unconnected" F=1
Kmarq B 5650 4200 "Warning Pin BiDi Unconnected" F=1
Kmarq B 5650 4300 "Warning Pin BiDi Unconnected" F=1
Kmarq B 5650 4400 "Warning Pin BiDi Unconnected" F=1
Kmarq B 5650 4500 "Warning Pin BiDi Unconnected" F=1
Kmarq B 4150 2200 "Warning Pin power_in Unconnected" F=1
Kmarq B 4350 2200 "Warning Pin power_in not driven (Net 13)" F=1
Kmarq B 6400 3600 "Warning Pin passive Unconnected" F=1
Kmarq B 6900 3000 "Warning Pin passive Unconnected" F=1
Kmarq B 5900 4350 "Warning Pin power_in not driven (Net 3)" F=1
Wire Wire Line
	5800 2500 5700 2500
Wire Wire Line
	5650 3000 5700 3000
Wire Wire Line
	5700 3000 5700 2500
Wire Wire Line
	5900 3800 5900 3100
Wire Wire Line
	5900 3100 5650 3100
Wire Wire Line
	5900 4200 5900 4350
Connection ~ 6400 4200
Wire Wire Line
	6500 4200 6150 4200
Wire Wire Line
	6150 4200 6150 3700
Wire Wire Line
	6150 3700 5650 3700
$Comp
L GND #PWR6
U 1 1 46F00EBB
P 5900 4350
F 0 "#PWR6" H 5900 4350 30  0001 C C
F 1 "GND" H 5900 4280 30  0001 C C
	1    5900 4350
	1    0    0    -1  
$EndComp
Wire Wire Line
	6900 3100 7000 3100
Wire Wire Line
	7000 3100 7000 4600
Wire Wire Line
	7000 4600 5650 4600
Wire Wire Line
	6900 3350 6900 3200
Wire Wire Line
	6100 3000 5950 3000
Wire Wire Line
	5950 3000 5950 3300
Wire Wire Line
	5950 3300 5650 3300
Wire Wire Line
	6100 3100 6000 3100
Wire Wire Line
	6000 3100 6000 3400
Wire Wire Line
	6000 3400 5650 3400
Wire Wire Line
	5650 3500 6050 3500
Wire Wire Line
	6050 3500 6050 3200
Wire Wire Line
	6050 3200 6100 3200
$Comp
L C C5
U 1 1 46F00DD6
P 5900 4000
F 0 "C5" H 5950 4100 50  0000 L C
F 1 "10n" H 5950 3900 50  0000 L C
	1    5900 4000
	1    0    0    -1  
$EndComp
Connection ~ 4750 2100
Wire Wire Line
	6850 2100 2650 2100
Wire Wire Line
	6850 2750 6850 2500
Wire Wire Line
	6850 2500 6700 2500
$Comp
L R R1
U 1 1 46F00AE4
P 6050 2500
F 0 "R1" V 6130 2500 50  0000 C C
F 1 "1k" V 5950 2500 50  0000 C C
	1    6050 2500
	0    1    1    0   
$EndComp
$Comp
L LED D3
U 1 1 46F00ABA
P 6500 2500
F 0 "D3" H 6500 2600 50  0000 C C
F 1 "LED" H 6500 2400 50  0000 C C
	1    6500 2500
	1    0    0    -1  
$EndComp
Wire Wire Line
	3250 3200 3150 3200
Wire Wire Line
	3150 3200 3150 3100
Wire Wire Line
	3150 3100 2300 3100
$Comp
L GND #PWR5
U 1 1 46EFE777
P 6900 3350
F 0 "#PWR5" H 6900 3350 30  0001 C C
F 1 "GND" H 6900 3280 30  0001 C C
	1    6900 3350
	1    0    0    -1  
$EndComp
$Comp
L CONN_3X2 P2
U 1 1 46EFE6C0
P 6500 3150
F 0 "P2" H 6500 3400 50  0000 C C
F 1 "ISP" V 6500 3200 40  0000 C C
	1    6500 3150
	1    0    0    -1  
$EndComp
Wire Wire Line
	5650 3600 6500 3600
$Comp
L CRYSTAL X1
U 1 1 46ED7938
P 6400 3900
F 0 "X1" H 6400 4050 60  0000 C C
F 1 "12Mhz" H 6400 3750 60  0000 C C
	1    6400 3900
	0    1    1    0   
$EndComp
Wire Wire Line
	2650 2100 2650 2900
Connection ~ 4350 2100
Connection ~ 4550 2100
Wire Wire Line
	4350 2100 4350 2200
Wire Wire Line
	4550 2100 4550 2200
Wire Wire Line
	4750 2100 4750 2200
Connection ~ 2550 3600
Wire Wire Line
	2300 3600 2950 3600
Connection ~ 2950 3000
Wire Wire Line
	2950 3200 2950 3000
Connection ~ 2550 3100
Wire Wire Line
	2550 3200 2550 3100
Wire Wire Line
	2650 2900 2300 2900
Wire Wire Line
	2300 3000 3250 3000
$Comp
L ZENER D2
U 1 1 46ED7229
P 2950 3400
F 0 "D2" H 2950 3550 50  0000 C C
F 1 "3v6" H 2950 3250 40  0000 C C
	1    2950 3400
	0    -1   -1   0   
$EndComp
$Comp
L ZENER D1
U 1 1 46ED71DB
P 2550 3400
F 0 "D1" H 2550 3550 50  0000 C C
F 1 "3v6" H 2550 3250 40  0000 C C
	1    2550 3400
	0    -1   -1   0   
$EndComp
$Comp
L GND #PWR3
U 1 1 46ED6F7C
P 2300 4300
F 0 "#PWR3" H 2300 4300 30  0001 C C
F 1 "GND" H 2300 4230 30  0001 C C
	1    2300 4300
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR2
U 1 1 46ED6F51
P 6850 2750
F 0 "#PWR2" H 6850 2750 30  0001 C C
F 1 "GND" H 6850 2680 30  0001 C C
	1    6850 2750
	1    0    0    -1  
$EndComp
Wire Wire Line
	6900 3600 6900 5400
$Comp
L C C3
U 1 1 46ED6EEB
P 6850 2300
F 0 "C3" H 6900 2400 50  0000 L C
F 1 "100n" H 6900 2200 50  0000 L C
	1    6850 2300
	1    0    0    -1  
$EndComp
Connection ~ 4650 5400
Wire Wire Line
	6900 5400 4250 5400
Connection ~ 4150 2200
Text Label 3000 3100 0    60   ~
D+
Text Label 3000 3000 0    60   ~
D-
$Comp
L CONN_4 P1
U 1 1 46ED6602
P 1950 3050
F 0 "P1" V 1900 3050 50  0000 C C
F 1 "USB-A" V 2000 3050 50  0000 C C
	1    1950 3050
	-1   0    0    -1  
$EndComp
Wire Wire Line
	4450 5400 4450 5600
$Comp
L GND #PWR1
U 1 1 46ED5A1B
P 4450 5600
F 0 "#PWR1" H 4450 5600 30  0001 C C
F 1 "GND" H 4450 5530 30  0001 C C
	1    4450 5600
	1    0    0    -1  
$EndComp
Connection ~ 4450 5400
Connection ~ 6900 4200
$Comp
L C C2
U 1 1 46ED5924
P 6700 3600
F 0 "C2" H 6750 3700 50  0000 L C
F 1 "27p" H 6750 3500 50  0000 L C
	1    6700 3600
	0    1    1    0   
$EndComp
$Comp
L C C1
U 1 1 46ED5904
P 6700 4200
F 0 "C1" H 6750 4300 50  0000 L C
F 1 "27p" H 6750 4100 50  0000 L C
	1    6700 4200
	0    1    1    0   
$EndComp
$Comp
L ATMEGA8 I1
U 1 1 46ED580E
P 4450 3750
F 0 "I1" H 5150 5150 60  0000 C C
F 1 "ATMEGA8" H 5100 2300 60  0000 C C
	1    4450 3750
	1    0    0    -1  
$EndComp
$EndSCHEMATC
