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
import re
import pprint
import tkinter as tk
from smspdudecoder.fields import SMSDeliver
from io import StringIO


# Function to wait for the response of the modem
def wait_response():
    response = b''
    while 'OK' not in response.decode() and 'ERROR' not in response.decode():
        response += modem.readline()
        response_str = response.decode()
        response_str = response_str[2:-2]

    print(response.decode())
    time.sleep(0.5)
    return response

# Function to execute AT commands
def execute_AT_command(command):
    print(command)
    output_text.insert(tk.END, "\n"+command)
    cmd = bytes(command + '\r\n', 'utf-8')
    modem.write(cmd)
    response = wait_response()
    output_text.insert(tk.END, response.decode() + '\n')
    return response

# Function to provide SMS info from a response string
def provide_sms_info(response_str, sender_number = None):
    pdu_list = []
    for match in re.findall(r'\+CMGL:.*?\n([0-9A-Fa-f]+)', response_str):
        pdu_list.append(match)

    if(len(pdu_list) == 0):
        print("No SMS available \n")
        output_text.insert(tk.END, "No SMS available \n")
        return
    
    print("SMS PDU's are: \n")
    output_text.insert(tk.END, "SMS PDU's are: \n")
    pprint.pprint(pdu_list)
    output_text.insert(tk.END, "\n" + pprint.pformat(pdu_list) + "\n")
    print('\n')

    print("SMS info: \n")
    output_text.insert(tk.END, "\nSMS info: \n")
    print_SMS(pdu_list, sender_number)

# Function to get the unread SMS PDU's
def get_unread_SMS_PDU(sender_number = None):
    response = execute_AT_command('AT+CMGL=0')
    response_str = response.decode()
    
    provide_sms_info(response_str, sender_number)

# Function to get all SMS PDU's
def get_all_SMS_PDU(sender_number = None):
    response = execute_AT_command('AT+CMGL=4')
    response_str = response.decode()

    provide_sms_info(response_str, sender_number)

# Function to print SMS PDU fields in a pretty way
def print_SMS(pduList, sender_number = None):
    for pdu in pduList:
        sms_data = SMSDeliver.decode(StringIO(pdu))
        if(sms_data["sender"]["number"] == sender_number or sender_number == None):
            pprint.pprint(sms_data)
            output_text.insert(tk.END, pprint.pformat(sms_data) + '\n')
            print('\n')

# Switch the modem to the modem mode
os.system('sudo usb_modeswitch -c /etc/k4203-modem.conf')
# Stop the ModemManager service
os.system('sudo systemctl stop ModemManager.service')
# Establish connection with the modem
modem = serial.Serial(port='/dev/ttyUSB0', baudrate=9600,
                      rtscts=True, dsrdtr=True, timeout=0.1)

print('Modem is ready!')

# Create the Tkinter GUI
root = tk.Tk()
root.title('AT Command Tester')

user_input = tk.StringVar(root)

input_frame = tk.Frame(root)
input_frame.pack(side=tk.TOP, pady=10)

at_label = tk.Label(input_frame, text='Enter AT command:')
at_label.pack(side=tk.LEFT, padx=5)

# Create the command entry field
command_entry = tk.Entry(input_frame, width=30, textvariable=user_input)
command_entry.pack(side=tk.LEFT, padx=5)

command_entry.bind('<Return>', lambda event: execute_AT_command(user_input.get() if user_input.get() != '' else 'AT'))

# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.pack(side=tk.TOP, pady=10)

# Create the execute button
execute_button = tk.Button(button_frame, text='Execute', command= lambda: execute_AT_command(user_input.get() if user_input.get() != '' else 'AT'))
execute_button.pack(side=tk.LEFT, padx=5)

# Create the get unread SMS button
get_unread_SMS_button = tk.Button(button_frame, text='Get Unread SMS', command= lambda: get_unread_SMS_PDU())
get_unread_SMS_button.pack(side=tk.LEFT, padx=5)

# Create the get all SMS button
get_all_SMS_button = tk.Button(button_frame, text='Get All SMS', command= lambda: get_all_SMS_PDU())
get_all_SMS_button.pack(side=tk.LEFT, padx=5)
# Create the output text box
output_text = tk.Text(root, width=300, height=200)
output_text.pack(side=tk.BOTTOM, pady=20)


execute_AT_command('AT')
execute_AT_command('AT^CURC=0')
execute_AT_command('AT+CNMI=2,0,0,2,1')
execute_AT_command('AT+CMGF=0')

# Start the Tkinter event loop
root.mainloop()


