#   Copyright 2018 Optimizely
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import re
import sys
import logging
import requests
from six.moves.urllib import parse

from . import constants

logger = logging.getLogger(__name__)


def list_all(operation, params=None, quiet=False):
    items = []

    if params is None:
        params = {}

    if not params.get('per_page'):
        params['per_page'] = constants.DEFAULT_PAGE_SIZE

    if not quiet:
        display_loading()
    message = None
    try:
        page_items, response = operation(**params).result()
        items += page_items
    except requests.exceptions.ConnectionError as e:
        message = "Can't to connect to {}".format(constants.HOST)
        return []
    except Exception as e:
        message = e
        return []
    finally:
        clear_loading(message)

    # if there's a link to the next page, fetch it
    next_link = response._delegate.links.get('next')
    if next_link and next_link.get('url'):
        next_url = parse.urlparse(next_link.get('url'))
        next_params = {}
        for key, value in parse.parse_qsl(next_url.query):
            if re.match(r'^\d+$', value):
                value = int(value)
            next_params[key] = value
        items += list_all(operation, params=next_params)

    return items


def display_loading():
    sys.stdout.write('loading...')
    sys.stdout.flush()


def clear_loading(message):
    sys.stdout.write('\r')
    if message:
        sys.stdout.write('{}\n'.format(message))
    sys.stdout.flush()
