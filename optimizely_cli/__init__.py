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

from optimizely_cli import main
from optimizely_cli.commands import init # noqa
from optimizely_cli.commands import project # noqa
from optimizely_cli.commands import experiment # noqa
from optimizely_cli.commands import event # noqa
from optimizely_cli.commands import audience # noqa
from optimizely_cli.commands import attribute # noqa
from optimizely_cli.commands import group # noqa
from optimizely_cli.commands import pull # noqa
from optimizely_cli.commands import push # noqa
from optimizely_cli.commands import feature # noqa
from optimizely_cli.commands import environment # noqa

cli = main.cli

if __name__ == '__main__':
    cli()
