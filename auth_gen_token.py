import json
import os
import requests
from pydrive.auth import GoogleAuth
from requests.exceptions import ConnectionError

def checkCreds():

    tokenExpirationThreshold=.10
    expiresIn=0

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
        try:
            if (r.json()['error']):
                print("Token invalid, re-authentication requied..")
                os.remove("mycreds.txt")
                return
        except KeyError:
            expiresIn=round(float(r.json()['expires_in'])/60/60,2)
    except KeyError:
        print("parsing available token response..")
        expiresIn=round(float(r.json()['token_response']['expires_in'])/60/60,2)
    except ConnectionError as c:
        print("Cannot connect to oauth2.googleapis.com exiting..")
        print(f"Connection Error: {c}")
        exit(1)
    except Exception as e:
        print(f"Exception occured: {e}")
        
    print(f'Access Token expiration in hours: {expiresIn}. Force re-auth within threshold: {tokenExpirationThreshold:.2f} hours')
    if expiresIn < tokenExpirationThreshold:
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

checkCreds()
authNow()