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
def event():
    """List, create, and manage Optimizely events"""


@event.command()
@click.option(
    '-p', '--project-id',
    type=click.INT,
    help='Project ID to list events for',
)
@click.option(
    '-s', '--sort',
    default='key',
    show_default=True,
    type=click.Choice(['id', 'key', 'created']),
    help='Attribute to sort by',
)
@click.option(
    '-a', '--archived', is_flag=True,
    help='Show archived events',
)
@click.pass_obj
def list(repo, project_id, sort, archived):
    """List Events in a project"""
    repo.require_credentials()

    if project_id is None:
        project_id = repo.project_id

    click.echo('Events for project id: {}'.format(project_id))

    events = repo.client.list_events(project_id)
    events = sorted(events, key=lambda e: getattr(e, sort))

    if not events:
        click.echo('No events to list')
        return

    if archived:
        events = [e for e in events if e.archived is True]
    else:
        events = [e for e in events if e.archived is False]

    columns = [
      {
          'field': 'id',
          'label': 'EVENT ID',
          'width': 13,
      },
      {
          'field': 'key',
          'truncate': 30,
      },
      {
          'field': 'description',
          'truncate': 60,
      },
      {
          'field': 'created',
          'type': 'date',
          'width': 12,
      },
    ]
    main.print_table(columns, events)


@event.command()
@click.argument('event_key')
@click.option(
    '-d', '--description',
    help='Event description (optional)',
)
@click.pass_obj
def create(repo, event_key, description):
    """
    Create a new custom event in your project

    Custom tracking events allow you to capture and report on visitor actions
    or events.

    You can always change the key and description later.
    """
    repo.require_credentials()

    click.echo('Creating event...')
    data = {
        'key': event_key,
        'name': event_key,
        'description': description,
        'project_id': repo.project_id,
    }
    new_event = repo.client.create_custom_event(data)

    if not new_event:
        click.echo('Unable to create a new event')
        return

    if new_event.id:
        msg = "Successfully created event '{}' (id: {})"
        click.echo(msg.format(new_event.key, new_event.id))
