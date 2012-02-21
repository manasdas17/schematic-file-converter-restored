EESchema Schematic File Version 2  date 30/07/2010 20:15:21
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:special
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:ps2toserial-cache
EELAYER 24  0
EELAYER END
$Descr User 6000 6000
Sheet 1 1
Title "PS/2 to serial converter"
Date "30 jul 2010"
Rev "2010.06.22"
Comp "PulkoTronics"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Wire Wire Line
	4500 2350 4250 2350
Wire Wire Line
	3750 2350 3750 2600
Wire Bus Line
	3850 3500 5150 3500
Wire Bus Line
	5150 3500 5150 4200
Wire Bus Line
	5150 4200 3850 4200
Wire Bus Line
	3850 4200 3850 3350
Wire Wire Line
	4400 3600 5050 3600
Wire Wire Line
	1000 650  600  650 
Wire Wire Line
	600  650  600  4300
Wire Wire Line
	4550 3800 4400 3800
Wire Wire Line
	3700 3100 3350 3100
Wire Notes Line
	2950 600  2950 700 
Wire Notes Line
	2950 700  2750 700 
Wire Notes Line
	4350 1650 4800 1650
Wire Notes Line
	4800 1650 4800 600 
Wire Notes Line
	4800 600  2750 600 
Wire Notes Line
	2750 600  2750 1400
Connection ~ 4200 1650
Wire Wire Line
	4300 1350 4300 1650
Wire Wire Line
	4300 1650 4100 1650
Wire Wire Line
	3850 1550 4100 1550
Wire Wire Line
	3300 1150 3400 1150
Wire Wire Line
	4300 1050 4300 650 
Connection ~ 4100 1150
Connection ~ 600  1150
Wire Wire Line
	600  1150 1000 1150
Wire Wire Line
	4050 3200 4150 3200
Wire Wire Line
	1700 1400 2350 1400
Connection ~ 600  1900
Wire Wire Line
	1100 1700 1450 1700
Wire Wire Line
	3350 4000 3550 4000
Wire Wire Line
	3350 3800 3550 3800
Wire Wire Line
	600  1900 1450 1900
Wire Wire Line
	2350 4600 2350 4300
Connection ~ 1100 2200
Wire Wire Line
	1000 2200 1450 2200
Wire Wire Line
	1450 2600 1450 2800
Connection ~ 2350 4300
Wire Notes Line
	3850 3350 4700 3350
Wire Wire Line
	3350 2900 3550 2900
Wire Wire Line
	3350 3000 3550 3000
Wire Notes Line
	4700 3350 4700 3500
Wire Wire Line
	1450 2100 2350 2100
Wire Wire Line
	2350 2100 2350 1100
Connection ~ 2350 1400
Wire Wire Line
	1450 2200 1450 2400
Wire Wire Line
	1450 2800 1000 2800
Connection ~ 1100 2800
Connection ~ 1450 1900
Connection ~ 600  2200
Wire Wire Line
	2350 4300 600  4300
Connection ~ 600  2800
Wire Wire Line
	3350 3900 3550 3900
Connection ~ 1200 1700
Connection ~ 2350 1150
Connection ~ 1200 1400
Wire Wire Line
	3350 3200 3550 3200
Wire Wire Line
	4550 3200 4700 3200
Wire Wire Line
	1400 1150 2350 1150
Connection ~ 1900 1150
Wire Wire Line
	4300 1150 3900 1150
Connection ~ 4000 1150
Wire Wire Line
	4300 1250 3900 1250
Connection ~ 4200 1250
Wire Wire Line
	4300 650  3900 650 
Connection ~ 4000 650 
Wire Wire Line
	3300 1250 3400 1250
Wire Wire Line
	4100 1550 4100 1650
Wire Notes Line
	2750 1400 3750 1400
Wire Notes Line
	3750 1400 3750 1550
Wire Wire Line
	3700 2800 3350 2800
Wire Wire Line
	4550 3700 4400 3700
Wire Wire Line
	1200 1400 1200 1700
Wire Wire Line
	1400 650  1900 650 
Wire Wire Line
	1900 650  1900 1150
Connection ~ 4550 3600
Wire Wire Line
	4350 4100 5050 4100
Connection ~ 4550 4100
Wire Wire Line
	3750 2600 3350 2600
Wire Wire Line
	4350 2600 4500 2600
$Comp
L JUMPER JP1
U 1 1 4C5307D0
P 4050 2600
F 0 "JP1" H 4050 2750 60  0000 C CNN
F 1 "FWUP" H 4050 2520 40  0000 C CNN
	1    4050 2600
	1    0    0    -1  
