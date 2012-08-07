title = 'LIGHTNING DETECTOR'
author = 'techman@dingoblue.net.au'
revision = '1.00'
filename = 'lightning.sch'
components = [
    {
        'refdes': 'L1',
        'filename': 'inductor-1.sym',
        'value': '10mH',
        'device': 'INDUCTOR',
        'symversion': '0.1',
    },
    {
        'filename': 'inductor-1.sym',
        'refdes': 'L2',
        'value': '10mH',
        'device': 'INDUCTOR',
        'symversion': '0.1',
    },
    {
        'filename': 'title-A4.sym',
    },
    {
        'filename': 'capacitor-2.sym',
        'refdes': 'C2',
        'value': '0.01uF',
        'device': 'POLARIZED_CAPACITOR',
        'symversion': '0.1',
    },
    {
        'filename': 'capacitor-2.sym',
        'refdes': 'C1',
        'value': '680pf',
        'device': 'POLARIZED_CAPACITOR',
        'symversion': '0.1',
    },
    {
        'filename': 'capacitor-2.sym',
        'refdes': 'C3',
        'value': '.01uF',
        'device': 'POLARIZED_CAPACITOR',
        'symversion': '0.1',
    },
    {
        'filename': 'capacitor-2.sym',
        'value': '100uF',
        'refdes': 'C4',
        'device': 'POLARIZED_CAPACITOR',
        'symversion': '0.1',
    },
    {
        'filename': 'capacitor-2.sym',
        'value': '.005uF',
        'refdes': 'C5',
        'device': 'POLARIZED_CAPACITOR',
        'symversion': '0.1',
    },
    {
        'filename': 'resistor-1.sym',
        'refdes': 'R1',
        'value': '180k',
        'device': 'RESISTOR',
    },
    {
        'filename': 'resistor-1.sym',
        'refdes': 'R2',
        'value': '3.9k',
        'device': 'RESISTOR',
    },
    {
        'filename': 'resistor-1.sym',
        'refdes': 'R7',
        'value': '47R',
        'device': 'RESISTOR',
    },
    {
        'filename': 'resistor-1.sym',
        'refdes': 'R3',
        'value': '22k',
        'device': 'RESISTOR',
    },
    {
        'filename': 'resistor-1.sym',
        'refdes': 'R5',
        'value': '2.2K',
        'device': 'RESISTOR',
    },
    {
        'filename': 'resistor-1.sym',
        'refdes': 'R6',
        'value': '2.7k',
        'device': 'RESISTOR',
    },
    {
        'filename': 'resistor-variable-1.sym',
        'refdes': 'R4',
        'value': '20k',
        'device': 'VARIABLE_RESISTOR',
    },
    {
        'filename': 'out-1.sym',
        'refdes': 'lamp(1)',
        'device': 'OUTPUT',
    },
    {
        'filename': 'out-1.sym',
        'refdes': 'lamp(2)',
        'device': 'OUTPUT',
    },
    {
        'filename': 'in-1.sym',
        'refdes': 'bat(+3v)',
        'device': 'INPUT',
    },
    {
        'filename': 'in-1.sym',
        'refdes': 'bat(0v)',
        'device': 'INPUT',
    },
    {
        'filename': 'in-1.sym',
        'refdes': 'A1',
        'device': 'INPUT',
    },
    {
        'filename': 'capacitor-2.sym',
        'value': '1uF',
        'refdes': 'C6',
        'device': 'POLARIZED_CAPACITOR',
        'symversion': '0.1',
    },
    {
        'filename': 'diode-1.sym',
        'refdes': 'D1',
        'value': '1N914',
        'device': 'DIODE',
    },
    {
        'filename': '2N4401.sym',
        'refdes': 'Q1',
        'value': '2N4401',
    },
    {
        'filename': '2N4403.sym',
        'refdes': 'Q2',
        'value': '2N4403',
    },
    {
        'filename': '2N4401.sym',
        'value': '2N4401',
        'refdes': 'Q3',
    },
    {
        'filename': '2N4401.sym',
        'refdes': 'Q4',
        'value': '2N4401',
    },
]
#N 53000 63100 53000 61500 4
#N 53000 60600 53000 60000 4
#N 53500 61100 53500 61600 4
#N 53500 60200 53500 60000 4
#N 53500 61600 53000 61600 4
#N 54400 61600 54500 61600 4
#N 55200 63900 55200 62100 4
#N 53000 64700 53000 64000 4
#N 62000 60000 53000 60000 4
#N 55200 61100 55200 60000 4
#N 55200 60000 60200 60000 4
#N 54400 63500 54400 63300 4
#N 54400 62400 54400 61600 4
#N 61700 60500 61700 60000 4
#N 62000 66000 55200 66000 4
#N 55200 66000 55200 64800 4
#N 61500 65800 61500 66000 4
#N 61500 63000 61500 64900 4
#N 61500 63000 61900 63000 4
#N 54400 63500 55200 63500 4
#N 61000 61000 56500 61000 4
#N 56500 61000 56500 61600 4
#N 60200 60900 60200 61000 4
#N 60200 62000 60200 61000 4
#N 60200 63000 60200 64800 4
#N 55200 63000 55600 63000 4
#N 56500 62500 56500 63600 4
#N 56000 64100 56000 64800 4
#N 56000 64800 61500 64800 4
#N 58200 62500 57500 62500 4
#N 61900 62000 61700 62000 4
#N 61700 62000 61700 61500 4
#N 59400 62500 59400 62100 4
#N 59400 61200 59400 61000 4
#N 57500 63500 58000 63500 4
#N 58000 63500 58000 62100 4
#N 58000 61200 58000 61000 4
#N 60800 64100 60800 66000 4
#N 60800 63200 60800 60000 4
#N 59100 62500 59500 62500 4
#N 56500 63000 56800 63000 4
#N 56500 64500 56500 64800 4
#N 57500 64700 57500 64800 4
#N 57500 63500 57500 63800 4


