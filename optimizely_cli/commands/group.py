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
def group():
    """Manage Optimizely exclusion groups"""


@group.command()
@click.option(
    '-p', '--project-id',
    type=click.INT,
    help='Project ID to list exclusion groups for',
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
    help='Show archived exclusion groups',
)
@click.pass_obj
def list(project, project_id, sort, archived):
    """List Exclusion Groups in a project"""
    project.require_credentials()

    if project_id is None:
        project_id = project.project_id

    click.echo('Exclusion Groups for project id: {}'.format(project_id))

    groups = project.client.list_groups(
        project_id,
        archived=archived
    )
    groups = sorted(groups, key=lambda e: getattr(e, sort))

    if not groups:
        click.echo('Unable to list exclusion groups')
        return

    for group in groups:
        group['experiments'] = len(group.entities)
        available_traffic = 10000
        for entity in group.entities:
            available_traffic -= entity.weight
        group['available_traffic'] = available_traffic

    columns = [
        {
            'field': 'id',
            'label': 'GROUP ID',
            'width': 13,
        },
        {
            'field': 'name',
            'truncate': 30,
        },
        {
            'field': 'experiments',
            'truncate': 11,
        },
        {
            'field': 'available_traffic',
            'truncate': 17,
        },
        {
            'field': 'last_modified',
            'type': 'date',
            'width': 13,
        },
        {
            'field': 'created',
            'type': 'date',
            'width': 12,
        },
    ]
    main.print_table(columns, groups)
