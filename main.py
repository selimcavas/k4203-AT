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


def wait_response():
    response = b''
    while 'OK' not in response.decode() and 'ERROR' not in response.decode() and not response.decode().strip().endswith('>'):
        response += modem.readline()
        response_str = response.decode()
        response_str = response_str[2:-2]

    print(response.decode())
    time.sleep(0.5)
    return response

def execute_AT_command(command):
    print(command)
    
    if not command.startswith('AT'):
        output_text.insert(tk.END, 'Error: Command must start with "AT"\n')
        command_entry.delete(0, tk.END)
        return b''
    
    output_text.insert(tk.END, "\n"+command)
    cmd = bytes(command + '\r\n', 'utf-8')
    modem.write(cmd)
    response = wait_response()
    output_text.insert(tk.END, response.decode() + '\n')
    command_entry.delete(0, tk.END)
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
            output_text.insert(tk.END, "Warning: Can't read the SMS PDU of sent messages but you can select it from the pdu list and convert it online \n")
            return

        if(sms_data["sender"]["number"] == sender_number or sender_number == None):
            pprint.pprint(sms_data)
            output_text.insert(tk.END, pprint.pformat(sms_data) + '\n')
            print('\n')

# Function to send SMS in text mode
def send_text_SMS():
    # Create the popup window
    popup_window = tk.Toplevel(root)
    popup_window.title('Send SMS in Text Mode')

    # Create the recipient number label and entry field
    recipient_label = tk.Label(popup_window, text='Recipient Number:')
    recipient_label.pack(side=tk.TOP, pady=5)
    recipient_entry = tk.Entry(popup_window, width=30)
    recipient_entry.pack(side=tk.TOP, pady=5)

    # Create the text message label and entry field
    message_label = tk.Label(popup_window, text='Text Message:')
    message_label.pack(side=tk.TOP, pady=5)
    message_entry = tk.Entry(popup_window, width=30)
    message_entry.pack(side=tk.TOP, pady=5)

    # Create the submit button
    submit_button = tk.Button(popup_window, text='Send', command= lambda: [execute_text_SMS(recipient_entry.get(), message_entry.get()), popup_window.destroy()])
    submit_button.pack(side=tk.TOP, pady=5)

    # Center the popup window on the screen
    popup_window.update_idletasks()
    width = popup_window.winfo_width()
    height = popup_window.winfo_height()
    x = (popup_window.winfo_screenwidth() // 2) - (width // 2)
    y = (popup_window.winfo_screenheight() // 2) - (height // 2)
    popup_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

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
    output_text.insert(tk.END, response.decode() + '\n')
    
    response_str = response.decode()
    number = re.findall(r'\+CMGW: (\d+)', response_str)
    print(number)
    execute_AT_command(f'AT+CMSS={number[0]}')

# Function to send SMS in PDU mode
def send_pdu_SMS():
    # Create the popup window
    popup_window = tk.Toplevel(root)
    popup_window.title('Send SMS in PDU Mode')

    # Create the CMGS number label and entry field
    cmgs_label = tk.Label(popup_window, text='CMGS Number:')
    cmgs_label.pack(side=tk.TOP, pady=5)
    cmgs_entry = tk.Entry(popup_window, width=30)
    cmgs_entry.pack(side=tk.TOP, pady=5)

    # Create the PDU message label and entry field
    pdu_label = tk.Label(popup_window, text='PDU Message:')
    pdu_label.pack(side=tk.TOP, pady=5)
    pdu_entry = tk.Entry(popup_window, width=30)
    pdu_entry.pack(side=tk.TOP, pady=5)

    # Create the submit button
    submit_button = tk.Button(popup_window, text='Send', command= lambda: [execute_pdu_SMS(cmgs_entry.get(), pdu_entry.get()), popup_window.destroy()])
    submit_button.pack(side=tk.TOP, pady=5)

    # Center the popup window on the screen
    popup_window.update_idletasks()
    width = popup_window.winfo_width()
    height = popup_window.winfo_height()
    x = (popup_window.winfo_screenwidth() // 2) - (width // 2)
    y = (popup_window.winfo_screenheight() // 2) - (height // 2)
    popup_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

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
    output_text.insert(tk.END, response.decode() + '\n')


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

# Create the send text SMS button
send_text_SMS_button = tk.Button(button_frame, text='Send Text SMS', command= lambda: send_text_SMS())
send_text_SMS_button.pack(side=tk.LEFT, padx=5)

# Create the send PDU SMS button
send_pdu_SMS_button = tk.Button(button_frame, text='Send PDU SMS', command= lambda: send_pdu_SMS())
send_pdu_SMS_button.pack(side=tk.LEFT, padx=5)

# Create the clear output button
clear_output_button = tk.Button(button_frame, text='Clear', command= lambda: output_text.delete(1.0, tk.END))
clear_output_button.pack(side=tk.LEFT, padx=5)

# Create the output text box
output_text = tk.Text(root, width=300, height=200)
output_text.pack(side=tk.BOTTOM, pady=20)

output_text.insert(tk.END, "Executing default setup commands to recieve SMS in PDU mode... \n")
output_text.insert(tk.END, "Run AT+CMGF=1 to listen in text mode. \n")
execute_AT_command('AT')
execute_AT_command('AT^CURC=0')
execute_AT_command('AT+CNMI=2,0,0,2,1')
execute_AT_command('AT+CMGF=0')
output_text.insert(tk.END, "Setup done, you can start executing AT commands!\n")


# Start the Tkinter event loop
root.mainloop()


