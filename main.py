from driveapi import getFileIdFromName, getServiceInstant, FileOnDriveError, insertFile, download_file, updateFile, getCredentials
from interpret import getIP, writeIPToFile, readIPFromFile, getHostname, getLocalIP, IPBank, Device

import argparse
from oauth2client import tools

file_name = 'Dynamip'


def echo():
    bank = IPBank()
    bank.parseFile(file_name)
    print(bank)


def hostOnly(service=None):
    from time import sleep

    if service is None:
        service = getServiceInstant()
    file_id = getFileIdFromName(service, file_name)

    bank = IPBank()
    bank.parseFile(file_name)
    this_device = Device()
    this_device.fromDevice()
    saved_states = bank.savedStates(this_device)
    while True:

        if this_device != saved_states:
            bank.updateFile(this_device)

            print("Uploading the file to Google Drive ...")
            updateFile(service, file_id, file_name)
            print("%s has been uploaded." % file_name)

            saved_states = this_device

        sleep(15)
        this_device.fromDevice()


def up():
    from time import sleep
    # service = getServiceInstant()
    # download(service)
    bank = IPBank()
    bank.parseFile(file_name)
    this_device = Device()
    this_device.fromDevice()
    saved_states = bank.savedStates(this_device)
    print("got this", saved_states)
    while True:
        # if file changed
        # download it
        # bank.parseFile()
        this_device.fromDevice()
        if this_device != saved_states:
            bank.updateFile(this_device)
            print("Uploading the file to Google Drive ...")

            # file_metadata = insertFile(service, file_name)
            # file_id = file_metadata['id']

            print("%s has been uploaded." % file_name)
            bank.parseFile()
            saved_states = bank.savedStates(this_device)
        sleep(15)


def askTunnel():
    pass


def upload(service=None):
    if service is None:
        service = getServiceInstant()

    file_metadata = insertFile(service, file_name)
    file_id = file_metadata['id']


def download(service=None):
    if service is None:
        service = getServiceInstant()

    # check see if file is online
    try:
        print("Finding file on google Drive ...")
        file_id = getFileIdFromName(service, file_name)

        # download it
        with open(file_name, 'wb+') as file_handle:
            download_file(service, file_id, file_handle)

    except FileOnDriveError as e:
        print("File could not be located on Google Drive:", e)


def generate():
    import os.path
    if os.path.isfile(file_name):
        response = input(
            'File already exist on the disk. Are you sure you want to overwrite?[y/n]:')
        if response not in ['y', 'yes', 'Y']:
            print("Aborted!")
            return
    print("Generating the file ...")
    bank = IPBank()
    device = Device()
    device.fromDevice()
    print(device)
    bank.updateFile(device, file_name)
    # writeIPToFile(file_name, hostname)

    print("Done.")


def main():
    """TODO"""

    hostname = getHostname()
    ip_public_current = getIP()
    ip_local_current = getLocalIP()
    service = getServiceInstant()

    # check see if file is online
    try:
        print("Finding file on google Drive ...")
        file_id = getFileIdFromName(service, file_name)

        # download it
        with open(file_name, 'wb+') as file_handle:
            download_file(service, file_id, file_handle)

        ip_public_saved = readIPFromFile(file_name, hostname)

        print("Done")

    except KeyError as e:
        print("An attribute could not be found in %s file: %s" % (file_name, e))
        print("Generating the file ...")

        writeIPToFile(file_name, hostname)

        print("Done.")

        print("Uploading the file to Google Drive ...")

        file_metadata = insertFile(service, file_name)
        file_id = file_metadata['id']

        print("%s has been uploaded with the id %s" % (file_name, file_id))

        ip_public_saved = ip_public_current
        ip_local_saved = ip_local_current

    except FileOnDriveError as e:
        print("File could not be located on Google Drive:", e)

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
            print("An error happend:", e)
            print("Generating the file ...")

            writeIPToFile(file_name, hostname)

            print("Done.")

            ip_public_saved = ip_public_current
            ip_local_saved = ip_local_current

        print("Uploading the file to Google Drive ...")

        file_metadata = insertFile(service, file_name)
        file_id = file_metadata['id']

        print("%s has been uploaded with the id %s" % (file_name, file_id))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.add_argument(
        "action", help='the Dynamic action to perform (e.g. `echo` or `somethingelse`.')

    args = parser.parse_args()

    if args.noauth_local_webserver:
        getCredentials(args)
        
    if args.action == "echo":
        echo()
    elif args.action == "generate":
        generate()
    elif args.action == "download":
        download()
    elif args.action == "up":
        up()
    elif args.action == "host":
        hostOnly()
    # download()
    # main()
