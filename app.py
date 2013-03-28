import os
import json
import datetime
import re
import urlparse
import requests
from flask import Flask, Response, render_template, request, abort
from flask.ext.cache import Cache

# Get environement variables
debug_app = 'DEBUG_APP' in os.environ
proxy_keys = os.environ['GS_PROXY_KEYS'].split(',')
proxy_cache = 5
if 'GS_PROXY_CACHE' in os.environ:
  proxy_cache = int(os.environ['GS_PROXY_CACHE'])


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
  
  # Get value
  proxy_request = requests.get(request_url)
  if proxy_request.status_code != requests.codes.ok:
    abort(proxy_request.status_code)
  
  return Response(proxy_request.text, None, proxy_request.headers)



# Helper function
def is_valid_url(url_parsed):
  # Make sure the key is in the path, and not the
  # query string, otherwise the service could be abused
  found = False
  
  for k in proxy_keys:
    if url_parsed.path.find(k) != -1:
      found = True

  return found;


# Start Flask App
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)