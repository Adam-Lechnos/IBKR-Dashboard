# IBKR-Dashboard
Docker Compose for creating a IBKR Dashboard which includes risk data and current positions

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
* [Docker Engine](https://docs.docker.com/engine/install/)
* Google Account and target Google Drive Folder ID
  * Embedded within the browser's URL when at the target folder usually after the `/folder/` string.
* Install `requirements.txt` by executing within the git folder `pip3 -r requirements.txt`
* [Docker Compose Environment Files](#docker-compose-environment-files)
* [Google Cloud OAuth With Enable APIs](#google-cloud-oauth-With-enable-apis)
  * And the subsequent `client_secrets.json` containing the `client_secret` and `client_id` for use by the [pydrive.auth](https://pythonhosted.org/PyDrive/oauth.html) library.

# Docker Compose Environment Files
Create the following Docker Compose environment files at the root of the git repo

* env.list.gdrive
  ```
  folderId=Google_Drive_Folder_ID
  refreshPushSeconds=60
  csvFileName=IBKR_Data
  ```
  * `refreshPushSeconds` may be set to the desired CSV push interval for data overwrite in Google Drive
  * `csvFileName` (optional) the file name of the downloadable CSV. When specified must match the value within `env.list.parser` env file. Defaults to `IBKR_Data`
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
  csvFileName=IBKR_Data
  ```
  * `sleepTimeSeconds` may set to the desired API parser re-run interval.
    * The pre-formatted HTML refresh interval will always be set to 5 seconds longer than this value.
  * `csvFileName` (optional) the file name of the downloadable CSV. When specified must match the value within `env.list.gdrive` env file. Defaults to `IBKR_Data`
* env.list.dashboard
  ```
  useTLS=no
  webPort=8443
  ```
  * `useTLS` may set to `yes` for enabling TLS. Place the key and certificate files within the root of the git repo with file names `server.key` and gh r`server.crt` respectively   
    * Uncomment the `docker-compose.yml` under the commented line `# Uncomment below to specify TLS cert/key files`
  * `webPort` may set to any other port. Change the port number in `docker-compose.yml` to the same value as the new webPort number under the `ibkr-dashboard` service

# Google Cloud OAuth With Enable APIs
Enable Google Cloud OAuth flow by creating a project in Google Console, enabling the Google Drive APIs, then downloading the OAuth `client_secrets.json` for OAuth command authorization flow for container permissions to Google Drive.