# IBKR-Dashboard
Docker Compose for creating an IBKR Dashboard which includes risk data and current positions across all accessible accounts.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![GitHub Release](https://img.shields.io/github/v/release/Adam-Lechnos/IBKR-Dashboard)
 

# Containers
Consists of fouse containers
* [ibeam](https://github.com/Voyz/ibeam) - With some modifications for inter-pod discovery; a headless API Gateway enabling authenticating to Interactive Brokers Web API
  * Created by [Voyz](https://github.com/Voyz) with modifications made by me for service discovery across external containers
* ibkr-api-parser - Parses the IBKR API and returns to pre-formatted HTML and a downloadable CSV on a recurring interval
* ibkr-dashboard - A Flask web server for displaying the pre-formatted HTML and refreshes on a recurring interval, also enabling access to the downloadable CSV data
* ibkr-push-gdrive - Pushes the updated and downloadable dashboard CSV data into Google Drive as a Google Sheet on a recurring interval, updating the existing file once created

## Docker Hub
The containers are made public within Docker Hub
* [ibeam](https://hub.docker.com/r/adamlechnos/ibeam)
* [ibkr-api-parser](https://hub.docker.com/r/adamlechnos/ibkr-create-website)
* [ibkr-dashboard](https://hub.docker.com/r/adamlechnos/ibkr-dashboard)
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
* [Google Cloud OAuth With Enable APIs](#google-cloud-oauth-with-enabled-apis)
  * And the subsequent `client_secrets.json` containing the `client_secret` and `client_id` for use by the [pydrive.auth](https://pythonhosted.org/PyDrive/oauth.html) library.

# Generate Encrypted IBKR Password and Key Pair
Encrypt your IBKR password and store the encryped password and key within the `env.list.ibeam` when creating the [Docker Compose Environment Files](#docker-compose-environment-files)

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
  ```
  * `PYTHONUNBUFFERED` should be specified as is to enable docker/container output logging.
  * `refreshPushSeconds` may be set to the desired CSV push interval for data overwrite in Google Drive. Defaults to 60 when omitted.
  * `csvFileName` (optional) the file name of the downloadable CSV. When specified must match the value within `env.list.parser` env file. Defaults to `IBKR_Data`.
* env.list.ibeam
  ```
  IBEAM_ACCOUNT=ibkr_username
  IBEAM_PASSWORD=encrypted_password
  IBEAM_KEY=encryption_key
  ```
  * Input your IBKR Username and Password into `gen_key_pw.py` then execute the script to generate the required input data
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
* env.list.dashboard
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
  * `flaskDebug` set the debug mode to. Defaults to False if omitted.

# Google Cloud OAuth With Enabled APIs
Enable Google Cloud OAuth flow by creating a project in Google Console, enabling the Google Drive APIs, then downloading the OAuth `client_secrets.json` for OAuth command authorization flow for container permissions to Google Drive.