import click
import findup
import json
import os
import re
import sys

from api import client as api_client
from . import auth

CREDENTIALS_FILE = '.optimizely-credentials.json'
CONFIG_FILE = '.optimizely.json'


class Repo(object):
    def __init__(self, root_dir=None, credentials_path=None):
        if credentials_path is None:
            credentials_path = findup.glob(CREDENTIALS_FILE)
        self.credentials = auth.load_credentials(credentials_path)

        # if the creds are expired, refresh the token
        if self.credentials.is_expired() and self.credentials.refresh_token:
            self.credentials = self.oauth.refresh_access_token(
                self.credentials.refresh_token
            )
            self.credentials.write(credentials_path)

        if root_dir:
            self.vcs = 'git'
            self.root = root_dir
        else:
            self.vcs, self.root = self.detect_vcs_and_project_root()
        config = self.load_config()
        self.config = config
        self.platform = config.get('platform')
        self.project_id = config.get('project_id')

        if self.credentials.is_valid():
            self.client = api_client.ApiClient(self.credentials.access_token)
        else:
            self.client = None

    def require_credentials(self):
        if self.credentials.is_valid():
            return

        click.echo('Could not find credentials. '
                   "Make sure you have run 'optimizely init' or specified a "
                   'valid path to a credentials file')
        sys.exit(1)

    def load_config(self, config_path=None):
        root_dir = self.root or '.'
        if config_path is None:
            config_path = os.path.join(root_dir, CONFIG_FILE)
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                return json.load(f)
        return {}

    def save_config(self, config, config_path=None, echo=False):
        root_dir = self.root or '.'
        if config_path is None:
            config_path = os.path.join(root_dir, CONFIG_FILE)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4, separators=(',', ': '))
        if echo:
            relative_path = os.path.relpath(config_path)
            click.echo('Config file written to {}'.format(relative_path))

    def detect_vcs_and_project_root(self):

        # it probably would be smart to detect hg/svn/bazaar/whatever here too
        # if those are things that people are still using
        path = findup.glob('.git')
        if path:
            return 'git', os.path.dirname(path)
        return (None, None)

    def detect_repo_name(self):
        root_dir = self.root or '.'
        return os.path.basename(os.path.abspath(root_dir))

    def detect_project_language(self):
        extension_languages = {
            'cs': 'csharp',
            'java': 'java',
            'js': 'javascript',
            'php': 'php',
            'py': 'python',
            'rb': 'ruby',
        }
        extensions = {}

        extension_regex = re.compile(r'\.(\w+)$', re.IGNORECASE)

        if self.vcs == 'git':
            files = os.popen('git ls-files').readlines()

            for f in files:
                extension_match = re.search(extension_regex, f)
                if not extension_match:
                    continue

                extension = extension_match.group(1)
                if extension not in extension_languages:
                    continue

                if not extensions.get(extension):
                    extensions[extension] = 0
                extensions[extension] += 1

            common_extensions = sorted(extensions, key=extensions.get,
                                       reverse=True)
            if common_extensions:
                return extension_languages[common_extensions][0]
            else:
                return None

    @property
    def oauth(self):
        return auth.LocalOAuth2(
            host='app.optimizely.com',
            client_id=10600571440,
            client_secret='zJWQalwxFk8ApplmaCmQuQiNR66gX-14AD8q1ZE2iAM',
            port=5050,
            authorize_endpoint='/oauth2/authorize',
            token_endpoint='/oauth2/token',
        )
