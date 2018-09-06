import os
from multiprocessing import pool

from optimizely_cli import stored_entity

all_list_endpoints = ['Experiment', 'Group', 'Audience', 'Attribute',
                      'CustomEvent', 'Feature', 'Environment']


def get_list_endpoints(repo):
    return {
        'Experiment': repo.client.list_experiments,
        'Group': repo.client.list_groups,
        'Audience': repo.client.list_audiences,
        'Attribute': repo.client.list_attributes,
        'Event': repo.client.list_events,
        'CustomEvent': repo.client.list_events,
        'Feature': repo.client.list_features,
        'Environment': repo.client.list_environments,
    }


def get_create_endpoints(repo):
    return {
        'Experiment': repo.client.create_experiment,
        'Group': repo.client.create_group,
        'Audience': repo.client.create_audience,
        'Attribute': repo.client.create_attribute,
        'Event': repo.client.create_custom_event,
        'CustomEvent': repo.client.create_custom_event,
    }


def get_update_endpoints(repo):
    return {
        'Experiment': repo.client.update_experiment,
        'Group': repo.client.update_group,
        'Audience': repo.client.update_audience,
        'Attribute': repo.client.update_attribute,
        'Event': repo.client.update_custom_event,
        'CustomEvent': repo.client.update_custom_event,
        'Feature': repo.client.update_feature,
        'Environment': repo.client.update_environment,
    }


def get_all_files(data_dir, repo_root=None):
    files = []
    for root, dirs, file_list in os.walk(data_dir):
        files += [
            os.path.join(root, name)
            for name in file_list
            if name.endswith('.yaml')
        ]
    if repo_root:
        return [os.path.join(repo_root, f) for f in files]
    else:
        return files


def fetch(repo, project_id=None, data_dir=None, entity_types=None):
    repo.client.set_quiet(True)

    if project_id is None:
        project_id = repo.project_id

    list_endpoints = get_list_endpoints(repo)

    endpoints = []
    if entity_types and len(entity_types) > 0:
        for entity_type in entity_types:
            endpoint = list_endpoints[entity_type]
            endpoints.append(endpoint)
    else:
        endpoints = [
            v for k, v in list_endpoints.iteritems()
            if k in all_list_endpoints
        ]

    entities = []
    thread_pool = pool.ThreadPool(5)
    results = []
    for endpoint in endpoints:
        results.append(thread_pool.apply_async(endpoint, args=(project_id,)))

    thread_pool.close()
    thread_pool.join()
    entities += [e for r in results for e in r.get(timeout=10)]

    stored_entities = []
    for entity_obj in entities:
        entity = stored_entity.StoredEntity(
            repo=repo,
            data_dir=data_dir,
            entity=entity_obj
        )
        stored_entities.append(entity)

    return stored_entities
