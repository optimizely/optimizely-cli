import click

from optimizely_cli import main
from optimizely_cli import local_store


@main.cli.command()
@click.option(
    '-p', '--project-id',
    type=click.INT,
    help='Project ID to pull data for',
)
@click.option(
    '-d', '--data-dir',
    default='optimizely',
    help='Directory to load data from',
)
@click.pass_obj
def pull(project, project_id, data_dir):
    """Pull down the current state of an Optimizely project"""
    project.require_credentials()

    if project_id is None:
        project_id = project.project_id

    click.echo('Getting optimizely data...')

    entities = local_store.fetch(
        project,
        project_id=project_id,
        data_dir=data_dir
    )
    for entity in entities:
        written_to = entity.store()
        if written_to:
            click.echo('Data written to {}'.format(written_to))

    click.echo('Optimizely data is up to date.')
