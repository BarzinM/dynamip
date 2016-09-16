import json
import urllib.request as urlreq
import requests
from time import sleep, time
import sys
import subprocess
import socket


class DynamipError(Exception):
    pass


def getBashOutput(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()[0].decode("utf-8").rstrip()


def getSSID():
    command = "iwgetid -r"
    return getBashOutput(command)


def getLocalIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def ipFromIpify():
    URL = 'https://api.ipify.org/?format=json'
    response = requests.get(URL)
    data = json.loads(response.text)
    my_ip = data['ip']
    return my_ip


def ipFromHttpbin():
    URL = 'http://httpbin.org/ip'
    response = requests.get(URL)
    data = json.loads(response.text)
    my_ip = data['origin']
    return my_ip


def getIP():
    try:
        return ipFromIpify()
    except:
        print(sys.exc_info()[0])
    try:
        return ipFromHttpbin()
    except:
        print(sys.exc_info()[0])
    return sys.exc_info()[0]


def getHostname():
    import socket
    return socket.gethostname()


def touchOpen(file_name, *args, **kwargs):
    import os
    fd = os.open(file_name, os.O_RDWR | os.O_CREAT)

    # Encapsulate the low-level file descriptor in a python file object
    return os.fdopen(fd, *args, **kwargs)


def writeIPToFile(file_name, hostname):
    
    ip_current_public = getIP()
    ip_current_local = getLocalIP()

    with touchOpen(file_name, 'r+') as file:
        try:
            whole_data = json.load(file)
        except ValueError:
            whole_data = dict()
        info = {'ip_public': ip_current_public,'local_networks':ip_current_local, 'ssid':getSSID(), 'mtime': time()}
        whole_data[hostname] = info
        file.seek(0)
        json.dump(whole_data, file, sort_keys=True, indent=4)
        file.truncate()


def readIPFromFile(file_name, hostname):
    with open(file_name, 'r') as ip_file:
        info = json.load(ip_file)[hostname]
        ip_public = info['ip_public']
        ip_local = info['local_networks']
    return ip_public, ip_local


def getChangedIP(minutes=15):
    my_ip = getIP()
    while True:
        sleep(minutes * 60)
        try:
            new_ip = getIP()
        except:
            raise
        if my_ip != new_ip:
            print('IP changed from', my_ip, 'to', new_ip)
            break
    return new_ip

if __name__ == '__main__':
    print(getHostname())
    print(getSSID(), getLocalIP())
