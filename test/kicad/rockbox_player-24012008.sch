EESchema Schematic File Version 1
LIBS:power,C:/Users/jpinto/Documents/01_projectos/90-auto_formacao/Rockbox Player/TLV320AIC23,device,transistors,conn,linear,regul,74xx,cmos4000,adc-dac,memory,xilinx,special,microcontrollers,dsp,microchip,analog_switches,motorola,texas,intel,audio,interface,digital-audio,philips,display,cypress,siliconi,contrib,valves
EELAYER 23  0
EELAYER END
$Descr A4 11700 8267
Sheet 1 1
Title "Rockbox Player"
Date "24 jan 2008"
Rev ""
Comp "Jorge Pinto"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Wire Wire Line
	7350 2550 7350 3050
Wire Wire Line
	7350 3050 6300 3050
Wire Wire Line
	6300 3050 6300 2650
Wire Wire Line
	7150 2550 7150 2850
Wire Wire Line
	7150 2850 6100 2850
Wire Wire Line
	6100 2850 6100 2650
Wire Wire Line
	7050 2550 7050 2700
Wire Wire Line
	6600 4250 7750 4250
Wire Wire Line
	7750 4250 7750 3400
Wire Wire Line
	7750 3400 6000 3400
Wire Wire Line
	6000 3400 6000 2650
Wire Wire Line
	5100 4250 4700 4250
Wire Wire Line
	4700 4250 4700 3400
Wire Wire Line
	4700 3400 5800 3400
Wire Wire Line
	5800 3400 5800 2650
Wire Wire Line
	6600 4450 7550 4450
Wire Wire Line
	7550 4450 7550 3150
Wire Wire Line
	7550 3150 5600 3150
Wire Wire Line
	5600 3150 5600 2650
Wire Wire Line
	5200 3050 5200 3150
Wire Wire Line
	5200 3150 5400 3150
Wire Wire Line
	5400 3150 5400 2650
Connection ~ 4150 4750
Wire Wire Line
	4150 4750 4150 4300
Wire Wire Line
	4150 4300 3050 4300
Wire Wire Line
	4750 4900 4750 4850
Wire Wire Line
	4750 4900 4350 4900
Connection ~ 6900 4050
Wire Wire Line
	6600 4050 6900 4050
Wire Wire Line
	6900 4050 7000 4050
Connection ~ 3100 4900
Wire Wire Line
	3250 4750 3100 4750
Wire Wire Line
	3750 4900 3850 4900
Wire Wire Line
	3850 4900 3950 4900
Wire Wire Line
	4750 4850 5100 4850
Connection ~ 6950 5550
Wire Wire Line
	6750 5550 6950 5550
Wire Wire Line
	6950 5550 7300 5550
Connection ~ 6750 5550
Connection ~ 6750 4550
Wire Wire Line
	6750 4550 6600 4550
Wire Wire Line
	6750 5250 6600 5250
Wire Wire Line
	4850 3750 4850 3950
Wire Wire Line
	4850 3950 4850 4650
Wire Wire Line
	4850 4650 4850 5250
Connection ~ 4850 3950
Wire Wire Line
	5100 4650 4850 4650
Wire Wire Line
	6900 3900 6900 4050
Wire Wire Line
	4850 3950 5100 3950
Wire Wire Line
	4850 5250 5100 5250
Connection ~ 4850 4650
Wire Wire Line
	4950 5400 4950 4950
Wire Wire Line
	4950 4950 5100 4950
Wire Wire Line
	6600 3950 6750 3950
Wire Wire Line
	6750 3950 6750 4150
Wire Wire Line
	6750 4150 6750 4550
Wire Wire Line
	6750 4550 6750 5250
Wire Wire Line
	6750 5250 6750 5550
Wire Wire Line
	6750 5550 6750 5750
Connection ~ 6750 5250
Wire Wire Line
	6600 5150 6950 5150
Wire Wire Line
	6950 5150 7300 5150
Connection ~ 6950 5150
Wire Wire Line
	4250 4750 4150 4750
Wire Wire Line
	4150 4750 3750 4750
Wire Wire Line
	3100 4900 3250 4900
Wire Wire Line
	4650 4750 5100 4750
Wire Wire Line
	3050 4450 3100 4450
Wire Wire Line
	3100 4450 3100 4750
Wire Wire Line
	3100 4750 3100 4900
Wire Wire Line
	3100 4900 3100 5100
Connection ~ 3100 4750
Wire Wire Line
	3050 4550 3850 4550
Wire Wire Line
	3850 4550 3850 4900
Connection ~ 3850 4900
Wire Wire Line
	5500 2650 5500 3250
Wire Wire Line
	5700 2650 5700 3250
Wire Wire Line
	5700 3250 7650 3250
Wire Wire Line
	7650 3250 7650 4350
Wire Wire Line
	7650 4350 6600 4350
Wire Wire Line
	5900 2650 5900 3500
Wire Wire Line
	5900 3500 4600 3500
Wire Wire Line
	4600 3500 4600 4350
Wire Wire Line
	4600 4350 5100 4350
Wire Wire Line
	6750 4150 7400 4150
Connection ~ 6750 4150
Wire Wire Line
	7400 4150 7400 4050
Wire Wire Line
	6950 2550 6950 2650
Wire Wire Line
	6950 2650 6750 2650
Wire Wire Line
	6750 2650 6750 2500
Wire Wire Line
	6200 2650 6200 2950
Wire Wire Line
	6200 2950 7250 2950
Wire Wire Line
	7250 2950 7250 2550