$EndComp
$Comp
L R R8
U 1 1 4C5307BB
P 4000 2350
F 0 "R8" V 4080 2350 50  0000 C CNN
F 1 "10K" V 4000 2350 50  0000 C CNN
	1    4000 2350
	0    -1   -1   0   
$EndComp
$Comp
L +5V #PWR01
U 1 1 4C5307A3
P 4500 2350
F 0 "#PWR01" H 4500 2440 20  0001 C CNN
F 1 "+5V" H 4500 2440 30  0000 C CNN
	1    4500 2350
	0    1    1    0   
$EndComp
$Comp
L GND #PWR02
U 1 1 4C530791
P 4500 2600
F 0 "#PWR02" H 4500 2600 30  0001 C CNN
F 1 "GND" H 4500 2530 30  0001 C CNN
	1    4500 2600
	0    -1   -1   0   
$EndComp
$Comp
L CP1 C5
U 1 1 4C52C709
P 1200 650
F 0 "C5" H 1250 750 50  0000 L CNN
F 1 "10µF" H 1250 550 50  0000 L CNN
	1    1200 650 
	0    1    1    0   
$EndComp
Text Notes 2950 700  2    60   ~ 0
USB
$Comp
L ZENER D4
U 1 1 4C21F047
P 4200 1450
F 0 "D4" H 4150 1200 50  0000 C CNN
F 1 "3.6V" H 4150 1300 40  0000 C CNN
	1    4200 1450
	0    -1   -1   0   
$EndComp
$Comp
L ZENER D3
U 1 1 4C21F044
P 4100 1350
F 0 "D3" H 4100 1450 50  0000 C CNN
F 1 "3.6V" H 4100 1550 40  0000 C CNN
	1    4100 1350
	0    -1   -1   0   
$EndComp
$Comp
L R R4
U 1 1 4C21F015
P 4000 900
F 0 "R4" V 4080 900 50  0000 C CNN
F 1 "2.2KR" V 4000 900 50  0000 C CNN
	1    4000 900 
	1    0    0    -1  
$EndComp
$Comp
L R R7
U 1 1 4C21EFE9
P 3650 1250
F 0 "R7" V 3730 1250 50  0000 C CNN
F 1 "68R" V 3650 1250 50  0000 C CNN
	1    3650 1250
	0    1    1    0   
$EndComp
$Comp
L R R6
U 1 1 4C21EFE5
P 3650 1150
F 0 "R6" V 3550 1150 50  0000 C CNN
F 1 "68R" V 3650 1150 50  0000 C CNN
	1    3650 1150
	0    1    1    0   
$EndComp
Text GLabel 3300 1150 0    60   BiDi ~ 0
USB_D-
Text GLabel 3300 1250 0    60   BiDi ~ 0
USB_D+
$Comp
L +5V #PWR03
U 1 1 4C21EFA8
P 3900 650
F 0 "#PWR03" H 3900 740 20  0001 C CNN
F 1 "+5V" H 3900 740 30  0000 C CNN
	1    3900 650 
	0    -1   -1   0   
$EndComp
$Comp
L GND #PWR04
U 1 1 4C21EFA1
P 3850 1550
F 0 "#PWR04" H 3850 1550 30  0001 C CNN
F 1 "GND" H 3850 1480 30  0001 C CNN
	1    3850 1550
	0    1    1    0   
$EndComp
$Comp
L CONN_4 USB1
U 1 1 4C21EF7A
P 4650 1200
F 0 "USB1" V 4600 1200 50  0000 C CNN
F 1 "CONN_4" V 4700 1200 50  0000 C CNN
	1    4650 1200
	1    0    0    -1  
$EndComp
Text GLabel 3700 3100 2    60   BiDi ~ 0
USB_D-
Text GLabel 3700 2800 2    60   BiDi ~ 0
USB_D+
$Comp
L R R5
U 1 1 4C21EEDC
P 5050 3850
F 0 "R5" V 5130 3850 50  0000 C CNN
F 1 "480R" V 5050 3850 50  0000 C CNN
	1    5050 3850
	1    0    0    -1  
$EndComp
Text Notes 3800 3700 2    60   ~ 0
to ICSP
Text Notes 4600 2950 2    60   ~ 0
to Keyboard
$Comp
L C C4
U 1 1 4C20B56F
P 1200 1150
F 0 "C4" H 1250 1250 50  0000 L CNN
F 1 "100nF" H 1250 1050 50  0000 L CNN
	1    1200 1150
	0    -1   -1   0   