header = ['device', 'value', 'footprint', 'quantity', 'refdes']
data = [
    ['DIODE', '1N914', 'unknown', 1, ['D1']],
    ['INDUCTOR', '10mH', 'unknown', 2, ['L1', 'L2']],
    ['INPUT', 'unknown', 'unknown', 3, ['A1', 'bat(+3v)', 'bat(0v)']],
    ['OUTPUT', 'unknown', 'unknown', 2, ['lamp(1)', 'lamp(2)']],
    ['POLARIZED_CAPACITOR', '.005uF', 'unknown', 1, ['C5']],
    ['POLARIZED_CAPACITOR', '.01uF', 'unknown', 1, ['C3']],
    ['POLARIZED_CAPACITOR', '0.01uF', 'unknown', 1, ['C2']],
    ['POLARIZED_CAPACITOR', '100uF', 'unknown', 1, ['C4']],
    ['POLARIZED_CAPACITOR', '1uF', 'unknown', 1, ['C6']],
    ['POLARIZED_CAPACITOR', '680pf', 'unknown', 1, ['C1']],
    ['RESISTOR', '180k', 'unknown', 1, ['R1']],
    ['RESISTOR', '2.2K', 'unknown', 1, ['R5']],
    ['RESISTOR', '2.7k', 'unknown', 1, ['R6']],
    ['RESISTOR', '22k', 'unknown', 1, ['R3']],
    ['RESISTOR', '3.9k', 'unknown', 1, ['R2']],
    ['RESISTOR', '47R', 'unknown', 1, ['R7']],
    ['unknown', '2N4401', 'unknown', 3, ['Q1', 'Q3', 'Q4']],
    ['unknown', '2N4403', 'unknown', 1, ['Q2']],
    ['VARIABLE_RESISTOR', '20k', 'unknown', 1, ['R4']],
]

bom = []
for item in data:
    bom.append(dict(zip(header, data)))
