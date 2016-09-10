from driveapi import getFileIdFromName, getServiceInstant, updateFile
from misc import getIP, getChangedIP, writeIPToFile
from json import dump, load


def main():
    """TODOS"""

    # service = getServiceInstant()
    # file_id = getFileIdFromName(service, 'dynamip.conf')
    # file = open('dynamip_metadata', 'w')
    ip = getIP()
    print 'Public IP is', ip
    with open('dynamip.conf') as ip_file:
        try:
            saved_ip = load(ip_file)['ip']
        except Exception,e:
            saved_ip=''
            print e
    if ip != saved_ip:
        print 'Old IP was', saved_ip
        writeIPToFile('dynamip.conf')
    #     metadata = updateFile(service, file_id, 'dynamip.conf')
    #     print metadata
    #     dump(metadata, file)
    while True:
        ip = getChangedIP(.3)
        writeIPToFile('dynamip.conf')
    #     metadata = updateFile(service, file_id, 'dynamip.conf')
    #     print metadata
    #     dump(metadata, file)

if __name__ == '__main__':
    main()
