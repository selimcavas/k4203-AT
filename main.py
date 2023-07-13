# coding=utf-8
# ------------------------
# Author:  Selim Çavaş
# Date:    July 2023
#
# Code to execute and read AT commands for Vodafone Huawei K4203 USB Modem
# ------------------------

import serial
import time
import os

# Function to wait for the response of the modem


def waitResponse():
    response = b''
    while 'OK' not in response.decode() and 'ERROR' not in response.decode():

        response += modem.readline()
        response_str = response.decode()
        response_str = response_str[2:-2]
        print(response_str)

    time.sleep(2)

def executeATcommand(command):
    print('\nSending ' + command + ' command')
    cmd = bytes(command + '\r\n', 'utf-8')
    modem.write(cmd)
    waitResponse()

# Switch the modem to the modem mode
os.system('sudo usb_modeswitch -c /etc/k4203-modem.conf')
# Stop the ModemManager service
os.system('sudo systemctl stop ModemManager.service')
# Establish connection with the modem
modem = serial.Serial(port='/dev/ttyUSB0', baudrate=9600,
                      rtscts=True, dsrdtr=True, timeout=0.1)

print('Modem is ready!')


try:
    time.sleep(0.5)

    executeATcommand('AT')
    executeATcommand('AT^CURC=0')
    executeATcommand('AT+CNMI?')
    executeATcommand('AT+CNMI=2,0,0,2,1')
    executeATcommand('AT+CNMI?')
    executeATcommand('AT+CMGF?')

finally:
    print('Closing modem')
    modem.close()
