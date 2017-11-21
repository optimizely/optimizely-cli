import click

from optimizely_cli import main

PLATFORM_BREAKDOWN = [
    ('Web', ['web']),
    ('Full Stack', ['csharp', 'java', 'javascript', 'node', 'php', 'python',
                    'ruby']),
    ('Mobile', ['android', 'ios']),
    ('Over-the-Top', ['android_tv', 'tv_os']),
]

PLATFORMS = []
for key, value in PLATFORM_BREAKDOWN:
    PLATFORMS += value


@main.cli.group()
def project():
    """List, create, and manage Optimizely projects"""


@project.command()
@click.option(
    '-p', '--platform',
    type=click.Choice(PLATFORMS),
    help='Project platform to filter by',
)
@click.option(
    '-s', '--sort',
    default='name',
    show_default=True,
    type=click.Choice(['id', 'name', 'platform', 'created']),
    help='Attribute to sort by',
)
@click.option(
    '-a', '--archived', is_flag=True,
    help='Show archived projects',
)
@click.pass_obj
def list(project, platform, sort, archived):
    """List projects in Optimizely"""
    project.require_credentials()

    if sort == 'platform':
        sort = 'platform_sdk'

    projects = project.client.list_projects(archived=archived)
    projects = sorted(projects, key=lambda p: getattr(p, sort))

    if not projects:
        click.echo('Unable to list projects')
        return

    projects = [
        p for p in projects
        if platform is None or platform == p.get('platform_sdk')
    ]

    columns = [
      {
          'field': 'id',
          'label': 'PROJECT ID',
          'width': 13,
      },
      {
          'field': 'name',
          'truncate': 30,
      },
      {
          'field': 'platform_sdk',
          'label': 'PLATFORM',
          'width': 10,
      },
      {
          'field': 'created',
          'type': 'date',
          'width': 12,
      },
    ]
    main.print_table(columns, projects)


@project.command()
@click.option(
    '-p', '--platform',
    type=click.Choice(PLATFORMS),
    help='Project platform',
)
@click.option(
    '-n', '--name',
    help='Project name',
)
@click.option(
    '-d', '--description',
    help='Project description (optional)',
)
@click.option(
    '-x', '--non-interactive', is_flag=True,
    help='Non-interactive mode. Uses detected platform & language',
)
@click.pass_obj
def create(project, platform, name, description, non_interactive):
    """
    Create a new Optimizely project

    You can always change the name and description later.
    """
    project.require_credentials()

    if platform is None:
        detected_language = project.detect_project_language()
        if non_interactive:
            platform = detected_language
        else:
            click.echo('Optimizely can be used to run experiments on many '
                       'different platforms.\nCreate a project based on the '
                       'platform you\'re using.\n')
            click.echo('Valid platforms are:\n')
            for platform_type, platforms in PLATFORM_BREAKDOWN:
                click.echo('{:>12.12}: {}'.format(platform_type,
                                                  ', '.join(platforms)))
            click.echo('')
            platform = click.prompt('Platform', type=click.Choice(PLATFORMS),
                                    default=detected_language)

    if name is None:
        detected_name = project.detect_repo_name()
        if non_interactive:
            name = detected_name
        else:
            name = click.prompt('Name', default=detected_name)

    if description is None and not non_interactive:
        description = click.prompt('Description (optional)',
                                   default='', show_default=False)

    click.echo('\nCreating project...')
    new_project = project.client.create_project(platform, name, description)

    if not new_project:
        click.echo('Unable to create a new project')
        return

    project_id = new_project.id
    if project_id:
        click.echo('Successfully created project (id: {})'.format(project_id))
