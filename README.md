# GS Proxy

A dead simple, caching proxy for Google spreadsheets.  Uses Flask and meant to be deployed on Heroku.

# Install and run locally

1. Create a virtualenv
2. ```pip install -r requirements.txt```
3. Set spreadsheet keys that are acceptable:  ```export GS_PROXY_KEYS=<KEY1>,<KEY2>,<KEY3>```
4. Set how many minutes to keep cached values (default is 5): ```export GS_PROXY_CACHE=<MINUTES>```
5. Run locally: ```python app.py```
6. Go to http://localhost:5000

## Deploy on Heroku

For Heroku.

1. Setup and install Heroku command line tools
1. Create Heroku app with whatever name you want: ```heroku apps:create <APP_NAME>```
1. Add spreadsheet keys: ```heroku config:set GS_PROXY_KEYS=<KEY1>,<KEY2>,<KEY3>```
1. (optional) Set cache time limit: ```heroku config:set GS_PROXY_CACHE=<MINUTES>```
1. Push up code: ```git push heroku master```
1. You can open the app with ```heroku open```
1. Use in your application by making a request like the following.  Make sure to encode the proxy url parameter. ```http://<APP_NAME>.herokuapp.com/proxy?url=https%3A//spreadsheets.google.com/feeds/worksheets/<KEY1>/public/basic%3Falt%3Djson-in-script```