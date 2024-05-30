import os.path
import sys
import time
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

folderId=os.environ.get('folderId')

# folderId="0B4wSVIZCga2IVElQNHZqWEVEQ1k"
gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    # gauth.LocalWebserverAuth()
    gauth.CommandLineAuth()
elif gauth.access_token_expired:
# Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")

try:
    if int(sys.argv[1])>0:
        sleepTimeSeconds=min(int(sys.argv[1]), 86400)
except: 
        sleepTimeSeconds=86400


def pushToGdrive(folderId):
    testCSV = os.path.isfile('/usr/src/app/webserver/static/IBKR_Data.csv')
    if not testCSV: print(f"File not found, '/usr/src/app/webserver/IBKR_Data.csv', retrying in {sleepTimeSeconds}", file=sys.stderr); return
    testCS = os.path.isfile('/usr/src/app/client_secrets.json')
    if not testCS: print(f"File not found, '/usr/src/app/client_secrets.json', retrying in {sleepTimeSeconds}", file=sys.stderr); return
    drive=GoogleDrive(gauth)
    try:
        file_list = drive.ListFile({'q':"'"+folderId+"' in parents and title='IBKR_Data' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"}).GetList()
        file_id=file_list[0]['id']
        csvUpdate = drive.CreateFile({'id':file_id})
        csvUpdate.SetContentFile('/usr/src/app/webserver/static/IBKR_Data.csv')
        csvUpdate.Upload({'convert':True})
        print(f"File update successful on File ID: {file_id}")
    except:
        print("'IBKR_Data.csv' not found, creating..")
        csvFile = drive.CreateFile({'title':'IBKR_Data', 'parents':[{'id': f'{folderId}'}]})
        csvFile.SetContentFile('/usr/src/app/webserver/static/IBKR_Data.csv')
        csvFile.Upload({'convert':True})
        file_id=csvFile['id']
        print(f"File creation successful. File ID: {file_id}")

# call function every set number of seconds
while True:
    pushToGdrive(folderId)
    for i in range(sleepTimeSeconds,0,-1):
        print(f'Sleeping for {sleepTimeSeconds} seconds.. Press CTRL+C to end: {i:<10d}', end="\r")
        time.sleep(1)
