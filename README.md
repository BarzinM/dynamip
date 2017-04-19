Dynamip (WIP)
======

### THIS IS A WORK IN PROGRESS

## Keep Track of Dynamic IP of Your Remote Devices

This is a tool that helps different devices to know each other's public IPs (static or dynamic) and also local IPs. Using this tool you can SSH into devices over Internet without the need for setting up a static IP. It uses local network if the target device is accessible through local network. 

Dynamip uses Google Drive API to communicate IP values between devices. User needs to authorize the tool to connect to Google Drive.

## As of Now
You can use the file `main.py` to try Dynamip so far:
	
	python3 main.py generate # to generate a sample data file
    python3 main.py upload # to upload the device info to cloud
    python3 main.py download # to download info of all devices
    python3 main.py echo # to echo all the informations available on the disk from last download
    python3 main.py ssh <remote computer name> <login name> [-p/--port <port number>] # to ssh into the remote device
    python3 main.py ping <remote computer name> # to ping the remote device

## Contribution
Very welcome.