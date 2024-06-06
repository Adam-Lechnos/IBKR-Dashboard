import json
import datetime
import pytz
import re
import os
from pydrive.auth import GoogleAuth

def checkCreds():
    today = datetime.datetime.now(pytz.timezone('UTC')).strftime("%Y%m%d%H%M%S")

    if os.path.exists("demofile.txt"):
        with open('mycreds.txt') as f:
            # Read the contents of the file
            text = f.read()
        credsData = json.loads(text)
    else:
        print("Google OAuth token not found, re-authentication required..")
        return

    tokenExpiry = credsData['token_expiry']
    tokenExpiry = re.sub("[^0-9]", "", tokenExpiry)
    difference = int(tokenExpiry[:-6])-int(currDate[:-6])
    print(difference)
    if difference < 2:
        print("Google OAuth token close to expiry, re-authentication required..")
        os.remove("mycreds.txt")


def authNow():
    gauth = GoogleAuth()
    # Try to load saved client credentials
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        # gauth.LocalWebserverAuth()
        print("Token generation required via OAuth flow..")
        gauth.CommandLineAuth()

    gauth.SaveCredentialsFile("mycreds.txt")

if __name__ == '__main__':
    checkCreds()
    authNow()