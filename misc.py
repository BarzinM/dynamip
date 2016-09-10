from json import load, dump
from urllib2 import urlopen
from time import sleep


def getIP():
    my_ip = load(urlopen('https://api.ipify.org/?format=json'))['ip']
    return my_ip


def returnIP():
    my_ip = load(urlopen('http://httpbin.org/ip'))['origin']
    return my_ip


def writeIPToFile(filename):
    my_ip = getIP()
    file = open(filename, 'w')
    info = {'ip': my_ip}
    dump(info, file)


def getChangedIP(minutes=15):
    my_ip = getIP()
    while True:
        sleep(minutes * 60)
        try:
            new_ip = getIP()
        except Exception, e:
            raise e
        if my_ip != new_ip:
            print 'IP changed from', my_ip, 'to', new_ip
            break
    return new_ip

if __name__ == '__main__':
    while True:
        ip = getChangedIP(.3)
        writeIPToFile('dynamip.conf')
