Dynamip (WIP)
======

### THIS IS A WORK IN PROGRESS

## Keep Track of Dynamic IP of Your Remote Devices

This is a tool that helps different devices to know each other's public IPs (static or dynamic) and also local IPs. Using this tool you can SSH into devices over internet without the need for setting up a static IP. It uses local network if the target device is accessible through local network. 

Dynamip uses Google Drive API to communicate IP values between devices. User needs to authorize the tool to connect to Google Drive.

## As of Now
You can use the file `syncIPfile.py` to try Dynamip so far:
	
	python3 syncIPfile.py

## TODO

- [ ] Finish development of main functionalities.
- [ ] SSH wrapper for forward and reverse tunneling.
- [ ] Bash scripts for: installation, setup, cronjob
- [ ] Documentation: dependencies, setup, test
- [ ] A lot more

## Contribution
Very welcome.