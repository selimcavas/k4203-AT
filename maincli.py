# coding=utf-8
# ------------------------
# Author:  Selim Çavaş
# Date:    July 2023
# CLI Version
# Code to execute and read AT commands for Vodafone Huawei K4203 USB Modem
# ------------------------

import cmd
import sys
import serial
import time
import os
import re
import pprint
from smspdudecoder.fields import SMSDeliver
from io import StringIO


def wait_response(hideOut = False):
    response = b''
    while 'OK' not in response.decode() and 'ERROR' not in response.decode() and not response.decode().strip().endswith('>'):
        response += modem.readline()
        response_str = response.decode()
        response_str = response_str[2:-2]

    if not hideOut:
        print(response.decode())
    time.sleep(0.5)
    return response

def execute_AT_command(command, hideOut = False):
    if not hideOut:
        print(command)
    
    if not command.startswith('AT'):
        print('Error: Command must start with "AT"\n')
        return b''
    
    cmd = bytes(command + '\r\n', 'utf-8')
    modem.write(cmd)
    response = wait_response(hideOut=hideOut)
    return response

# Function to provide SMS info from a response string
def provide_sms_info(response_str, sender_number = None):
    pdu_list = []
    for match in re.findall(r'\+CMGL:.*?\n([0-9A-Fa-f]+)', response_str):
        pdu_list.append(match)

    if(len(pdu_list) == 0):
        print("No SMS available \n")
        return
    
    print("SMS PDU's are: \n")
    pprint.pprint(pdu_list)
    

    print("SMS info: \n")
    print_SMS(pdu_list, sender_number)

# Function to get the unread SMS PDU's
def get_unread_SMS_PDU(sender_number = None):
    execute_AT_command('AT+CMGF=0')
    response = execute_AT_command('AT+CMGL=0')
    response_str = response.decode()
    
    provide_sms_info(response_str, sender_number)

# Function to get all SMS PDU's
def get_all_SMS_PDU(sender_number = None):
    execute_AT_command('AT+CMGF=0')
    response = execute_AT_command('AT+CMGL=4')
    response_str = response.decode()

    provide_sms_info(response_str, sender_number)

# Function to print SMS PDU fields in a pretty way
def print_SMS(pdu_list, sender_number = None):
    pprint.pprint(pdu_list)
    for pdu in pdu_list:
        try:
            sms_data = SMSDeliver.decode(StringIO(pdu))
        except:
            print("Warning: Can't read the SMS PDU of sent messages but you can select it from the pdu list and convert it online  \n")
            return

        if(sms_data["sender"]["number"] == sender_number or sender_number == None):
            pprint.pprint(sms_data)
            print('\n')

def execute_text_SMS(recipient_number, message):
    # Set the modem to text mode
    execute_AT_command('AT+CMGF=1')
    time.sleep(0.5)
    # Set the recipient number
    execute_AT_command(f'AT+CMGW="{recipient_number}"')

    # Send the message and Ctrl+Z character
    cmd = bytes(message + '\x1A', 'utf-8')
    modem.write(cmd)
    
    response = wait_response()

    response_str = response.decode()
    number = re.findall(r'\+CMGW: (\d+)', response_str)
    print(number)
    execute_AT_command(f'AT+CMSS={number[0]}')


def execute_pdu_SMS(cmgs_number, pdu_message):
    # Set the modem to PDU mode
    execute_AT_command('AT+CMGF=0')
    time.sleep(0.5)
    # Set the CMGS number
    execute_AT_command(f'AT+CMGS={cmgs_number}')

    # Send the message and Ctrl+Z character
    cmd = bytes(pdu_message + '\x1A', 'utf-8')
    modem.write(cmd)
    
    response = wait_response()

cmdargs = False
len_cmdargs = len(sys.argv)
option = ''

if len_cmdargs > 1:
        cmdargs = True
        option = sys.argv[1]

if option == "s" or not cmdargs:
     # Move the modem config file to the /etc/ directory
    if not (os.path.exists('/etc/k4203-modem.conf')):
        print('Modem config file not found!')
        os.system('sudo mv k4203-modem.conf /etc/')
    else:
        print('Modem config file found!')
    # Switch the modem to the modem mode
    os.system('sudo usb_modeswitch -c /etc/k4203-modem.conf')
    # Stop the ModemManager service
    os.system('sudo systemctl stop ModemManager.service')
    # Establish connection with the modem
    modem = serial.Serial(port='/dev/ttyUSB0', baudrate=9600,
                        rtscts=True, dsrdtr=True, timeout=0.1)

    print('Modem is ready!')
    execute_AT_command('AT')
    execute_AT_command('AT^CURC=0')
    execute_AT_command('AT+CNMI=2,0,0,2,1')
    execute_AT_command('AT+CMGF=0')
    print('Setup done! \n')

# Establish connection with the modem
modem = serial.Serial(port='/dev/ttyUSB0', baudrate=9600,
                        rtscts=True, dsrdtr=True, timeout=0.1)
time.sleep(0.5)
os.system('clear')

while True:
    # list options for the user
    if not cmdargs:
        print('------------------------')
        print('Select an option: \n')
        print('1. Execute AT command')
        print('2. Get all SMS PDU\'s')
        print('3. Get unread SMS PDU\'s')
        print('4. Send text SMS')
        print('5. Send PDU SMS')
        print('6. Clear screen')
        print('7. Exit')
        print('\n')
        option = input('Enter your option (1-7): ')

    if len(option) != 1 or option not in ['1', '2', '3', '4', '5', '6', '7', 's']:
        print('Invalid option!')
        continue

    if option == '1':
        if len_cmdargs > 2:
            command = sys.argv[2]
        else:
            command = input('Enter the command: ')
        execute_AT_command(command)

    if option == '2':
        get_all_SMS_PDU()

    elif option == '3':
        get_unread_SMS_PDU()

    elif option == '4':
        if len_cmdargs > 2:
            recipient_number = sys.argv[2]
            message = sys.argv[3]
        else:
            recipient_number = input('Enter the recipient number: ')
            message = input('Enter the message: ')
        execute_text_SMS(recipient_number, message)

    elif option == '5':
        if len_cmdargs > 2:
            cmgs_number = sys.argv[2]
            pdu_message = sys.argv[3]
        else:
            cmgs_number = input('Enter the CMGS number: ')
            pdu_message = input('Enter the PDU message: ')
        execute_pdu_SMS(cmgs_number, pdu_message)

    elif option == '6':
        os.system('clear')

    elif option == '7':
        break

    if cmdargs:
        break
    
