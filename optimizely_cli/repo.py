import click
import findup
import json
import os
import re
import sys

from api import client as api_client

CREDENTIALS_FILE = '.optimizely-credentials.json'
CONFIG_FILE = '.optimizely.json'


class Repo(object):
    def __init__(self, root_dir=None, credentials_path=None):
        self.token, self.credentials_path = self.load_credentials(
            credentials_path
        )
        if root_dir:
            self.vcs = 'git'
            self.root = root_dir
        else:
            self.vcs, self.root = self.detect_vcs_and_project_root()
        config = self.load_config()
        self.config = config
        self.platform = config.get('platform')
        self.project_id = config.get('project_id')

        if self.token:
            self.client = api_client.ApiClient(self.token)
        else:
            self.client = None

    def load_credentials(self, credentials_path=None):
        if credentials_path is None:
            credentials_path = findup.glob(CREDENTIALS_FILE)
        if credentials_path:
            with open(credentials_path) as f:
                config = json.load(f)
                return (config.get('token'), credentials_path)

        return (None, None)

    def require_credentials(self):
        if self.token:
            return

        click.echo('Could not find credentials. '
                   "Make sure you have run 'optimizely init' or specified a "
                   'valid path to a credentials file')
        sys.exit(1)

    def load_config(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(self.root, CONFIG_FILE)
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                return json.load(f)
        return {}

    def save_config(self, config, config_path=None, echo=False):
        if config_path is None:
            config_path = os.path.join(self.root, CONFIG_FILE)
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

    def detect_repo_name(self):
        return os.path.basename(self.root)

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
