# GS Proxy

A simple cache proxy for Google spreadsheets.  Uses Flask and meant to be deployed on Heroku.

# Install

1. Create a virtualenv
2. ```pip install -r requirements.txt```
3. Set spreadsheet keys that are acceptable:  ```export GS_PROXY_KEYS=key1,key2,key3```
4. Set how many minutes to keep cached values (default is 10): ```export GS_PROXY_CACHE=60```

## Deploy

For Heroku.