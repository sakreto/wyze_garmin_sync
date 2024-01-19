  

# Wyze Connect Sync - Historical Data Fork

  
This is a forked version of Wyze Connect Sync that focuses on pulling historical data. This is made for technology savvy users with knowledge of python. Issues/suggestions are welcome.

### Overview of the Script

1.  **Environment Variables Loading:**
    
    -   Loads credentials and configuration from a `creds.env` file using the `load_env` function. (You must create the creds.env)
    - The contents of the creds.env file are as follows:<br> `WYZE_EMAIL=*string*
	WYZE_PASSWORD=*string*
	WYZE_KEY_ID=*string*
	WYZE_API_KEY=*string*
	GARMIN_USERNAME=*string*
	GARMIN_PASSWORD=*string*`
    -   This function changes the working directory to `wyze_garmin_sync`, which might not be necessary or desirable for all use cases. Consider whether this is required and ensure that the directory exists.
2.  **Wyze Integration:**
    
    -   Logs in to the Wyze service using credentials from the environment variables.
    -   Handles potential API errors gracefully.
3.  **Garmin Integration:**
    
    -   The `upload_to_garmin` function attempts to resume a Garmin session or log in if needed, then uploads a file to Garmin.
    -   It handles exceptions and prompts for credentials if necessary. This could be a security concern, as manual input of credentials might not be ideal in an automated script.
4.  **FIT File Generation:**
    
    -   `generate_fit_file` creates a FIT file based on the data record from the Wyze Scale.
    -   It converts various health metrics and writes them to a FIT file, which is then saved to a specified path.
5.  **Data Processing and Uploading:**
    
    -   The `main` function handles the overall process, including fetching device data, processing each record, and deciding whether to upload based on checksum comparison.
    -   It checks for new measurements by comparing checksums and uploads the FIT files to Garmin if necessary.

## Usage

 1. Clone into a local directory
 2. Create python VENV
 3. Install dependencies
 4. Create `creds.env` file and input credentials (inside of the wyze_garmin_sync directory)
 5. Set up the datestamps for the API fetch in `scale.py` ln 33 and 35
 6. Run using `python3 scale.py` (play around with your directory setup if needed)

<br><br>
**Please find the original Read-Me with links to original repo and contribution to creator below:**
***

<p  align="center">

<img  width="25%"  src="https://user-images.githubusercontent.com/22617546/208175452-dbbff5b9-59ce-4ffc-a255-698617c94de0.jpg" />

</p>

  

