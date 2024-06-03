# IBKR-Dashboard
Docker Compose for creating a IBKR Dashboard which includes risk data and current positions

# Containers
Consists of three containers
* [ibeam](https://github.com/Voyz/ibeam) - With some modifications for a headless API Gateway enabling authenticating to Interactive Brokers Web API
  * Created by [Voyz](https://github.com/Voyz) with modifications made by me for service discovery across external containers
* ibkr-api-parser - Parses the IBKR API and returns to formatted html
* ibkr-dashboard - A web interface consisting of the risk and position data
* ibkr-push-gdrive - Pushes the updated and downloadable dashboard CSV data into Google Drive as a Google Sheet.

# Pre-requisites
* Python3
* Python3 pip
* [Docker Engine](https://docs.docker.com/engine/install/)
* Google Account and target Google Drive Folder ID
  * Embedded within the browser's URL at the target folder, usually after `../folder/..` string.
* Install `requirements.txt` by executing within the git folder `pip3 -r requirements.txt`
* [Docker Compose Environment Files](#docker-compose-environment-files)
* [Google Cloud OAuth With Enable APIs](#google-cloud-oauth-With-enable-apis)

# Docker Compose Environment Files
Create the following Docker Compose environment files at the root of the git repo

* env.list.gdrive
  ```
  folderId=Google_Drive_Folder_ID
  refreshPushSeconds=60
  ```
  * `refreshPushSeconds` may be set to the desired CSV push interval for data overwrite in Google Drive
* env.list.ibeam
  ```
  IBEAM_ACCOUNT=ibkr_username
  IBEAM_PASSWORD=encrypted_password
  IBEAM_KEY=encryption_key
  ```
  * Input your IBKR Username and Password into `gen_key_pw.py` then execute the script to generate the required input data
* env.list.parser
  ```
  sleepTimeSeconds=60
  ```
  * `sleepTimeSeconds` may set to the desired website data refresh parser

# Google Cloud OAuth With Enable APIs
Enable Google Cloud OAuth flow by creating a project in Google Console, enabling the Google Drive APIs, then downloading the OAuth `client_secrets.json` for OAuth command authorization flow for container permissions to Google Drive.