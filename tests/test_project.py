from click.testing import CliRunner

from optimizely_cli import main


def test_no_credentials():
    runner = CliRunner()
    result = runner.invoke(main.cli, args=['project', 'list'])
    assert result.exit_code == 1
    assert result.output == 'Could not find credentials. Make sure you have ' \
        "run 'optimizely init' or specified a valid " \
        'path to a credentials file\n'
