import os.path
import sys
import pytz
import datetime
import smtplib
from email.mime.text import MIMEText
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from cryptography.fernet import Fernet

folderId= os.environ.get('folderId')
csvFileName = os.environ.get('csvFileName')
gmailAppPassword = os.environ.get('gmailAppPassword')
gmailAppPasswordKey = os.environ.get('gmailAppPasswordKey')
gmailUserName = os.environ.get('gmailUserName')
gmailRecipient = os.environ.get('gmailRecipient')
if csvFileName == None: csvFileName = 'IBKR_Data'
sleepTimeSeconds=int(os.environ.get('refreshPushSeconds'))
if sleepTimeSeconds == None: sleepTimeSeconds = 60


if gmailAppPasswordKey != None:
    def decodeGmailAppPassword():
        b=Fernet(gmailAppPasswordKey)
        pw=bytes(gmailAppPassword, "utf-8")
        decoded_pw = b.decrypt(pw)
        return str(decoded_pw, 'UTF-8')
    gmailAppPassword = decodeGmailAppPassword()


def sendEmail(sender, recipient, subject, body, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.ehlo()
        smtp_server.sendmail(sender, recipient, msg.as_string())
    print("Email message sent")


def oauthFlow(today):
    gauth = GoogleAuth()
    # Try to load saved client credentials
    gauth.LoadCredentialsFile("/usr/src/app/mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        # gauth.LocalWebserverAuth()
        print(f"({today}) Google OAuth Token expired, executing OAuth flow below or run 'force_gdrive_push_reauth.sh'")
        if gmailAppPassword != None:
            sendEmail(gmailUserName, gmailRecipient, f"{csvFileName} - Push GDrive Token failed ({today})", "Log in to ssh-cloud1 and either follow the container logs and perform the OAuth CLI process, pasting the Access Code via an interactive container shell or execute the 'force_gdrive_push_reauth.sh'", gmailAppPassword)
        gauth.CommandLineAuth()
    elif gauth.access_token_expired:
    # Refresh them if expired
        try:
            gauth.Refresh()
        except Exception as e:
                print(f"({today}) Google OAuth Token Refresh failed, execute 'force_gdrive_push_reauth.sh'. Exiting..")
                print(f"Exception: {e}")
                if gmailAppPassword != None:
                    sendEmail(gmailUserName, gmailRecipient, f"{csvFileName} - Push GDrive Token failed ({today})", "Log in to ssh-cloud1 and execute the 'force_gdrive_push_reauth.sh'", gmailAppPassword)
                exit(1)
    else:
        # Initialize the saved creds
        print(f"({today}) Initializing saved OAuth creds file..")
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("/usr/src/app/mycreds.txt")
    drive=GoogleDrive(gauth)
    return drive

# try:
#     if int(sys.argv[1])>0:
#         sleepTimeSeconds=min(int(sys.argv[1]), 86400)
# except: 
#         sleepTimeSeconds=86400


def pushToGdrive(folderId, today, drive):
    testCSV = os.path.isfile(f'/usr/src/app/webserver/static/{csvFileName}.csv')
    if not testCSV: print(f"({today}) File not found, '/usr/src/app/webserver/{csvFileName}.csv', retrying in {sleepTimeSeconds}", file=sys.stderr); return
    testCS = os.path.isfile('/usr/src/app/client_secrets.json')
    if not testCS: print(f"({today}) File not found, '/usr/src/app/client_secrets.json', retrying in {sleepTimeSeconds}", file=sys.stderr); return
    if folderId == None: print(f"({today}) 'FolderId' must be specified in environment file, retrying in {sleepTimeSeconds}", file=sys.stderr); return
    # drive=GoogleDrive(gauth)
    try:
        file_list = drive.ListFile({'q':"'"+folderId+"' in parents and title='"+csvFileName+"' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"}).GetList()
        file_id=file_list[-1]['id']
        csvUpdate = drive.CreateFile({'id':file_id})
        csvUpdate.SetContentFile(f'/usr/src/app/webserver/static/{csvFileName}.csv')
        csvUpdate.Upload({'convert':True})
        print(f"({today}) File update successful on File ID: {file_id}")
    except IndexError:
        print(f"({today}) '{csvFileName}.csv' not found, creating..")
        csvFile = drive.CreateFile({'title':f'{csvFileName}', 'parents':[{'id': f'{folderId}'}]})
        csvFile.SetContentFile(f'/usr/src/app/webserver/static/{csvFileName}.csv')
        csvFile.Upload({'convert':True})
        file_id=csvFile['id']
        print(f"({today}) File creation successful. File ID: {file_id}")
    except Exception as e:
        print(f"({today}) '{csvFileName}.csv' not found due to the following exception: {e}, retrying in {sleepTimeSeconds}..", file=sys.stderr); return

# call function every set number of seconds
if __name__ == '__main__':
    today=datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%B %d, %Y %I:%M%p %Z")
    drive = oauthFlow(today)
    pushToGdrive(folderId, today, drive)
