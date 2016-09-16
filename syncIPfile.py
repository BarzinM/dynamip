from driveapi import getFileIdFromName, getServiceInstant, updateFile, FileOnDriveError, insertFile
from misc import getIP, getChangedIP, writeIPToFile, readIPFromFile, DynamipError, getHostname, getLocalIP, getHostname
from json import dump, load


def main():
    """TODOS"""
    file_name = 'Dynamip'

    hostname = getHostname()
    ip_public_current = getIP()
    ip_local_current = getLocalIP()
    service = getServiceInstant()

    # check see if file is online
    try:
        print("Finding file on google Drive ...")
        file_id = getFileIdFromName(service, file_name)
        # download it
        # download .........
        ip_public_saved = readIPFromFile(file_name, hostname)
        print("Done")
    except KeyError as e:
        print("An attribute could not be found in %s file: %s" % (file_name, e))
        print("Generating the file ...")
        writeIPToFile(file_name, hostname)
        print("Done.")
        ip_public_saved = ip_public_current
        ip_local_saved = ip_local_current
    except FileOnDriveError:
        print("File could not be located on Google Drive.")
        # check see if it exists locally
        try:
            print("Looking for the file on disk ...")
            ip_public_saved, ip_local_saved = readIPFromFile(
                file_name, hostname)
            print("Found it.")
            if ip_public_current != ip_public_saved or ip_local_current != ip_local_saved:
                print('Old IP was', ip_public_saved,
                      'and current one is', ip_public_current)
                writeIPToFile(file_name, hostname)
        except (FileNotFoundError, KeyError) as e:
            print(e)
            print("Generating the file ...")
            writeIPToFile(file_name, hostname)
            print("Done.")
            ip_public_saved = ip_public_current
            ip_local_saved = ip_local_current
        print("Uploading the file to Google Drive ...")
        file_metadata = insertFile(service, file_name)
        file_id = file_metadata['id']
        print("%s has been uploaded with the id %s" % (file_name, file_id))

    # while True:
    #     ip_public_current = getChangedIP(.3)
    #     writeIPToFile(file_name)
    #     metadata = updateFile(service, file_id, file_name)
    #     print(metadata)
    #     dump(metadata, file)

if __name__ == '__main__':
    main()