$Comp
L GND #PWR?
U 1 1 4798760F
P 7050 2700
F 0 "#PWR?" H 7050 2700 30  0001 C C
F 1 "GND" H 7050 2630 30  0001 C C
	1    7050 2700
	1    0    0    -1  
$EndComp
$Comp
L +3.3V #PWR?
U 1 1 47987608
P 6750 2500
F 0 "#PWR?" H 6750 2460 30  0001 C C
F 1 "+3.3V" H 6750 2610 30  0000 C C
	1    6750 2500
	1    0    0    -1  
$EndComp
$Comp
L CONN_5 connector~2
U 1 1 4798741F
P 7150 2150
F 0 "connector 2" V 7300 2150 50  0000 C C
F 1 "CONN_5" V 7200 2150 50  0001 C C
	1    7150 2150
	0    -1   -1   0   
$EndComp
$Comp
L GND #PWR?
U 1 1 479873A3
P 5500 3250
F 0 "#PWR?" H 5500 3250 30  0001 C C
F 1 "GND" H 5500 3180 30  0001 C C
	1    5500 3250
	1    0    0    -1  
$EndComp
$Comp
L +3.3V #PWR?
U 1 1 4798737C
P 5200 3050
F 0 "#PWR?" H 5200 3010 30  0001 C C
F 1 "+3.3V" H 5200 3160 30  0000 C C
	1    5200 3050
	1    0    0    -1  
$EndComp
$Comp
L CONN_10 connector~1
U 1 1 47987363
P 5850 2300
F 0 "connector 1" V 6000 2300 60  0000 C C
F 1 "CONN_10" V 5900 2300 60  0001 C C
	1    5850 2300
	0    -1   -1   0   
$EndComp
$Comp
L JACK_2P Jack~stereo~headphones
U 1 1 47986A51
P 2600 4450
F 0 "Jack stereo headphones" H 2950 4800 60  0000 C C
F 1 "JACK_2P" H 2450 4700 60  0000 C C
	1    2600 4450
	1    0    0    -1  
$EndComp
$Comp
L C C5
U 1 1 47986797
P 7200 4050
F 0 "C5" V 6900 4100 50  0000 L C
F 1 "100nF" V 7000 4150 50  0000 L C
	1    7200 4050
	0    1    1    0   
$EndComp
$Comp
L GND #PWR?
U 1 1 4798656D
P 3100 5100
F 0 "#PWR?" H 3100 5100 30  0001 C C
F 1 "GND" H 3100 5030 30  0001 C C
	1    3100 5100
	1    0    0    -1  
$EndComp
$Comp
L R 47K5
U 1 1 4798653E
P 3500 4900
F 0 "47K5" V 3580 4900 50  0000 C C
F 1 "R1" V 3500 4900 50  0000 C C
	1    3500 4900
	0    1    1    0   
$EndComp
$Comp
L R 47K5
U 1 1 479864E8
P 3500 4750
F 0 "47K5" V 3400 4750 50  0000 C C
F 1 "R1" V 3500 4750 50  0000 C C
	1    3500 4750
	0    1    1    0   
$EndComp
$Comp
L CAPAPOL C4
U 1 1 479863FA
P 4150 4900
F 0 "C4" V 4300 4900 50  0000 L C
F 1 "220uF" V 4400 4950 50  0000 L C
	1    4150 4900
	0    1    1    0   
$EndComp
$Comp
L CAPAPOL C3
U 1 1 479863AE
P 4450 4750
F 0 "C3" V 4150 4750 50  0000 L C
F 1 "220uF" V 4250 4850 50  0000 L C
	1    4450 4750
	0    1    1    0   
$EndComp
$Comp
L CAPAPOL C2
U 1 1 479862AA
P 7300 5350
F 0 "C2" H 7350 5450 50  0000 L C
F 1 "10uF" H 7350 5250 50  0000 L C
	1    7300 5350
	1    0    0    -1  
$EndComp
$Comp
L C C1
U 1 1 4798623A
P 6950 5350
F 0 "C1" H 7000 5450 50  0000 L C
F 1 "0.1uF" H 7000 5250 50  0000 L C
	1    6950 5350
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR?
U 1 1 479861C0
P 6750 5750
F 0 "#PWR?" H 6750 5750 30  0001 C C
F 1 "GND" H 6750 5680 30  0001 C C
	1    6750 5750
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR?
U 1 1 47986179
P 4950 5400
F 0 "#PWR?" H 4950 5400 30  0001 C C
F 1 "GND" H 4950 5330 30  0001 C C
	1    4950 5400
	1    0    0    -1  
$EndComp
$Comp
L +3.3V #PWR?
U 1 1 479860B3
P 4850 3750
F 0 "#PWR?" H 4850 3710 30  0001 C C
F 1 "+3.3V" H 4850 3860 30  0000 C C
	1    4850 3750
	1    0    0    -1  
$EndComp
$Comp
L +3.3V #PWR?
U 1 1 47986032
P 6900 3900
F 0 "#PWR?" H 6900 3860 30  0001 C C
F 1 "+3.3V" H 6900 4010 30  0000 C C
	1    6900 3900
	1    0    0    -1  
$EndComp
$Comp
L TLV320AIC23 U1
U 1 1 47985ED5
P 5850 4600
F 0 "U1" H 5850 4500 50  0000 C C
F 1 "TLV320AIC23" H 5850 4700 50  0000 C C
	1    5850 4600
	1    0    0    -1  
$EndComp
$EndSCHEMATC
