import click

from optimizely_cli import main


@main.cli.group()
def feature():
    """Manage Features"""


@feature.command()
@click.option(
    '-p', '--project-id',
    type=click.INT,
    help='Project ID to list features for',
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
    help='Show archived features',
)
@click.pass_obj
def list(project, project_id, sort, archived):
    """List Features in a project"""
    project.require_credentials()

    if project_id is None:
        project_id = project.project_id

    click.echo('Features for project id: {}'.format(project_id))

    features = project.client.list_features(
        project_id,
        archived=archived
    )
    features = sorted(features, key=lambda e: getattr(e, sort))

    if not features:
        click.echo('Unable to list features')
        return

    def get_enabled(feature):
        env = feature.environments.get('Production')
        if env and env.rollout_rules[0].enabled:
            return 'On'
        return 'Off'

    def get_percent(feature):
        env = feature.environments.get('Production')
        if env and env.rollout_rules[0].enabled:
            return '{}%'.format(env.rollout_rules[0].percentage_included / 100.0)
        return '-'

    columns = [
        {
            'field': 'id',
            'label': 'FEATURE ID',
            'width': 13,
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
            'label': 'Enabled',
            'accessor': get_enabled,
            'truncate': 12,
        },
        {
            'label': 'Rollout',
            'accessor': get_percent,
            'truncate': 12,
        },
        {
            'field': 'created',
            'type': 'date',
            'width': 12,
        },
        {
            'field': 'last_modified',
            'type': 'date',
            'width': 13,
        },
    ]
    main.print_table(columns, features)
