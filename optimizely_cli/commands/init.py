import click
import getpass
import json
import os
import requests

from optimizely_cli import main
from optimizely_cli import api


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
@click.pass_obj
def init(project):
    """Link an Optimizely project with your repository"""

    store_credentials = False
    token = project.token
    if project.credentials_path:
        click.echo('Credentials found in {}'.format(project.credentials_path),
                   err=True)
    if not token:
        click.echo('First visit https://app.optimizely.com/v2/profile/api '
                   'to create a new access token')
        token = getpass.getpass('Enter the token you created here: ')
        store_credentials = True

    # make sure the token actually works
    click.echo('Verifying token...')
    if verify_token(token):
        click.echo('Token is valid')
    else:
        click.echo('Invalid token, try again.')
        click.echo('Maybe you copy/pasted the wrong thing?')
        return

    if store_credentials:
        # create the credentials file user-readable/writable only (0600)
        fdesc = os.open(main.CREDENTIALS_FILE, os.O_WRONLY | os.O_CREAT, 0o600)
        with os.fdopen(fdesc, 'w') as f:
            json.dump({'token': token}, f, indent=4, separators=(',', ': '))
        click.echo('Credentials written to {}'.format(main.CREDENTIALS_FILE))
        click.echo('Do not add this file to version control!')
        click.echo('It should stay private\n')

    if project.platform and project.project_id:
        click.echo('Config successfully loaded')
        click.echo('You are all set up and ready to go')
        return

    click.echo('Checking for an existing project...')
    detected_name = project.detect_repo_name()
    detected_language = project.detect_project_language()
    projects = api.projects.list_projects(project.token)
    discovered_project = [
        p
        for p in projects
        if p.get('name') == detected_name
        and p.get('platform_sdk') == detected_language
    ]
    if discovered_project:
        project.project_id = discovered_project[0].get('id')
        project.platform = discovered_project[0].get('platform_sdk')
        click.echo('Found project (id: {})'.format(project.project_id))
    else:
        # create the project
        new_project = api.projects.create_project(
            project.token,
            detected_language,
            detected_name
        )

        if not new_project:
            click.echo('Unable to create a new project')
            return

        project_id = new_project.get('id')
        if project_id:
            project.project_id = project_id
            project.platform = detected_language
            click.echo('Successfully created project (id: {})'.format(
                       project_id))

    # write the config file so we have baseline context
    config = {
        'project_id': project.project_id,
        'platform': project.platform,
    }
    project.save_config(config, echo=True)
