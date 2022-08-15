import pyvisa
import numpy as np
import pandas as pd
import skrf as rf
from time import sleep

"""
# Description
This script controls a vector network analyzer and two regulated power supplies.
S-parameters and operating points are measured while sweeping biases.
The measurement results are saved as the CSV format and the touchstone format.

# Requirements
- Keysight IO Libraries Suite (https://www.keysight.com/en/pd-1985909/io-libraries-suite?cc=US&lc=eng&jmpid=zzfindiolib)
- pyvisa (```pip install pyvisa```)
- numpy (```pip install numpy```)
- pandas (```pip install pandas```)
- scikit-rf (```pip install scikit-rf```)

# Instruments
- Hewlett-Packard 8510C
- KIKUSUI PMX35-1A (x2)

# Author
Keisuke Kawahara <7320529(at)ed.tus.ac.jp>
"""

# Connect to the instruments
rm = pyvisa.ResourceManager()
visa_list = rm.list_resources()
print(visa_list)
vna = rm.open_resource(visa_list[0])
ps1 = rm.open_resource(visa_list[4])
ps2 = rm.open_resource(visa_list[3])

# Setting of the VNA
f_start = 1 # GHz
f_end = 50 # GHz
f_npoints = 401 # Only 51, 101, 201, or 401
aver_factor = 512
cal_on = True
cal_number = 1

# Setting of the power supplies
biases1 = tuple((i/10 for i in range(0, 19, 2)))
biases2 = tuple((i/10 for i in range(0, 19, 2)))

biases = [(bias1, bias2)
    for bias1 in biases1
    for bias2 in biases2
    ]

# Initial process
freq = rf.Frequency(f_start, f_end, f_npoints, 'ghz')
opr_points = pd.DataFrame(columns=['v1', 'v2', 'meas_v1', 'meas_i1', 'meas_v2', 'meas_i2'])
vna.write('STAR ' + str(f_start) + ' GHz; STOP ' + str(f_end) + ' GHz;')
vna.write('POIN ' + str(f_npoints) + ';')
vna.write('FORM4')
vna.write('AVERON ' + str(aver_factor))
if cal_on:
    vna.write('CORRON')
    vna.write('CALS' + str(cal_number))
else:
    vna.write('CORROFF')

# Main
for bias1, bias2 in biases:

    # Set voltage
    ps1.write('VOLT ' + str(bias1))
    ps1.write('OUTP ON')
    ps2.write('VOLT ' + str(bias2))
    ps2.write('OUTP ON')

    # Operationg point measurement
    sleep(5)
    volt1 = float(ps1.query('MEAS:VOLT?'))
    curr1 = float(ps1.query('MEAS:CURR?'))
    volt2 = float(ps2.query('MEAS:VOLT?'))
    curr2 = float(ps2.query('MEAS:CURR?'))
    opr_points = opr_points.append({'v1': bias1, 'v2': bias2, 'meas_v1': volt1, 'meas_i1': curr1, 'meas_v2': volt2, 'meas_i2': curr2}, ignore_index=True)
    opr_points.to_csv('op_csv/opr_points.csv', index=False)

    # S-parameters measurement
    for SMN in ('S11', 'S12', 'S21', 'S22'):

        vna.write('CHAN1; ' + SMN + ';')
        vna.write('CONT; OUTPDATA')
        sleep(10)
        meas = vna.read()

        # Save the mesured S-parameter as CSV
        csvpath = 'spara_csv/' + SMN + '_' + str(bias1).replace('.', '') + '_' + str(bias2).replace('.', '') + '.csv'
        with open(csvpath, 'w', encoding="utf-8") as f:
            f.write(meas)

        # Load the CSV as a numpy array
        exec('{} = {}'.format(SMN + '_ri', "np.loadtxt(csvpath, delimiter=',')"))

    # Save the numpy arrays as a touchstone
    s11 = S11_ri[:,0] + 1j * S11_ri[:,1]
    s12 = S12_ri[:,0] + 1j * S12_ri[:,1]
    s21 = S21_ri[:,0] + 1j * S21_ri[:,1]
    s22 = S22_ri[:,0] + 1j * S22_ri[:,1]
    s = np.empty((freq.npoints,2,2), dtype=complex)
    s[:,0,0] = s11
    s[:,0,1] = s12
    s[:,1,0] = s21
    s[:,1,1] = s22
    ntwk = rf.Network(s=s, frequency=freq)
    ntwk.write_touchstone(filename=str(bias1).replace('.', '')+'_'+str(bias2).replace('.', ''), dir='spara_s2p', form='ri')

# Turn off power supply
ps1.write('VOLT 0')
ps1.write('OUTP OFF')
ps2.write('VOLT 0')
ps2.write('OUTP OFF')