# 8510C-controller
This script controls a vector network analyzer 8510C and two regulated power supplies PMX35-1A. S-parameters and operating points are measured while sweeping biases. The measurement results are saved as the CSV format and the touchstone format.

# Requirements
- Keysight IO Libraries Suite (https://www.keysight.com/en/pd-1985909/io-libraries-suite?cc=US&lc=eng&jmpid=zzfindiolib)
- Python
- pyvisa (```pip install pyvisa```)
- numpy (```pip install numpy```)
- pandas (```pip install pandas```)
- scikit-rf (```pip install scikit-rf```)

# Instruments
- Hewlett-Packard 8510C
- KIKUSUI PMX35-1A (x2)

# Author
Keisuke Kawahara
