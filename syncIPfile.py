from driveapi import getFileIdFromName, getServiceInstant, updateFile, FileOnDriveError, insertFile
from misc import getIP, getChangedIP, writeIPToFile, readIPFromFile, DynamipError, getHostname
from json import dump, load


def main():
    """TODOS"""
    file_name = 'dynamip.txt'

    hostname = getHostname()
    ip = getIP()
    service = getServiceInstant()

    # check see if file is online

    try:
        saved_ip = readIPFromFile(file_name, hostname)
        if ip != saved_ip:
            print('Old IP was', saved_ip,'and current one is',ip)
            writeIPToFile(file_name, hostname)
    except (KeyError,ValueError) as e:
        print(e)
        writeIPToFile(file_name,hostname,ip)
    except FileNotFoundError:
        try:
            file_id = getFileIdFromName(service, file_name)
        except FileOnDriveError:
            writeIPToFile(file_name,hostname,ip)
        # Download file
        # writeIPToFile(file_name, hostname,ip)
        # saved_ip = ip
        # print("Could not get the old IP from %s. Uploading the new IP to the file."%ip)


    try:
        file_id = getFileIdFromName(service, file_name)
        print("%s file found on Google Drive with ID %s"%(file_name,file_id))
    except FileOnDriveError:
        print("File %s could not be located on the drive. Creating ..."%file_name)
        file_metadata = insertFile(service, file_name)
        file_id = file_metadata['id']
        print("%s has been created with the id %s"%(file_name,file_id))

    #     metadata = updateFile(service, file_id, file_name)
    #     print(metadata)
    #     dump(metadata, file)
    # while True:
    #     ip = getChangedIP(.3)
    #     writeIPToFile(file_name)
    #     metadata = updateFile(service, file_id, file_name)
    #     print(metadata)
    #     dump(metadata, file)

if __name__ == '__main__':
    main()
