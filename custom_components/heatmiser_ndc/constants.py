#
# Neil Trimboy 2011
#

import serial

# Define magic numbers used in messages
FUNC_READ = 0
FUNC_WRITE = 1

# COMM SETTINGS

COM_PORT = 6  # 1 less than com port, USB is 6=com7, ether is 9=10
COM_BAUD = 4800
COM_SIZE = serial.EIGHTBITS
COM_PARITY = serial.PARITY_NONE
COM_STOP = serial.STOPBITS_ONE
COM_TIMEOUT = 0.8
