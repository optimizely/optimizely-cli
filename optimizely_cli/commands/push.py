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

import click
import os
import sys
import yaml

from jsonschema import exceptions

from optimizely_cli import main
from optimizely_cli import stored_entity
from optimizely_cli import local_store


@main.cli.command()
@click.option(
    '-p', '--project-id',
    type=click.INT,
    help='Project ID to push data to',
)
@click.option(
    '--data-dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True,
                    readable=True, resolve_path=True),
    default='optimizely',
    help='Directory load to data from',
)
@click.option(
    '-f', '--for-real', is_flag=True,
    help='Actually push updates, instead of reporting what would be pushed',
)
@click.argument('entity_files', nargs=-1, type=click.Path(exists=True))
@click.pass_obj
def push(project, project_id, data_dir, for_real, entity_files):
    """Push back local data to an Optimizely project"""
    project.require_credentials()

    if project_id is None:
        project_id = project.project_id

    files = []
    if entity_files:
        files = list(entity_files)
    else:
        files = local_store.get_all_files(data_dir)

    if not files:
        raise click.UsageError('No files specified')

    entities = {}
    entity_list = []

    for file_path in files:
        with open(file_path) as f:
            entity_dict = yaml.safe_load(f)

        entity_dir = os.path.basename(os.path.dirname(file_path))

        entity_type = stored_entity.REVERSE_ENTITY_MAPPING[entity_dir]
        obj = project.client.dict_to_obj(entity_type, entity_dict)
        try:
            project.client.validate(entity_type, entity_dict)
        except exceptions.ValidationError as e:
            click.echo('An error occurred validating {}'.format(file_path))
            if len(e.path) > 0:
                click.echo("field '{}': {}".format(e.path.pop(), e.message))
            else:
                click.echo(e.message)
            sys.exit(1)

        entity = stored_entity.StoredEntity(
            repo=project,
            data_dir=data_dir,
            entity=obj
        )
        entities[entity_type] = entity
        entity_list.append(entity)

    # now that we have the entities to send and know that they're valid,
    # fetch them to see what operation we actually have to do
    # e.g. create or update
    remote_entities = local_store.fetch(
        project,
        project_id=project_id,
        data_dir=data_dir,
        entity_types=entities.keys(),
    )
    canonical_files = {}
    remote_ids = {}
    for entity in remote_entities:
        canonical_files[entity.full_path] = entity
        remote_ids[entity.entity.id] = entity

    updates, creates, deletes = [], [], []
    for local_entity in entity_list:
        canonical_file = canonical_files.get(local_entity.full_path)
        remote_id = remote_ids.get(local_entity.entity.id)
        if canonical_file and remote_id and \
           canonical_file.sha1() == local_entity.sha1():
            # everything is the same and there's nothing to do here
            continue

        if not canonical_file and not remote_id:
            # if we don't have the file or id, then it's new
            creates.append(local_entity)

        if canonical_file and canonical_file.sha1() != local_entity.sha1():
            updates.append(local_entity)
        elif remote_id:
            # this id already exists, so it's an update
            updates.append(local_entity)

    create_endpoints = local_store.get_create_endpoints(project)
    update_endpoints = local_store.get_update_endpoints(project)
    for item in creates:
        click.echo('Create {}: {}'.format(item.entity_type, item.name))
        if for_real:
            endpoint = create_endpoints.get(item.entity_type)
            obj = item.entity
            if hasattr(obj, 'project_id') and obj.project_id != project_id:
                obj.project_id = project_id

            endpoint(obj)

    for item in updates:
        click.echo('Update {}: {}'.format(item.entity_type, item.name))
        if for_real:
            endpoint = update_endpoints.get(item.entity_type)
            endpoint(item.as_update())

    if not creates and not updates and not deletes:
        click.echo('No changes to push')
        sys.exit(0)

    if for_real:
        click.echo('Changes have been pushed.')
        click.echo('Go to https://app.optimizely.com/v2/projects/{} '
                   'to see your changes'.format(project_id))
    else:
        click.echo('Running without --for-real. No changes have been made')
