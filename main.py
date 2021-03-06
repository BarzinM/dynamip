#!/usr/bin/python3
import argparse
import driveapi

from driveapi import getFileIdFromName, getServiceInstant, FileOnDriveError, insertFile, download_file, getCredentials
from interpret import getIP, writeIPToFile, readIPFromFile, getHostname, getLocalIP, IPBank, Device, getBashOutput
from oauth2client import tools
from lib.tool_box_dev_text.dev_and_text_tools import setupLogger


file_name = 'Dynamip'


def echo(service=None, name=None):
    bank = IPBank()
    try:
        bank.parseFile(file_name)
    except FileNotFoundError:
        print("File could not be located on the disk.")
        try:
            if service is None:
                service = getServiceInstant()
            getFileIdFromName(service, file_name)
            response = input('Do you want to download it from Drive?[y/n]:')
            if response in ['y', 'Y', 'yes']:
                download()

        except FileOnDriveError:
            response = input('Do you want to generate a new file?[y/n]:')
            if response in ['y', 'Y', 'yes']:
                generate()
    if name is None:
        print(bank)
    else:
        print(bank.savedStates(name))


def hostOnly(service=None):
    from time import sleep

    if service is None:
        service = getServiceInstant()
    file_id = download(service)

    bank = IPBank()
    bank.parseFile(file_name)
    this_device = Device()
    this_device.fromDevice()
    saved_states = bank.savedStates(this_device)
    while True:

        if this_device != saved_states:
            bank.updateFile(this_device)

            print("Uploading the file to Google Drive ...")
            driveapi.updateFile(service, file_id, file_name)
            print("%s has been uploaded." % file_name)

            saved_states = this_device

        sleep(15)
        this_device.fromDevice()


def up(service=None):
    from time import sleep

    if service is None:
        service = getServiceInstant()
    file_id = download(service)

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
        if this_device != saved_states:
            bank.updateFile(this_device)
            print("Uploading the file to Google Drive ...")
            driveapi.updateFile(service, file_id, file_name)
            print("%s has been uploaded." % file_name)
        sleep(15)
        download(service)
        this_device.fromDevice()
        bank.parseFile()
        saved_states = bank.savedStates(this_device)


def askTunnel():
    pass


def upload(service=None):
    if service is None:
        service = getServiceInstant()

    file_metadata = insertFile(service, file_name)
    file_id = file_metadata['id']
    return file_id


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

        return file_id
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


def ssh(name, port):
    import os
    bank = IPBank()
    bank.parseFile(file_name)
    dev = bank.savedStates(name)
    ip = dev.ip_public
    os.execvp('ssh', ['ssh', ip, '-l', name, '-p', str(port)])


def ping(name):
    import os
    bank = IPBank()
    bank.parseFile(file_name)
    dev = bank.savedStates(name)
    ip = dev.ip_public
    os.execvp('ping', ['ping', ip])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.add_argument('-l', '--log', action='store_true', dest='l')
    parser.add_argument('-v', '--verbose', action='store_true', dest='v')

    subparsers = parser.add_subparsers(dest='cmd')

    parse_ssh = subparsers.add_parser('ssh', description='ssh desc', help='ssh help')
    parse_ssh.add_argument('name', type=str)
    parse_ssh.add_argument('-p', '--port', type=int, default=22)

    parse_echo = subparsers.add_parser('echo', description='echo desc', help='echo help')
    parse_echo.add_argument('name', nargs='?')

    parse_ping = subparsers.add_parser('ping', description='ping desc', help='ping help')

    parse_ping.add_argument('name', type=str)

    args = parser.parse_args()

    if args.noauth_local_webserver:
        getCredentials(args)

    if args.l is True:
        logger = setupLogger(True, 'dynamip_logger', True)

    verbose = args.v

    if args.cmd == 'echo':
        echo(name=args.name)
    elif args.cmd == 'up':
        up()
    elif args.cmd == 'host':
        hostOnly()
    elif args.cmd == 'ssh':
        ssh(args.name, args.port)
    elif args.cmd == 'download':
        download()
    elif args.cmd == 'generate':
        generate()
    elif args.cmd == 'upload':
        upload()
    elif args.cmd == 'ping':
        ping(args.name)
    else:
        print('Unknown command!')
