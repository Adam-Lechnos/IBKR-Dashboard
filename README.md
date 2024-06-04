# IBKR-Dashboard
Docker Compose for creating a IBKR Dashboard which includes risk data and current positions

# Containers
Consists of fouse containers
* [ibeam](https://github.com/Voyz/ibeam) - With some modifications for inter-pod discovery; a headless API Gateway enabling authenticating to Interactive Brokers Web API
  * Created by [Voyz](https://github.com/Voyz) with modifications made by me for service discovery across external containers
* ibkr-api-parser - Parses the IBKR API and returns to pre-formatted HTML and a downloadable CSV on a recurring interval
* ibkr-dashboard - A Flask web server for displaying the pre-formatted HTML and refreshes on a recurring interval, also enabling access to the downloadable CSV data
* ibkr-push-gdrive - Pushes the updated and downloadable dashboard CSV data into Google Drive as a Google Sheet on a recurring interval, updating the existing file once created

# Pre-requisites
* Python3
* Python3 pip
* [Docker Engine](https://docs.docker.com/engine/install/){:target="_blank" rel="noopener"}
* Google Account and target Google Drive Folder ID
  * Embedded within the browser's URL at the target folder, usually after `../folder/..` string.
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
  * `sleepTimeSeconds` may set to the desired API parser re-run interval.
    * The pre-formatted HTML refresh interval will always be set to 5 seconds longer than this value.
* env.list.dashboard
  ```
  useTLS=no
  webPort=8443
  ```
  * `useTLS` may set to `yes` for enabling TLS. Place the key and certificate files within the root of the git repo with file names `server.key` and `server.crt` respectively   
    * Uncomment the `docker-compose.yml` under the commented line `# Uncomment below to specify TLS cert/key files`
  * `webPort` may set to any other port. Change the port number in `docker-compose.yml` to the same value as the new webPort number under the `ibkr-dashboard` service

# Google Cloud OAuth With Enable APIs
Enable Google Cloud OAuth flow by creating a project in Google Console, enabling the Google Drive APIs, then downloading the OAuth `client_secrets.json` for OAuth command authorization flow for container permissions to Google Drive.