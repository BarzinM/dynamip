import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from apiclient import errors
from apiclient.http import MediaFileUpload, MediaIoBaseDownload

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
# SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
SCOPES = 'https://www.googleapis.com/auth/drive.file'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


class FileOnDriveError(Exception):
    pass


def getFileIdFromName(service, file_name):
    results = service.files().list().execute()
    items = results.get('items', [])
    for item in items:
        # print(item['title'])
        if item['title'] == file_name:
            return item['id']
    raise FileOnDriveError("File %s was not found on Google Drive" % file_name)


def updateFile(service, file_id, filename, new_title=None, new_description=None, new_mime_type=None, new_revision=True):
    """Update an existing file's metadata and content.

    Args:
      service: Drive API service instance.
      file_id: ID of the file to update.
      new_title: New title for the file.
      new_description: New description for the file.
      new_mime_type: New MIME type for the file.
      filename: Filename of the new content to upload.
      new_revision: Whether or not to create a new revision for this file.
    Returns:
      Updated file metadata if successful, None otherwise.
    """
    try:
        # First retrieve the file from the API.
        file = service.files().get(fileId=file_id).execute()

        # File's new metadata.
        if new_title is not None:
            file['title'] = new_title
        if new_description is not None:
            file['description'] = new_description
        if new_mime_type is not None:
            file['mimeType'] = new_mime_type

        # File's new content.
        media_body = MediaFileUpload(
            filename, mimetype=file['mimeType'], resumable=True)

        # Send the request to the API.
        updated_file = service.files().update(
            fileId=file_id,
            body=file,
            newRevision=new_revision,
            media_body=media_body).execute()
        return updated_file
    except errors.HttpError:
        print('An error occurred.')
        raise
        return None


def insertFile(service, filename, title=None, description='', parent_id=[]):
    """Insert new file.

    Args:
      service: Drive API service instance.
      title: Title of the file to insert, including the extension.
      description: Description of the file to insert.
      parent_id: Parent folder's ID.
      mime_type: MIME type of the file to insert.
      filename: Filename of the file to insert.
    Returns:
      Inserted file metadata if successful, None otherwise.
    """
    mime_type = '*/*'
    try:
        media_body = MediaFileUpload(
            filename, mimetype=mime_type, resumable=True)
    except Exception as e:
        raise
    if title is None:
        title = filename
    body = {
        'title': title,
        'description': description,
        'mimeType': mime_type
    }
    # Set the parent folder.
    if parent_id:
        body['parents'] = [{'id': parent_id}]

    try:
        file = service.files().insert(
            body=body,
            media_body=media_body).execute()

        # Uncomment the following line to print the File ID
        # print('File ID: %s' % file['id'])

        return file
    except errors.HttpError as e:
        print('An error occured.', e)
        raise
        return None

def download_file(service, file_id, local_fd):
  """Download a Drive file's content to the local filesystem.

  Args:
    service: Drive API Service instance.
    file_id: ID of the Drive file that will downloaded.
    local_fd: io.Base or file object, the stream that the Drive file's
        contents will be written to.
  """
  request = service.files().get_media(fileId=file_id)
  media_request = MediaIoBaseDownload(local_fd, request)

  while True:
    try:
      download_progress, done = media_request.next_chunk()
    except errors.HttpError as error:
      print('An error occurred: %s' % error)
      return
    if download_progress:
      print('Download Progress: %d%%' % int(download_progress.progress() * 100))
    if done:
      print('Download Complete')
      return

def print_file_content(service, file_id):
  """Print a file's content.

  Args:
    service: Drive API service instance.
    file_id: ID of the file.

  Returns:
    File's content if successful, None otherwise.
  """
  try:
    print(service.files().get_media(fileId=file_id).execute())
  except errors.HttpError as error:
    print('An error occurred: %s' % error)

def getCredentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        try:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        except oauth2client.clientsecrets.InvalidClientSecretsError:
            raise oauth2client.clientsecrets.InvalidClientSecretsError(
                "The client secret file couldn't be found. Go to: https://developers.google.com/drive/v3/web/quickstart/python")

        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def uploadFileToDrive(filename, drive_filename=None, description='', parents=[], save_metadata=False):
    if drive_filename is None:
        drive_filename = filename

    credentials = getCredentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)
    metadata = insertFile(service, filename, 'dynamip_title',
                          'TEMP TEMP TEMP dynamic app info', [])
    print('Metadata of', filename, ':\n', metadata)
    return metadata


def downloadFile(file_id):
    # file_id = '0BwwA4oUTeiV1UVNwOHItT0xfa2M'
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))


def printFilesList(service, number_of_results=10):
    results = service.files().list(maxResults=number_of_results).execute()
    items = results.get('items', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            try:
                print('{0} ({1})'.format(item['title'], item['id']))
            except Exception:
                raise
                # print(e)


def getServiceInstant():
    credentials = getCredentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)
    return service


def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    # service = getServiceInstant()
    # # insertFile(service, 'dynamip.conf')
    # file_id = getFileIdFromName(service, 'dynamip.conf')
    # metadata = updateFile(service, file_id, 'dynamip.conf')
    # print(metadata)
    # file = open('metadata_of_updated_dynamip_file', 'w')
    # json.dump(metadata, file)
    # file.write(file)
    # results = service.files().list(maxResults=10).execute()
    # items = results.get('items', [])
    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     for item in items:
    #         try:
    #             print('{0} ({1})'.format(item['title'], item['id']))
    #         except Exception, e:
    #             print(e)

if __name__ == '__main__':
    main()
