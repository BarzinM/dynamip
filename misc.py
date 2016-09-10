import json
import urllib.request as urlreq
import requests
from time import sleep,time
import sys

class DynamipError(Exception):
    pass


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

def touchOpen(file_name,*args,**kwargs):
    import os
    fd = os.open(file_name, os.O_RDWR | os.O_CREAT)

    # Encapsulate the low-level file descriptor in a python file object
    return os.fdopen(fd, *args, **kwargs)

def writeIPToFile(file_name, hostname, ip=None):
    if ip is None:
        my_ip = getIP()
    else:
        my_ip = ip
    with touchOpen(file_name, 'r+') as file:
        try:
            whole_data = json.load(file)
            print(whole_data)
        except ValueError:
            whole_data=dict()
            print("couldn't read")
        info = {'ip': my_ip,'mtime':time()}
        whole_data[hostname]=info
        print(whole_data)
        file.seek(0)
        json.dump(whole_data, file)
        file.truncate()


def readIPFromFile(file_name,hostname):
    with open(file_name, 'r') as ip_file:
        saved_ip = json.load(ip_file)[hostname]['ip']
    return saved_ip

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
