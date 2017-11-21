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
def list(project, project_id, sort, archived):
    """List Events in a project"""
    project.require_credentials()

    if project_id is None:
        project_id = project.project_id

    click.echo('Events for project id: {}'.format(project_id))

    events = project.client.list_events(project_id)
    events = sorted(events, key=lambda e: getattr(e, sort))

    if not events:
        click.echo('Unable to list events')
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
