import json
import os
import requests
from pydrive.auth import GoogleAuth

def checkCreds():

    if os.path.exists("mycreds.txt"):
        with open('mycreds.txt') as f:
            # Read the contents of the file
            text = f.read()
        credsData = json.loads(text)
    else:
        print("Google OAuth token not found, re-authentication required..")
        return
    
    accessToken=credsData['access_token']
    r = requests.get(f"https://oauth2.googleapis.com/tokeninfo?access_token={accessToken}")
    difference=round(float(r.json()['expires_in'])/60/60,2)
    print(f'Access Token exiration in hours: {difference}')
    if difference < .10:
        print(f"Google OAuth access token expiry in less than hours specified: {difference}, re-authentication required via OAuth flow..")
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