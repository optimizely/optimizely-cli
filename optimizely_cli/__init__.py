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
