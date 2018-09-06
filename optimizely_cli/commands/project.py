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

    projects = project.client.list_projects(archived=archived)
    projects = sorted(projects, key=lambda p: getattr(p, sort))

    if not projects:
        click.echo('Unable to list projects')
        return

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
          'label': 'TYPE',
          'accessor': lambda project: 'Web' if project.platform == 'web' else 'Full Stack',
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
