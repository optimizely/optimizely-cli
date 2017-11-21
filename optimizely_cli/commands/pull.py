import click
import errno
import hashlib
import os
import yaml

from optimizely_cli import main
from optimizely_cli.api import client as api_client


OPTIMIZELY_DATA_DIR = 'optimizely'


def file_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha1.update(chunk)
    return sha1.hexdigest()


def string_sha1(content):
    sha1 = hashlib.sha1()
    sha1.update(content)
    return sha1.hexdigest()


def make_directory(dir_path):
    if os.path.isdir(dir_path):
        return

    try:
        os.makedirs(dir_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dir_path):
            pass
        else:
            raise


def store_entity(root_dir, entity_type, entity):
    content = yaml.safe_dump(entity, default_flow_style=False)
    signature = string_sha1(content)

    entity_dir = os.path.join(root_dir, OPTIMIZELY_DATA_DIR, entity_type)
    path = os.path.join(entity_dir, '{}.yaml'.format(entity.get('id')))

    if os.path.isfile(path):
        # if the file already exists and is the same there's nothing to do
        file_signature = file_sha1(path)
        if file_signature == signature:
            return

    make_directory(entity_dir)
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
            store_entity(project.root, entity_type, entity)

    click.echo('Optimizely data is up to date')
