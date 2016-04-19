Github statistic tool
=====================
This utility collects statistics of all commits to all repos in the github organisation and export that to CSV files.

# Requirements
* python 3  (3.2 and higher, tested with 3.2 and 3.4)
* pip

Libraries that should be installed separately (with pip, for example). See Installation section for more details
* jsmin
* requests

# Installation
You should use access-tokens isntead your password for HTTPS/github authentication.

* Create and activate virtual environment, install required packages
```
$ virtualenv -p /usr/bin/python3 venv
$ source venv/bin/activate
$ pip install jsmin requests
```

**Set up github credentials**
* Get github OAuth acess token for github user you will be using with the app.
    * If this user doesn't have personal access token here are instructions how to create it:
        https://developer.github.com/v3/oauth/
        https://github.com/blog/1509-personal-api-tokens
    * If your githab user has OAuth access tokens already, you could find that tokens at the user settings page:
        https://github.com/settings/tokens
* Copy a `config/secret.config.json.dummy` to the file `config/secret.config.json`
* Edit `config/secret.config.json` file and enter your github user name and its access token hash to the appropriate fields.
* Create a new ssh key (see more details here: https://help.github.com/articles/generating-ssh-keys/).

Now you can run the application. The easiest way to check if it works or not is to run:

# Usage:
```
./git-stats.py <organisation> -csv <csv-filename> [-limit <number>]
```

Examples:
Save all commits for the opensoft organisation to the file:
```
./git-stats opensoft -csv commiters.csv
```
Save all commits for the first 5 repos in opensoft to csv file (this is useful for testing)
```
./git-stats opensoft -csv commiters.csv -limit 5
```
