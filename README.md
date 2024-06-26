# Bitwarden Item Cleaner

## Why?
There might be some cases when you want to log in on site by clicking link from Bitwarden and accidentally visit old password recovery expired link, so you need get back to the site, click on log in button and fill your credentials

## Features

- ### URI Converter
    This script has two ways of URIs converting: domain and subdomain converter

    #### 1. Domain converter
    To convert URIs to domain only, use **-domain** flag

    ``` python bwc.py bitwarden_export.json -domain ```

    ![](https://github.com/graythze/BitwardenItemCleaner/blob/main/src/pic/domain.jpg)

    #### 2. Subdomain converter
    To convert URIs including subdomain, use **-subdomain** flag
  
    ``` python bwc.py bitwarden_export.json -subdomain ```

    ![](https://github.com/graythze/BitwardenItemCleaner/blob/main/src/pic/subdomain.jpg)

- ### Password history cleaner
    If you need to delete old previously used passwords (aka "Password History"), you can use this script with **-removeusedpw** flag. After that, all entries including old passwords will be removed.

    ``` python bwc.py bitwarden_export.json -removeusedpw ```

    ![](https://github.com/graythze/BitwardenItemCleaner/blob/main/src/pic/removeusedpw.jpg)

- ### Use cleaner and converter together
    If you want to clean old used passwords and convert URIs, you can set flags together

    ``` python bwc.py bitwarden_export.json [-domain | -subdomain] [-removeusedpw] ```

## Security
To edit URIs or remove Password History, you'll need export your vault in unencrypted JSON file.

After using this script, import result file in to Bitwarden and DELETE OLD AND RESULT JSON FILES
