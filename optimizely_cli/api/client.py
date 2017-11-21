import requests
from bravado import client as swagger_client
from bravado import requests_client

from . import constants
from . import tools


def get(entity, attr):
    if isinstance(entity, dict):
        return entity.get(attr)
    return getattr(entity, attr)


class ApiClient(object):
    def __init__(self, token, **kwargs):
        http_client = requests_client.RequestsClient()
        http_client.set_api_key(
            constants.HOST, 'Bearer {}'.format(token),
            param_name='Authorization',
            param_in='header',
        )

        config = {
            'also_return_response': True,
            # TODO: fix the API so we don't need this off
            'validate_responses': False,
        }
        config.update(kwargs)
        self.client = swagger_client.SwaggerClient.from_url(
            constants.SWAGGER_URL,
            http_client=http_client,
            config=config,
        )

    def list_projects(self, archived=False):
        projects = tools.list_all(self.client.Projects.list_projects)
        if archived:
            projects = [p for p in projects if p.status == 'archived']
        else:
            projects = [p for p in projects if p.status != 'archived']

        for project in projects:
            if project.platform == 'custom':
                project['platform_sdk'] = project.sdks[0] or 'custom'
            else:
                project['platform_sdk'] = project.platform

        return projects

    def list_experiments(self, project_id, archived=False):
        items = tools.list_all(self.client.Experiments.list_experiments,
                               params={'project_id': project_id})

        if archived:
            items = [i for i in items if get(i, 'status') == 'archived']
        else:
            items = [i for i in items if get(i, 'status') != 'archived']

        return items

    def list_audiences(self, project_id, archived=False):
        items = tools.list_all(self.client.Audiences.list_audiences,
                               params={'project_id': project_id})

        if archived:
            items = [i for i in items if get(i, 'archived') is True]
        else:
            items = [i for i in items if not get(i, 'archived')]

        return items

    def list_events(self, project_id):
        items = tools.list_all(self.client.Events.list_events,
                               params={'project_id': project_id})

        return items

    def list_groups(self, project_id, archived=False):
        items = tools.list_all(self.client.Groups.list_groups,
                               params={'project_id': project_id})

        if archived:
            items = [i for i in items if get(i, 'archived') is True]
        else:
            items = [i for i in items if not get(i, 'archived')]

        return items

    def list_attributes(self, project_id, archived=False):
        items = tools.list_all(self.client.Attributes.list_attributes,
                               params={'project_id': project_id})

        if archived:
            items = [i for i in items if get(i, 'archived') is True]
        else:
            items = [i for i in items if not get(i, 'archived')]

        return items

    def create_project(self, platform, name, description=None):
        data = {
            'name': name
        }
        if platform == 'web':
            data['platform'] = platform
        else:
            data['platform'] = 'custom'
            data['sdks'] = [platform]

        if description:
            data['description'] = description

        tools.display_loading()
        message = None
        try:
            project, response = self.client.Projects.create_project(
                body=data
            ).result()
            return project
        except requests.exceptions.ConnectionError as e:
            message = "Can't to connect to {}".format(constants.HOST)
        except Exception as e:
            message = e
        finally:
            tools.clear_loading(message)

    def create_experiment(self, params=None):
        experiment, response = self.client.Experiments.create_experiment(
            body=params
        ).result()
        return experiment
        #    "project_id":9179861621,
        #    "key":"second_test",
        #    "description":"",
        #    "variations":[
        #        {
        #            "guid":"14FC2DB3-6006-480A-BA15-1A0CE32CA5F7",
        #            "weight":5000,
        #            "api_name":"a"
        #        },
        #        {
        #            "guid":"235E5FDD-E6F3-4A4F-A703-3D064BCB62E3",
        #            "weight":5000,
        #            "api_name":"b"
        #        }
        #    ],
        #    "audience_ids":[],
        #    "group_id":null,
        #    "percentage_included":10000,
        #    "layer_id":9178796000
