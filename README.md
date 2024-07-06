# IBKR-Dashboard
Docker Compose for creating an IBKR Dashboard which includes risk data and current positions across all accessible accounts.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![GitHub Release](https://img.shields.io/github/v/release/Adam-Lechnos/IBKR-Dashboard)
 

# Containers
Consists of fouse containers
* [ibeam](https://github.com/Voyz/ibeam) - With some modifications for inter-pod discovery; a headless API Gateway enabling authenticating to Interactive Brokers Web API
  * Created by [Voyz](https://github.com/Voyz) with modifications made by me for service discovery across external containers
* ibkr-api-parser - Parses the IBKR API and returns to pre-formatted HTML and a downloadable CSV on a recurring interval
* ibkr-dashboard-nginx - An nginx web server for displaying the `ibkr-api-parser` generated pre-formatted HTML, enabled with TLS and Basic Authentication by default.
* ibkr-push-gdrive - Pushes the updated and downloadable dashboard CSV data into Google Drive as a Google Sheet on a recurring interval, updating the existing file once created

## Docker Hub
The containers are made public within Docker Hub
* [ibeam](https://hub.docker.com/r/adamlechnos/ibeam)
* [ibkr-api-parser](https://hub.docker.com/r/adamlechnos/ibkr-create-website)
* [ibkr-dashboard-nginx](https://hub.docker.com/r/adamlechnos/ibkr-dashboard-nginx)
* [ibkr-push-gdrive](https://hub.docker.com/r/adamlechnos/ibkr-push-gdrive)

# Pre-requisites
* Python3
* Python3 pip
* [Apache Utilities Package](https://www.digitalocean.com/community/tutorials/how-to-set-up-password-authentication-with-apache-on-ubuntu-18-04-quickstart) for Basic Authentication
* [Docker Engine](https://docs.docker.com/engine/install/)
* Google Account and target Google Drive Folder ID
  * Embedded within the browser's URL when at the target folder usually after the `/folder/` string.
* Install `requirements.txt` by executing within the git folder `pip3 -r requirements.txt`
* [Generate Encrypted IBKR Password and Key Pair](#generate-encrypted-ibkr-password-and-key-pair)
* [Docker Compose Environment Files](#docker-compose-environment-files)
* [nginx Config file](#nginx-config-file)
* [Google Cloud OAuth With Enable APIs](#google-cloud-oauth-with-enabled-apis)
  * And the subsequent `client_secrets.json` containing the `client_secret` and `client_id` for use by the [pydrive.auth](https://pythonhosted.org/PyDrive/oauth.html) library.

# Generate Encrypted IBKR Password and Key Pair
Encrypt your IBKR password and store the encryped password and key within the `env.list.ibeam` when creating the [Docker Compose Environment Files](#docker-compose-environment-files)

**Security Recommendation**: It is recommend to first create an additional read-only user with a strong password. Additional IP restriction is also recommended if feasible. Refer to the official Interactive Brokers documenting [here](https://www.ibkrguides.com/clientportal/uar/addingauser.htm).

* Create a file named `gen_key_pw.py`
* Add the following to the file, replacing `'password'` with your IBKR password. (this file is part of `.gitignore`)
  ``` python
  from cryptography.fernet import Fernet

  key = Fernet.generate_key()
  f = Fernet(key)
  password = f.encrypt(b'password')
  print(f'IBEAM_PASSWORD={password}, IBEAM_KEY={key}')
  ```
* Execute the file via the command `python3 gen_key_pw.py`. Make not of the printed encrypted password and key, excluding the `b` in front of each string.
* Remove the password from the `gen_key_pw.py` file

# Docker Compose Environment Files
Create the following Docker Compose environment files at the root of the git repo.

* env.list.gdrive
  ```
  PYTHONUNBUFFERED=1
  folderId=Google_Drive_Folder_ID
  refreshPushSeconds=60
  csvFileName=IBKR_Data
  gmailAppPassword=encrypted_password
  gmailAppPasswordKey=encryption_key
  gmailUserName=gmailuser@gmail.com
  gmailRecipient=gmailrecipient@gmail.com

  ```
  * `PYTHONUNBUFFERED` should be specified as is to enable docker/container output logging.
  * `refreshPushSeconds` may be set to the desired CSV push interval for data overwrite in Google Drive. Defaults to 60 when omitted.
  * `csvFileName` (optional) the file name of the downloadable CSV. When specified must match the value within `env.list.parser` env file. Defaults to `IBKR_Data`.
  * `gmailAppPassword` use Google Accounts to generate an app password for GMail TLS SMTP Authentication. Encrypt the app password using `gen_key_pw.py`. Optional, if omitted alert emails will be disabled.
  * `gmailAppPasswordKey` the app password encryption key, generated from the same output as the `gmailAppPassword` using `gen_key_pw.py`. Required when specifying `gmailAppPassword`.
    * Note that a plain text password may be used as a value for `gmailAppPassword` with the `gmailAppPasswordKey` key and value omitted, this is not recommended however.
  * `gmailUserName` the GMail user sending the email and authenticating to GMail. Required when specifying `gmailAppPassword`.
  * `gmailRecipient` the recipient of the emails. Required when specifying `gmailAppPassword`.

* env.list.ibeam
  ```
  IBEAM_ACCOUNT=ibkr_username
  IBEAM_PASSWORD=encrypted_password
  IBEAM_KEY=encryption_key
  ```
  * Input your IBKR Username and Password into `gen_key_pw.py` then execute the script to generate the required input data
    * Note that a plain text password may be used as a value for `IBEAM_PASSWORD` with the `IBEAM_KEY` key and value omitted, this is not recommended however.
    
* env.list.parser.
  ```
  PYTHONUNBUFFERED=1
  sleepTimeSeconds=60
  csvFileName=IBKR_Data
  ```
  * `PYTHONUNBUFFERED` should be specified as is to enable docker/container output logging.
  * `sleepTimeSeconds` may set to the desired API parser re-run interval. Defaults to 60 when omitted.
    * The pre-formatted HTML refresh interval will always be set to 5 seconds longer than this value.
  * `csvFileName` (optional) the file name of the downloadable CSV. When specified must match the value within `env.list.gdrive` env file. Defaults to `IBKR_Data` when omitted.
<!-- * env.list.dashboard
  ```
  PYTHONUNBUFFERED=1
  useTLS=no
  webPort=8443
  flaskDebug=False
  ```
  * `PYTHONUNBUFFERED` should be specified as is to enable docker/container output logging.
  * `useTLS` may set to `yes` for enabling TLS. Place the key and certificate files within the root of the git repo with file names `server.key` and gh r`server.crt` respectively.
    * Uncomment the `docker-compose.yml` under the commented line `# Uncomment below to specify TLS cert/key files`.
  * `webPort` may set to any other port. Change the port number in `docker-compose.yml` to the same value as the new webPort number under the `ibkr-dashboard` service.
  * `flaskDebug` set the debug mode to. Defaults to False if omitted. -->

# nginx Config file
The nginx config file provides customizable authentication settings, ports, TLS certificates, error and default web pages.

* default.conf
  * Global config - TLS, port, server name, and TLS cert settings
    ```
    listen       8443 ssl;
    listen  [::]:8443 ssl;
    server_name  ibkr-dash.example.com;
    ssl_certificate /usr/src/app/server.crt;
    ssl_certificate_key /usr/src/app/server.key;
    ```
  * option details:
    * listen: must match the port specified within the `docker-compose.yml`. Remove `ssl` option to disable TLS auth
    * server_name: the full DNS of the webserver address. May be set to `localhost`
    * ssl_certificate: certificate file which is first copied from the root folder `./server.crt`
    * ssl_certificate_key: certificate private key which is first copied from the root folder `./server.key`

  * Local config - basic auth and default webpage settings
    ```
    location / {
        root   /usr/src/app/webserver/static;
        index  index.html;

        auth_basic "Restricted";
        auth_basic_user_file  /etc/nginx/.htpasswd;

        include  /etc/nginx/mime.types;
    }
    ```
  * option details:
    * root: location where the static webpages are served
    * index.html: default webpage filename
    * auth_basic: leave as `"Restricted"` to enable password auth challenge
    * auth_basic_user_file: location of the `.htpasswd` which houses the authorized users and accompanying encrypted passwords. The file is generated upon running `run.sh` the fist time and placed in the root folder, adding the initial authorized user.

# Google Cloud OAuth With Enabled APIs
Enable Google Cloud OAuth flow by creating a project in Google Console, enabling the Google Drive APIs, then downloading the OAuth `client_secrets.json` for OAuth command authorization flow for container permissions to Google Drive.