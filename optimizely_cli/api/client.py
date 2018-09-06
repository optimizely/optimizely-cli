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

import requests

from bravado import client as swagger_client
from bravado import requests_client
from bravado_core import validate as bravado_validate
from bravado_core import marshal as bravado_marshal
from bravado_core import model as bravado_model
from bravado_core import unmarshal as bravado_unmarshal


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
        self.quiet = False

    def set_quiet(self, quiet=True):
        self.quiet = quiet

    def list_projects(self, archived=False):
        projects = tools.list_all(self.client.Projects.list_projects,
                                  quiet=self.quiet)
        if archived:
            projects = [p for p in projects if p.status == 'archived']
        else:
            projects = [p for p in projects if p.status != 'archived']

        return projects

    def list_experiments(self, project_id, archived=False):
        items = tools.list_all(self.client.Experiments.list_experiments,
                               params={'project_id': project_id},
                               quiet=self.quiet)

        if archived:
            items = [i for i in items if get(i, 'status') == 'archived']
        else:
            items = [i for i in items if get(i, 'status') != 'archived']

        return items

    def list_audiences(self, project_id, archived=False):
        items = tools.list_all(self.client.Audiences.list_audiences,
                               params={'project_id': project_id},
                               quiet=self.quiet)

        if archived:
            items = [i for i in items if get(i, 'archived') is True]
        else:
            items = [i for i in items if not get(i, 'archived')]

        return items

    def list_events(self, project_id):
        items = tools.list_all(self.client.Events.list_events,
                               params={'project_id': project_id},
                               quiet=self.quiet)

        return items

    def list_features(self, project_id, archived=False):
        items = tools.list_all(self.client.Features.list_features,
                               params={'project_id': project_id},
                               quiet=self.quiet)

        if archived:
            items = [i for i in items if get(i, 'archived') is True]
        else:
            items = [i for i in items if not get(i, 'archived')]

        return items

    def list_environments(self, project_id, archived=False):
        items = tools.list_all(self.client.Environments.list_environments,
                               params={'project_id': project_id},
                               quiet=self.quiet)

        if archived:
            items = [i for i in items if get(i, 'archived') is True]
        else:
            items = [i for i in items if not get(i, 'archived')]

        return items

    def list_groups(self, project_id, archived=False):
        items = tools.list_all(self.client.Groups.list_groups,
                               params={'project_id': project_id},
                               quiet=self.quiet)

        if archived:
            items = [i for i in items if get(i, 'archived') is True]
        else:
            items = [i for i in items if not get(i, 'archived')]

        return items

    def list_attributes(self, project_id, archived=False):
        items = tools.list_all(self.client.Attributes.list_attributes,
                               params={'project_id': project_id},
                               quiet=self.quiet)

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
            data['sdks'] = []

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
        if isinstance(params, dict):
            variations = params.get('variations', [])
            for variation in variations:
                if 'variation_id' in variation:
                    del variation['variation_id']
            if 'campaign_id' in params:
                del params['campaign_id']
        elif isinstance(params, bravado_model.Model):
            variations = params.variations
            for variation in variations:
                if variation.variation_id:
                    variation.variation_id = None
            if params.campaign_id:
                params.campaign_id = None

        experiment, response = self.client.Experiments.create_experiment(
            body=params
        ).result()
        return experiment

    def create_group(self, params=None):
        group, response = self.client.Groups.create_group(
            body=params
        ).result()
        return group

    def create_audience(self, params=None):
        audience, response = self.client.Audiences.create_audience(
            body=params
        ).result()
        return audience

    def create_attribute(self, params=None):
        attribute, response = self.client.Attributes.create_attribute(
            body=params
        ).result()
        return attribute

    def create_custom_event(self, params=None):
        if isinstance(params, bravado_model.Model) and \
           type(params).__name__ == 'Event':
            event_dict = self.obj_to_dict(params)
            params = self.dict_to_obj('CustomEvent', event_dict)
        if hasattr(params, 'id'):
            project_id = params.project_id
        else:
            project_id = params.get('project_id')

        event, response = self.client.Events.create_custom_event(
            project_id=project_id,
            body=params
        ).result()
        return event

    def update_experiment(self, params=None):
        if hasattr(params, 'id'):
            experiment_id = params.id
        else:
            experiment_id = params.get('experiment_id')

        experiment, response = self.client.Experiments.update_experiment(
            experiment_id=experiment_id,
            body=params
        ).result()
        return experiment

    def update_group(self, params=None):
        if hasattr(params, 'id'):
            group_id = params.id
        else:
            group_id = params.get('group_id')

        group, response = self.client.Groups.update_group(
            group_id=group_id,
            body=params
        ).result()
        return group

    def update_audience(self, params=None):
        if hasattr(params, 'id'):
            audience_id = params.id
        else:
            audience_id = params.get('audience_id')

        audience, response = self.client.Audiences.update_audience(
            audience_id=audience_id,
            body=params
        ).result()
        return audience

    def update_attribute(self, params=None):
        if hasattr(params, 'id'):
            attribute_id = params.id
        else:
            attribute_id = params.get('attribute_id')

        attribute, response = self.client.Attributes.update_attribute(
            attribute_id=attribute_id,
            body=params
        ).result()
        return attribute

    def update_custom_event(self, params=None):
        if hasattr(params, 'id'):
            event_id = params.id
        else:
            event_id = params.get('event_id')

        event, response = self.client.Events.update_custom_event(
            event_id=event_id,
            body=params
        ).result()
        return event

    def update_feature(self, params=None):
        if hasattr(params, 'id'):
            feature_id = params.id
        else:
            feature_id = params.get('feature_id')

        feature, response = self.client.Features.update_feature(
            feature_id=feature_id,
            body=params
        ).result()
        return feature

    def update_environment(self, params=None):
        if hasattr(params, 'id'):
            environment_id = params.id
        else:
            environment_id = params.get('environment_id')

        environment, response = self.client.Environments.update_environment(
            environment_id=environment_id,
            body=params
        ).result()
        return environment

    def dict_to_obj(self, entity_type, entity_dict):
        spec = self.client.swagger_spec
        definition = spec.spec_dict['definitions'][entity_type]

        obj = bravado_unmarshal.unmarshal_schema_object(
            spec,
            definition,
            entity_dict
        )
        return obj

    def obj_to_dict(self, obj):
        spec = self.client.swagger_spec
        entity_type = type(obj).__name__
        definition = spec.spec_dict['definitions'][entity_type]
        item = bravado_marshal.marshal_schema_object(
            spec,
            definition,
            obj
        )
        return item

    def read_only_properties(self, obj):
        spec = self.client.swagger_spec
        entity_type = type(obj).__name__
        definition = spec.spec_dict['definitions'][entity_type]

        read_only_properties = [
            k
            for k, p in definition.get('properties').iteritems()
            if p.get('readOnly')
        ]
        return read_only_properties

    def change_type(self, entity_type, entity):
        entity_dict = self.obj_to_dict(entity)
        return self.dict_to_obj(entity_type, entity_dict)

    def validate(self, entity_type, entity_dict):
        spec = self.client.swagger_spec
        definition = spec.spec_dict['definitions'][entity_type]
        bravado_validate.validate_schema_object(
            spec,
            definition,
            entity_dict
        )
