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
def attribute():
    """Manage Audience Attributes"""


@attribute.command()
@click.option(
    '-p', '--project-id',
    type=click.INT,
    help='Project ID to list attributes for',
)
@click.option(
    '-s', '--sort',
    default='name',
    show_default=True,
    type=click.Choice(['id', 'name', 'created', 'last_modified']),
    help='Attribute to sort by',
)
@click.option(
    '-a', '--archived', is_flag=True,
    help='Show archived attributes',
)
@click.pass_obj
def list(project, project_id, sort, archived):
    """List Attributes in a project"""
    project.require_credentials()

    if project_id is None:
        project_id = project.project_id

    click.echo('Attributes for project id: {}'.format(project_id))

    attributes = project.client.list_attributes(
        project_id,
        archived=archived
    )
    attributes = sorted(attributes, key=lambda e: getattr(e, sort))

    if not attributes:
        click.echo('Unable to list exclusion attributes')
        return

    columns = [
        {
            'field': 'id',
            'label': 'ATTRIBUTE ID',
            'width': 13,
        },
        {
            'field': 'key',
            'truncate': 30,
        },
        {
            'field': 'last_modified',
            'type': 'date',
            'width': 13,
        },
    ]
    main.print_table(columns, attributes)
