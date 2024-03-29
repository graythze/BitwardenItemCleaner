# Bitwarden Item Cleaner

## Why?
There might be some cases when you want to login on site by clicking link from Bitwarden and accidentally visit old password recovery expired link, so you need get back to the site, click on log in and fill your credentials
## Features

- ### URI Cleaner
    This script has two ways of URIs converting: domain and subdomain converter
    #### 1. Domain converter
    To convert URIs to domain only, use *-domain* flag

    #### 2. Subdomain converter
    To convert URIs including subdomain, use *-subdomain* flag

- ### Password history cleaner
    If you need to delete old previously used passwords (aka "Password History"), you can use this script with *-removeusedpw* flag. After that, all entries including old passwords will be removed.

## Security
To edit URIs or remove Password History, you'll need export your vault in unencrypted JSON file.

After using this script, import result file in to Bitwarden and DELETE OLD AND RESULT JSON FILES