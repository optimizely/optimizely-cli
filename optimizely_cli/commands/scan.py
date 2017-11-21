import click

from optimizely_cli import main


@main.cli.command()
def scan():
    """Scan a repository for Optimizely references"""
    click.echo('Scanned')
