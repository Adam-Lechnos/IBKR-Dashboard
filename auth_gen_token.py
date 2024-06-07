import json
import os
import requests
from pydrive.auth import GoogleAuth

tokenExpirationThreshold=.10

def checkCreds():

    if os.path.exists("mycreds.txt"):
        with open('mycreds.txt') as f:
            # Read the contents of the file
            text = f.read()
        credsData = json.loads(text)
    else:
        print("Google OAuth token not found, re-authentication required..")
        return
    
    try:
        accessToken=credsData['access_token']
        r = requests.get(f"https://oauth2.googleapis.com/tokeninfo?access_token={accessToken}")
        difference=round(float(r.json()['expires_in'])/60/60,2)
    except:
        print("token file 'mycreds.txt' missing keys per lookup values 'accessToken' or 'expires_in', re-authentication required..")
        os.remove("mycreds.txt")
        return

    print(f'Access Token expiration in hours: {difference}. Force re-auth within threshold: {tokenExpirationThreshold:.2f} hours')
    if difference < tokenExpirationThreshold:
        print(f'Token expiration threshold within {tokenExpirationThreshold:.2f} hours of expiry, re-authentication required..')
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