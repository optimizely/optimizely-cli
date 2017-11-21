import click
import errno
import os
import yaml


from optimizely_cli import main
from optimizely_cli.api import client as api_client


OPTIMIZELY_DATA_DIR = 'optimizely'


def write_file_for_entity(root_dir, entity_type, entity):
    entity_dir = os.path.join(root_dir, OPTIMIZELY_DATA_DIR, entity_type)
    try:
        os.makedirs(entity_dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(entity_dir):
            pass
        else:
            raise
    path = os.path.join(entity_dir, '{}.yml'.format(entity.get('id')))
    with open(path, 'w') as outfile:
        yaml.safe_dump(entity, outfile, default_flow_style=False)

    relative_path = os.path.relpath(path)
    click.echo('Data written to {}'.format(relative_path))


@main.cli.command()
@click.option(
    '-p', '--project-id',
    type=click.INT,
    help='Project ID to pull data for',
)
@click.pass_obj
def pull(project, project_id):
    """Pull down the current state of your entire Optimizely project"""
    project.require_credentials()

    if project_id is None:
        project_id = project.project_id

    project.client = api_client.ApiClient(project.token, use_models=False)

    entities = {}

    click.echo('Getting experiments...')
    entities['experiments'] = project.client.list_experiments(project_id)

    click.echo('Getting groups...')
    entities['groups'] = project.client.list_groups(project_id)

    click.echo('Getting audiences...')
    entities['audiences'] = project.client.list_audiences(project_id)

    click.echo('Getting attributes...')
    entities['attributes'] = project.client.list_attributes(project_id)

    click.echo('Getting events...')
    entities['events'] = project.client.list_events(project_id)

    for entity_type in entities.keys():
        for entity in entities[entity_type]:
            write_file_for_entity(project.root, entity_type, entity)
