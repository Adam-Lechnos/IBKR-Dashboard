from pydrive.auth import GoogleAuth

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
    authNow()