import json
import requests
from time import sleep, time, ctime
import sys
import subprocess
import socket
# from getAllNetworks import getInterfaceList
import warnings

def fuzzyLookup(key, word_list):
    from difflib import SequenceMatcher as sm
    max_ratio = 0.
    best_match = ""
    for ind in range(len(word_list)):
        ratio = sm(None,key,word_list[ind]).ratio()
        if ratio>max_ratio:
            max_ratio = ratio
            best_match = word_list[ind]
    return best_match



class IPBank(object):
    def __init__(self):
        self.bank = []
        self.file_name = None

    def savedStates(self, device):
        name = device.getName()
        for saved_device in self.bank:
            if name == saved_device.getName():
                return saved_device
        raise DynamipError(
            "Could not find information of the following device: %s" % device)

    def parseDict(self, dictionary):
        list_devices = []
        for key in dictionary.keys():
            device = Device(key)
            device.fromDict(dictionary[key])
            list_devices.append(device)
        self.bank = list_devices

    def parseFile(self, file_name=None):
        if file_name is None:
            if self.file_name is None:
                raise DynamipError("A file name should be specified")
            else:
                file_name = self.file_name
        else:
            self.file_name = file_name
        with open(file_name, 'r') as file:
            info = json.load(file)

        self.parseDict(info)
        return self.bank

    def updateFile(self, device, file_name=None):
        if file_name is None:
            if self.file_name is None:
                raise DynamipError("A file name should be specified")
            else:
                file_name = self.file_name
        else:
            self.file_name = file_name

        info = device.toDict()

        with touchOpen(file_name, 'r+') as file:
            file_info = json.load(file)
            file_info.update(info)
            file.seek(0)
            json.dump(file_info, file, sort_keys=True, indent=4)
            file.truncate()

        # self.parseDict(file_info)

    def __str__(self):
        text = [str(device) for device in self.bank]
        return "\n-----\n".join(text)


class interface(object):
    def __init__(self):
        self.ip = None
        self.ip_gateway = None
        self.interface_type = None  # `public`, `wlan`, or `eth`
        self.subnet_mask = None
        self.mac_address = None
        self.mac_address_gateway = None
        self.ssh_port = None
        self.tunneled = False
        self.tunnel_request_recieved = False
        self.tunneled_to = {'ip': '0.0.0.0', 'port': 22}

    def fromFile(self, file_name):
        self.ssh_port = 22  # TODO: correct this to read from file


class Device(object):

    def __init__(self, name=None):
        self.name = name
        self.networks = []
        self.ip_local = None
        self.ip_public = None
        self.port_forwarding = None
        self.local_network = [{'type': None, 'ip': None}]
        self.update_time = None

    def getName(self):
        return self.name

    def fromDevice(self):
        self.name = getHostname()
        self.ip_public = getIP()
        self.update_time = time()
        self.up_loca = getLocalIP()
        self.port_forwarding = None  # look this up from config file

    def lookup(self, key, dictionary):
        # TODO: clean up this methods
        return dictionary[key]
        try:
            return dictionary[key]
        except KeyError:
            warnings.warn(
                'Could not find the key `%s`. Returning `None`.' % key)
            return None

    def fromDict(self, dictionary):
        if self.name is None:
            raise DynamipError(
                "Device object needs a name associated with the device")
        if self.name in dictionary.keys():
            warnings.warn(
                "The dictionary provided to `Device.fromDict` seem to contain information of multiple devices!")
            print("Narrowing the information to current device")
            dictionary = dictionary[self.name]
        try:
            self.ip_public = self.lookup('ip_public', dictionary)
            self.update_time = self.lookup('update_time', dictionary)
        except KeyError as e:
            warnings.warn('%s is missing %s key.' % (self.name,e))

    def toDict(self):
        information = {}
        information[self.name] = {"ip_public": self.ip_public,
                                  "update_time": self.update_time, "local_network": self.local_network}

        return information

    def isComplete(self):
        if None in [self.name, self.ip_public, self.mtim]:
            raise DynamipError(
                "Device information is incomplete:%s" % str(self))

    def __eq__(self, other):
        equal = True
        try:
            equal &= self.name == other.name
            equal &= self.ip_public == other.ip_public
            equal &= self.ip_local == other.ip_local
            return equal
        except Exception as e:
            print("Following error happened during comparing %s and %s: %s" %
                  (e, self.name, other.name))
            return False

    def __neq__(self, other):
        equal = True
        try:
            equal &= self.name == other.name
            equal &= self.ip_public == other.ip_public
            equal &= self.ip_local == other.ip_local
            return not equal
        except Exception as e:
            print("Following error happened during comparing %s and %s: %s" %
                  (e, self.name, other.name))
            return True

    def __str__(self):

        text = ["Device name: %s" % self.name]
        if self.update_time is not None:
            text.append("- Updated @ %s" % ctime(self.update_time))
        text.append("- Public IP: %s" % self.ip_public)
        text.append("- Local Networks: %s" % self.local_network)

        text = "\n".join(text)
        return text


class DynamipError(Exception):
    pass


def getBashOutput(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()[0].decode("utf-8").rstrip()


def getSSID():
    command = "iwgetid -r"
    return getBashOutput(command)


def gatewayMacAddress():
    """wip"""
    command = "arping -f -I $(ip route show match 0/0 | awk '{print $5, $3}')"
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
        info = {'ip_public': ip_current_public, 'update_time': time()}
        # info['local_networks']=getInterfaceList()
        whole_data[hostname] = info
        file.seek(0)
        json.dump(whole_data, file, sort_keys=True, indent=4)
        file.truncate()


def readIPFromFile(file_name, hostname):
    with open(file_name, 'r') as ip_file:
        info = json.load(ip_file)[hostname]
        ip_public = info['ip_public']
        # local_network = info['local_networks']
    return ip_public, local_network


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
    # print(getHostname())
    # print(getSSID(), getLocalIP())
    # m = Device('qwer')
    # print(m)
    print(fuzzyLookup('methi',['something','nothing','somethingelse']))
