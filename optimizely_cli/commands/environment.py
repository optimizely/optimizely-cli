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

from optimizely_cli import main


@main.cli.group()
def environment():
    """Manage Environments"""


@environment.command()
@click.option(
    '-p', '--project-id',
    type=click.INT,
    help='Project ID to list environments for',
)
@click.option(
    '-s', '--sort',
    default='key',
    show_default=True,
    type=click.Choice(['id', 'key', 'created', 'last_modified']),
    help='Attribute to sort by',
)
@click.option(
    '-a', '--archived', is_flag=True,
    help='Show archived environments',
)
@click.pass_obj
def list(project, project_id, sort, archived):
    """List Environments in a project"""
    project.require_credentials()

    if project_id is None:
        project_id = project.project_id

    click.echo('Environments for project id: {}'.format(project_id))

    environments = project.client.list_environments(
        project_id,
        archived=archived
    )
    environments = sorted(environments, key=lambda e: getattr(e, sort))

    if not environments:
        click.echo('Unable to list environments')
        return

    columns = [
        {
            'field': 'id',
            'label': 'ENVIRONMENT ID',
            'width': 14,
        },
        {
            'field': 'key',
            'truncate': 30,
        },
        {
            'field': 'description',
            'truncate': 40,
        },
        {
            'field': 'url',
            'accessor': lambda env: env.datafile.url,
            'truncate': 70,
        },
        {
            'field': 'revision',
            'accessor': lambda env: env.datafile.revision,
            'truncate': 10,
        },
    ]
    main.print_table(columns, environments)
