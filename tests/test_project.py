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

from click.testing import CliRunner

from optimizely_cli import main


def test_no_credentials():
    runner = CliRunner()
    result = runner.invoke(main.cli, args=['project', 'list'])
    assert result.exit_code == 1
    assert result.output == 'Could not find credentials. Make sure you have ' \
        "run 'optimizely init' or specified a valid " \
        'path to a credentials file\n'
