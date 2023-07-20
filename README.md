# Vodafone Huawei K4203 USB Modem AT Command Interface

This is a program that allows you to execute and read AT commands for the Vodafone Huawei K4203 USB Modem. The program is written in Python and uses the `serial` library to communicate with the modem. For headless execution use `maincli.py` and for the GUI version use `main.py` file.

## Usage

To use the program, you need to have Python 3 installed on your computer. You also need to connect the Vodafone Huawei K4203 USB Modem to your computer via USB.

1. Clone or download the repository to your computer.
2. `sudo nano /etc/usb_modeswitch.conf` and set DisableSwitching flag to 1.
3. Open a terminal or command prompt and navigate to the directory where the program is located.
4. Run the program by typing `python3 maincli.py` or `python3 main.py` and pressing Enter.
5. Follow the on-screen instructions to select an option and enter any required parameters.


## Features

The program provides the following features:

- Execute AT commands: You can enter any AT command and the program will send it to the modem and display the response.
- Get all SMS PDU's: You can retrieve all SMS PDU's stored on the modem and display their information.
- Get unread SMS PDU's: You can retrieve only the unread SMS PDU's stored on the modem and display their information.
- Send text SMS: You can send a text SMS to a recipient by entering their phone number and the message.
- Send PDU SMS: You can send a PDU SMS to a recipient by entering the CMGS number and the PDU message.
