from __future__ import print_function
import json
import os
import time
import uuid
import webbrowser

from six.moves import BaseHTTPServer
from six.moves import urllib
import requests


class Credentials(object):
    def __init__(self, data=None):
        if not data:
            data = {}

        self.access_token = data.get('access_token')
        self.refresh_token = data.get('refresh_token')
        self.expiration = data.get('expiration')
        self.scope = data.get('scope')
        self.path = None

        expires_in = data.get('expires_in')
        if expires_in:
            self.expiration = int(time.time() + expires_in)

    def is_expired(self):
        if not self.expiration:
            return False

        return self.expiration < time.time()

    def is_valid(self):
        if self.is_expired():
            return False
        if self.access_token is None:
            return False
        return True

    def as_dict(self):
        creds_dict = {}
        for attr in ['access_token', 'refresh_token', 'expiration', 'scope']:
            value = getattr(self, attr)
            if value:
                creds_dict[attr] = value
        return creds_dict

    def write(self, file_path=None):
        path = file_path or self.path
        config = {}

        # load existing config
        if os.path.exists(path):
            with open(file_path) as f:
                config = json.load(f)

        fdesc = os.open(path, os.O_WRONLY | os.O_CREAT, 0o600)
        with os.fdopen(fdesc, 'w') as f:
            config.update(self.as_dict())
            f.truncate()
            json.dump(config, f, indent=4, separators=(',', ': '))
        print('Credentials written to {}'.format(path))
        return True


def load_credentials(file_path):
    if not file_path or not os.path.exists(file_path):
        return Credentials()

    try:
        with open(file_path) as f:
            config = json.load(f)
            creds = Credentials(config)
            creds.path = file_path

            return creds
    except Exception:
        # if we couldn't read the credentials, return empty credentials
        return Credentials()


class OAuthResponseHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        """Respond to a GET request."""
        query = self.path.split('?', 1)[-1]
        query = dict(urllib.parse.parse_qsl(query))
        self.server.query_params = query

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = "<html><head><script>setTimeout(function(){" \
               "window.open('','_self','');window.close()},10)" \
               '</script></head><body>You may close this window.</body></html>'
        self.wfile.write(html)

    def log_message(self, format, *args):
        """Don't log to stdout"""


class LocalOAuth2(object):
    def __init__(self, host=None, client_id=None, client_secret=None,
                 port=None, authorize_endpoint=None, token_endpoint=None):
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.port = port
        self.redirect_uri = 'http://localhost:{}/'.format(port)
        self.authorize_endpoint = authorize_endpoint
        self.token_endpoint = token_endpoint

    def manual_flow(self):
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'all',
            'state': str(uuid.uuid4()),
        }
        query = urllib.parse.urlencode(params)
        url_parts = ('https', self.host, self.authorize_endpoint, None,
                     query, None)
        url = urllib.parse.urlunparse(url_parts)

        webbrowser.open_new(url)

        server_address = ('', self.port)

        httpd = BaseHTTPServer.HTTPServer(server_address, OAuthResponseHandler)

        sa = httpd.socket.getsockname()
        print('Server started on {}:{}...'.format(sa[0], sa[1]))
        httpd.handle_request()

        if httpd.query_params.get('state') == params['state']:
            code = httpd.query_params.get('code')
            credentials = self.request_access_token('authorization_code',
                                                    code=code)
            return credentials

    def request_access_token(self, grant_type, code=None, refresh_token=None):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': grant_type,
            'redirect_uri': self.redirect_uri,
        }
        if code:
            data['code'] = code
        if refresh_token:
            data['refresh_token'] = refresh_token
        response = requests.post(
            'https://{}{}'.format(self.host, self.token_endpoint),
            data=data,
            headers={
              'Accept': 'application/json,application/x-www-form-urlencoded',
            }
        )
        if response.ok:
            token_data = response.json()
            return Credentials(data=token_data)
        return Credentials()

    def refresh_access_token(self, refresh_token):
        print('Acquiring access token...')
        return self.request_access_token(
            'refresh_token',
            refresh_token=refresh_token
        )
