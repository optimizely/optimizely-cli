import click
import getpass
import requests

from optimizely_cli import main
from optimizely_cli import repo
from optimizely_cli.api import client as api_client


def verify_token(token):
    try:
        resp = requests.get(
            'https://api.optimizely.com/v2/projects',
            params={'per_page': 1},
            headers={'Authorization': 'Bearer {}'.format(token)}
        )
        resp.raise_for_status()
    except Exception as e:
        print e
        return False
    return True


@main.cli.command()
@click.option(
    '-n', '--project-name',
    help='Project name',
)
@click.option(
    '-i', '--project-id',
    help='Project ID',
)
@click.option(
    '-c', '--create', is_flag=True,
    help='Create a new project',
)
@click.option(
    '-t', '--personal-token', is_flag=True,
    help='Specify a Personal Access Token instead of doing an OAuth Login',
)
@click.pass_obj
def init(project, project_name, project_id, create, personal_token):
    """Link an Optimizely project with your repository"""

    store_credentials = False
    credentials = project.credentials
    if project.credentials.path:
        click.echo('Credentials found in {}'.format(project.credentials.path),
                   err=True)
    if not credentials or not credentials.is_valid():
        if personal_token:
            click.echo('First visit https://app.optimizely.com/v2/profile/api '
                       'to create a new access token')
            token = getpass.getpass('Enter the token you created here: ')
            credentials.access_token = token
            store_credentials = True
        else:
            click.echo('Opening a browser to get an access token...')
            credentials = project.oauth.manual_flow()
            store_credentials = True

    # make sure the token actually works
    click.echo('Verifying token...')
    if verify_token(credentials.access_token):
        click.echo('Token is valid')
    else:
        click.echo('Invalid token, try again.')
        click.echo('Maybe you copy/pasted the wrong thing?')
        return

    if store_credentials:
        credentials.write(repo.CREDENTIALS_FILE)
        click.echo('Do not add this file to version control!')
        click.echo('It should stay private\n')

    if project.project_id:
        click.echo('Config successfully loaded')
        click.echo('You are all set up and ready to go')
        return

    client = api_client.ApiClient(credentials.access_token)

    if not project_name:
        project_name = project.detect_repo_name()
    if project_id:
        click.echo("Checking for an existing project with ID {}...".format(
                   project_id))
    else:
        click.echo("Checking for an existing project named '{}'...".format(
                   project_name))
    projects = client.list_projects()
    if project_id:
        discovered_projects = [
            p
            for p in projects
            if p.id == int(project_id)
        ]
    else:
        discovered_projects = [
            p
            for p in projects
            if p.name == project_name
        ]
    if discovered_projects:
        project.project_id = discovered_projects[0].id
        click.echo('Found project (id: {})'.format(project.project_id))
    elif create and project_name:
        # create the project
        new_project = client.create_project(
            platform=None,
            name=project_name
        )

        if not new_project:
            click.echo('Unable to create a new project')
            return

        project_id = new_project.id
        if project_id:
            project.project_id = project_id
            click.echo('Successfully created project (id: {})'.format(
                       project_id))
    else:
        if project_id:
            click.echo('No project found with id: {}'.format(project_id))
        else:
            click.echo('No project found with name: {}'.format(project_name))
        click.echo('Use -p <project_name> or -i <project_id> to use an '
                   'existing project or -c to create a new one')
        return

    # write the config file so we have baseline context
    config = {
        'project_id': project.project_id,
    }
    project.save_config(config, echo=True)
