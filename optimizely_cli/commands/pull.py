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

from optimizely_cli import main
from optimizely_cli import local_store


@main.cli.command()
@click.option(
    '-p', '--project-id',
    type=click.INT,
    help='Project ID to pull data for',
)
@click.option(
    '--data-dir',
    default='optimizely',
    help='Directory to load data from',
)
@click.option(
    '-d', '--delete', is_flag=True,
    help='Delete extra files not on the server',
)
@click.pass_obj
def pull(repo, project_id, data_dir, delete):
    """Pull down the current state of an Optimizely project"""
    repo.require_credentials()

    if project_id is None:
        project_id = repo.project_id

    click.echo('Getting optimizely data...')

    files = set(local_store.get_all_files(data_dir, repo.root))

    entities = local_store.fetch(
        repo,
        project_id=project_id,
        data_dir=data_dir
    )
    for entity in entities:
        written_to = entity.store()
        if written_to:
            click.echo('Data written to {}'.format(entity.relative_path))
        if entity.full_path in files:
            files.remove(entity.full_path)

    if files:
        if delete:
            click.echo('Deleting extra entities not found on the server:')
        else:
            click.echo('Extra entities not found on the server:')
        for leftover_file in files:
            relative_path = os.path.relpath(leftover_file)
            click.echo(relative_path)
            if delete:
                os.remove(leftover_file)
        click.echo('')

    click.echo('Optimizely data is up to date.')