[![Stars](https://img.shields.io/github/stars/svanhoutte/wyze_garmin_sync)](https://github.com/svanhoutte/wyze_garmin_sync/stargazers)

[![Version](https://img.shields.io/github/v/release/svanhoutte/wyze_garmin_sync)](https://github.com/svanhoutte/wyze_garmin_sync/releases/latest)

[![Commits Since Latest Release](https://img.shields.io/github/commits-since/svanhoutte/wyze_garmin_sync/latest)](https://github.com/svanhoutte/wyze_garmin_sync/commits/master)

[![Latest Release Date](https://img.shields.io/github/release-date/svanhoutte/wyze_garmin_sync)](https://github.com/svanhoutte/wyze_garmin_sync/releases/latest)

[![Open Issues](https://img.shields.io/github/issues-raw/svanhoutte/wyze_garmin_sync)](https://github.com/svanhoutte/wyze_garmin_sync/issues?q=is%3Aopen+is%3Aissue)

[![Closed Issues](https://img.shields.io/github/issues-closed-raw/svanhoutte/wyze_garmin_sync)](https://github.com/svanhoutte/wyze_garmin_sync/issues?q=is%3Aissue+is%3Aclosed)

  

[![PayPal](https://img.shields.io/badge/PayPal-Donate-green)](https://paypal.me/SVanhoutte79?country.x=US&locale.x=en_US)

[![Buymeacoffee](https://badgen.net/badge/icon/buymeacoffee?icon=buymeacoffee&label)](https://www.buymeacoffee.com/sebastienv)

  
  


***

**Sync the Wyze scale with Garmin connect v2.0.0**

  

The python script collect the data from your Wyze account and create the .fit file to be uploaded to Garmin. The script leverage [Garth](https://github.com/matin/garth), and [Wyze_SDK](https://github.com/shauntarves/wyze-sdk) to automatically upload the last measurement you took on your Wyze smart scale to Garmin Connect.

  

The V2.0.0 is 100% python based and doesn't require anymore a shell script.

Support 2FA for Garmin and Wyze and scale auto-discovery.

Python package is not yet available but docker version is available on alpine python based image.

  

## Authentication

  

**Wyze authentication**

Login/Pass/TOTP is not working anymore Wyze requires an API key and id to log in

Visit the Wyze developer API portal to generate an API ID/KEY: https://developer-api-console.wyze.com/#/apikey/view

  

**Garmin authentication**

For Garmin authentication with 2FA :

First run the docker compose this way :

  

docker compose run --rm wyzegarminconnect

  

You ll be prompted for the 2FA code, enter it, this will create the token that will be valid for one year.

Once the token is created you don't have to authenticate again as long as the token is valid and you can run the

  

docker compose run -d

docker compose logs -f

  

## Install through docker compose

  

[![Docker](https://img.shields.io/docker/v/svanhoutte/wyzegarminconnect/latest?logo=docker)](https://hub.docker.com/repository/docker/svanhoutte/wyzegarminconnect)

![Docker](https://badgen.net/badge/color/arm64/yellow?icon=docker&label=) ![Docker](https://badgen.net/badge/color/arm/orange?icon=docker&label=) ![Docker](https://badgen.net/badge/color/amd64/blue?icon=docker&label=)

  

Docker image is now available for amd64, arm64 and arm.

  

Download the [docker-compose.yml](https://github.com/svanhoutte/wyze_garmin_sync/blob/main/docker-compose.yml  "docker-compose.yml") and add your credentials:

  

version: "3.9"

services:

wyzegarminconnect:

image: svanhoutte/wyzegarminconnect:latest

stdin_open: true # docker run -i

tty: true # docker run -t

restart: unless-stopped

network_mode: "host"

environment:

WYZE_EMAIL: "wyze username"

WYZE_PASSWORD: "wyze password"

WYZE_KEY_ID: "ID"

WYZE_API_KEY: "KEY"

Garmin_username: "garmin username"

Garmin_password: "garmin password"

volumes:

- "/etc/timezone:/etc/timezone:ro"

- "/etc/localtime:/etc/localtime:ro"

- "./tokens:/wyze_garmin_sync/tokens"

  
  

The volumes are mounted to sync logs in the containers and the host.

Then do the

  

docker compose up -d

docker compose logs -f

  
  

## Legacy install

  

### Requirements

  

This requires Python 3.8 and above. If you're unsure how to check what version of Python you're on, you can check it using the following:

  

> **Note:** You may need to use `python3` before your commands to ensure you use the correct Python path. e.g. `python3 --version`

  

python --version

-- or --

python3 --version

  

You ll need also a Linux environment most of the recent distribution should work.

  

### [](https://github.com/svanhoutte/wyze_garmin_sync#installation)Installation

  

#### [](https://github.com/svanhoutte/wyze_garmin_sync#installation-of-wyze-sdk)Installation of Wyze SDK

  

$ pip install wyze_sdk

  

#### [](https://github.com/svanhoutte/wyze_garmin_sync#installation-of-garth)Installation of Garth

  

$ pip install garth

  

#### [](https://github.com/svanhoutte/wyze_garmin_sync#installation-of-the-script-shell)Installation of the python script

  

First clone the repository

  

git clone https://github.com/svanhoutte/wyze_garmin_sync.git

  

Provide and export your credentials in your shell environment

  

WYZE_EMAIL=

WYZE_PASSWORD=

WYZE_TOTP=

WYZE_KEY_ID=

WYZE_API_KEY=

Garmin_username=

Garmin_password=

export WYZE_API_KEY

export WYZE_KEY_ID

export WYZE_EMAIL

export WYZE_PASSWORD

export Garmin_username

export Garmin_password

  

#### [](https://github.com/svanhoutte/wyze_garmin_sync#run-the-script)Run the script

  

In your working directory add the execution right on the script

`chmod +x ./scale.py` Then run `./scale.py` and if all goes well you should be able to see your data in Garmin connect.

This should be done at least once before setting up the cron as if you have 2FA for Garmin to allow you to enter the 2 step of authentication.

  

#### [](https://github.com/svanhoutte/wyze_garmin_sync#setup-with-cron)Setup with Cron

  

Will run the script every 10 min to get if a new measurement has been made on the scale.

  

*/10 * * * * path_to_script/scale.py 2>&1 | /usr/bin/logger -t garminsync

  

***

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/sebastienv)