$EndComp
$Comp
L GND #PWR05
U 1 1 4C20B3CD
P 4700 3200
F 0 "#PWR05" H 4700 3200 30  0001 C CNN
F 1 "GND" H 4700 3130 30  0001 C CNN
	1    4700 3200
	0    -1   -1   0   
$EndComp
$Comp
L LED D2
U 1 1 4C20B393
P 4350 3200
F 0 "D2" H 4350 3300 50  0000 C CNN
F 1 "LED" H 4350 3100 50  0000 C CNN
	1    4350 3200
	1    0    0    -1  
$EndComp
$Comp
L R R2
U 1 1 4C20B383
P 3800 3200
F 0 "R2" V 3700 3200 50  0000 C CNN
F 1 "470R" V 3800 3200 50  0000 C CNN
	1    3800 3200
	0    -1   -1   0   
$EndComp
$Comp
L R R1
U 1 1 4C20B267
P 1450 1400
F 0 "R1" V 1530 1400 50  0000 C CNN
F 1 "10K" V 1450 1400 50  0000 C CNN
	1    1450 1400
	0    -1   -1   0   
$EndComp
Text GLabel 3550 4000 2    60   Input ~ 0
SCK
Text GLabel 1100 1700 0    60   Input ~ 0
RESET
Text GLabel 3550 3900 2    60   Output ~ 0
MISO
Text GLabel 3550 3800 2    60   Input ~ 0
MOSI
$Comp
L C C2
U 1 1 4C20AD73
P 800 2800
F 0 "C2" H 850 2900 50  0000 L CNN
F 1 "27pF" H 850 2700 50  0000 L CNN
	1    800  2800
	0    1    1    0   
$EndComp
$Comp
L C C1
U 1 1 4C20AD6D
P 800 2200
F 0 "C1" H 850 2300 50  0000 L CNN
F 1 "27pF" H 850 2100 50  0000 L CNN
	1    800  2200
	0    1    1    0   
$EndComp
$Comp
L CRYSTAL X1
U 1 1 4C20AD34
P 1100 2500
F 0 "X1" H 1100 2650 60  0000 C CNN
F 1 "16MHz" H 1100 2350 60  0000 C CNN
	1    1100 2500
	0    1    1    0   
$EndComp
$Comp
L +5V #PWR06
U 1 1 4C20ABFF
P 4350 4100
F 0 "#PWR06" H 4350 4190 20  0001 C CNN
F 1 "+5V" H 4350 4190 30  0000 C CNN
	1    4350 4100
	0    -1   -1   0   
$EndComp
$Comp
L GND #PWR07
U 1 1 4C20ABF2
P 4400 3700
F 0 "#PWR07" H 4400 3700 30  0001 C CNN
F 1 "GND" H 4400 3630 30  0001 C CNN
	1    4400 3700
	0    1    1    0   
$EndComp
Text Notes 3900 3450 0    60   ~ 0
Connecteur ps/2
Text GLabel 3550 3000 2    60   BiDi ~ 0
PS2_DATA
Text GLabel 4400 3800 0    60   BiDi ~ 0
PS2_DATA
Text GLabel 4400 3600 0    60   Output ~ 0
PS2_CLK
Text GLabel 3550 2900 2    60   Input ~ 0
PS2_CLK
$Comp
L GND #PWR08
U 1 1 4C20AAB2
P 2350 4600
F 0 "#PWR08" H 2350 4600 30  0001 C CNN
F 1 "GND" H 2350 4530 30  0001 C CNN
	1    2350 4600
	1    0    0    -1  
$EndComp
$Comp
L +5V #PWR09
U 1 1 4C20AAA4
P 2350 1100
F 0 "#PWR09" H 2350 1190 20  0001 C CNN
F 1 "+5V" H 2350 1190 30  0000 C CNN
	1    2350 1100
	1    0    0    -1  
$EndComp
$Comp
L CONN_6 PS2
U 1 1 4C20A3B4
P 4900 3850
F 0 "PS2" V 4850 3850 60  0000 C CNN
F 1 "CONN_6" V 4950 3850 60  0000 C CNN
F 2 "Mini_din6" V 4790 3790 60  0001 C CNN
	1    4900 3850
	1    0    0    -1  
$EndComp
$Comp
L ATMEGA8-P IC1
U 1 1 4C209A59
P 2350 2800
F 0 "IC1" H 1650 4050 50  0000 L BNN
F 1 "ATMEGA8-P" H 2600 1400 50  0000 L BNN
F 2 "DIP-28__300" H 2850 1325 50  0001 C CNN
	1    2350 2800
	1    0    0    -1  
$EndComp
$EndSCHEMATC
