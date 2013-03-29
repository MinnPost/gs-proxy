import os
import json
import datetime
import re
import urlparse
import urllib
import requests
from flask import Flask, Response, render_template, request, abort
from flask.ext.cache import Cache

# Get environement variables
debug_app = 'DEBUG_APP' in os.environ
proxy_keys = os.environ['GS_PROXY_KEYS'].split(',')
proxy_cache = 5
if 'GS_PROXY_CACHE' in os.environ:
  proxy_cache = int(os.environ['GS_PROXY_CACHE'])
  

# Other application wide variables
default_google_callback = 'gdata.io.handleScriptLoaded'
domain_check = 'google'
jsonp_to_json_keys = {
  'json-in-script': 'json'
}


# Make and configure the Flask app
app = Flask(__name__)
if debug_app:
  app.debug = True


# Set up cache
cache_config = {
  'CACHE_TYPE': 'filesystem',
  'CACHE_THRESHOLD': 1000,
  'CACHE_DIR': 'cache'
}
cache = Cache(config = cache_config)
cache.init_app(app, config = cache_config)



# Just a default route
@app.route('/')
@cache.cached(timeout = 500)
def index():
  return 'Supported keys: %s' % ', '.join(proxy_keys)
    

# Proxy route
@app.route('/proxy')
def handle_proxy():
  request_url = request.args.get('url', '')
  request_parsed = urlparse.urlparse(request_url)
  
  # Check if valid proxy url
  if not is_valid_url(request_parsed):
    abort(404)
  
  # Turn into JSON request and cache that
  request_url, callback = convert_jsonp_to_json(request_parsed)
  
  # Get value from proxied url (this is the cached part)
  proxy_request = make_proxy(request_url)
  if proxy_request['status_code'] != requests.codes.ok:
    abort(proxy_request['status_code'])
  
  # If callback, wrap response text
  response_text = proxy_request['text']
  if callback:
    response_text = '%s(%s);' % (callback, proxy_request['text'])
  
  return Response(response_text, 
    proxy_request['status_code'], proxy_request['headers'])


# Get proxy URL and cache the results
@cache.memoize(proxy_cache * 60)
def make_proxy(url):
  if app.debug:
    print 'Cache missed: %s' % url

  r = requests.get(url)
  return {
    'text': r.text,
    'status_code': r.status_code,
    'headers': r.headers,
  }


# Convert call to json request and get callback
def convert_jsonp_to_json(url_parsed):
  # Parses query string into list of tuples
  query_parsed = urlparse.parse_qsl(url_parsed.query)

  # Get callback if there is one
  callback = False
  for i, v in enumerate(query_parsed):
    if query_parsed[i][0] == 'callback':
      callback = query_parsed[i][1]
      del query_parsed[i]
  
  # Convert jsonp request to json
  jsonp_found = False
  
  for k in jsonp_to_json_keys:
    for i, v in enumerate(query_parsed):
      if query_parsed[i][0] == 'alt' and query_parsed[i][1] == k:
        query_parsed[i] = ('alt', jsonp_to_json_keys[k])
        jsonp_found = True
  
  # If no callback and jsonp, set default
  if jsonp_found and not callback:
    callback = default_google_callback
  
  # Recreate the query string by making new tuple.
  # Note that we are reseting the fragment
  # and any the other probably unnecessary parts.
  new_url_tuple = url_parsed[0:4] + (urllib.urlencode(query_parsed),) + ('',)
  
  return urlparse.urlunparse(new_url_tuple), callback


# Check if valid key is in url
def is_valid_url(url_parsed):
  # Make sure the key is in the path, and not the
  # query string, otherwise the service could be abused.
  # As an extra mesaure, just make sure the domain
  # is google.
  found = False
  
  for k in proxy_keys:
    if url_parsed.path.find(k) != -1:
      found = True
  
  if url_parsed.netloc.find(domain_check) == -1:
    found = False

  return found;


# Start Flask App
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)