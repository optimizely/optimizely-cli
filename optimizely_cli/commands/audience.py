import click

from optimizely_cli import main


@main.cli.group()
def audience():
    """Manage Optimizely audiences"""


@audience.command()
@click.option(
    '-p', '--project-id',
    type=click.INT,
    help='Project ID to list audiences for',
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
    help='Show archived audiences',
)
@click.pass_obj
def list(project, project_id, sort, archived):
    """List Audiences in a project"""
    project.require_credentials()

    if project_id is None:
        project_id = project.project_id

    click.echo('Audiences for project id: {}'.format(project_id))

    audiences = project.client.list_audiences(
        project_id,
        archived=archived
    )
    audiences = sorted(audiences, key=lambda e: getattr(e, sort))

    if not audiences:
        click.echo('Unable to list audiences')
        return

    columns = [
        {
            'field': 'id',
            'label': 'AUDIENCE ID',
            'width': 13,
        },
        {
            'field': 'name',
            'truncate': 30,
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
    main.print_table(columns, audiences)
