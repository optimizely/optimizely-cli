import errno
import hashlib
import os
import yaml

ENTITY_TO_DIR_MAPPING = {
    'Experiment': 'experiments',
    'Group': 'groups',
    'Audience': 'audiences',
    'Attribute': 'attributes',
    'CustomEvent': 'custom_events',
    'Event': 'custom_events',
    'Feature': 'features',
    'Environment': 'environments',
}
REVERSE_ENTITY_MAPPING = {v: k for k, v in ENTITY_TO_DIR_MAPPING.iteritems()}


def ensure_dir_exists(dir_path):
    if os.path.isdir(dir_path):
        return

    try:
        os.makedirs(dir_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dir_path):
            pass
        else:
            raise


class StoredEntity(object):
    def __init__(self, repo=None, data_dir=None, entity=None):
        self.repo = repo
        self.data_dir = data_dir
        self.entity = entity

    @classmethod
    def file_sha1(cls, file_path):
        sha1 = hashlib.sha1()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha1.update(chunk)
        return sha1.hexdigest()

    @property
    def entity_dir(self):
        return os.path.join(
            self.repo.root,
            self.data_dir,
            ENTITY_TO_DIR_MAPPING[self.entity_type]
        )

    @property
    def entity_type(self):
        return type(self.entity).__name__

    @property
    def name(self):
        name = getattr(self.entity, 'key', None)
        if not name:
            name = getattr(self.entity, 'name', None)
            if name:
                name = name.replace(' ', '_').lower()
            else:
                name = getattr(self.entity, 'id')
        return name

    @property
    def filename(self):
        return '{}.yaml'.format(self.name)

    @property
    def full_path(self):
        return os.path.join(self.entity_dir, self.filename)

    @property
    def relative_path(self):
        return os.path.relpath(self.full_path)

    def to_dict(self):
        return self.repo.client.obj_to_dict(self.entity)

    def as_update(self):
        entity_type = '{}{}'.format(self.entity_type, 'Update')
        return self.repo.client.change_type(entity_type, self.entity)

    def serialized_content(self):
        raw_data = self.to_dict()
        content = yaml.safe_dump(raw_data, default_flow_style=False)
        read_only_properties = self.repo.client.read_only_properties(self.entity)

        lines = []
        for line in content.splitlines():
            property_name = line.split(':')[0]

            if property_name in read_only_properties:
                lines.append('{:<60} # READ-ONLY'.format(line))
            else:
                lines.append(line)

        return "\n".join(lines)

    def sha1(self):
        content = self.serialized_content()
        sha1 = hashlib.sha1()
        sha1.update(content)
        return sha1.hexdigest()

    def store(self):
        path = self.full_path

        if os.path.isfile(path):
            # if the file already exists and is the same there's nothing to do
            file_signature = self.file_sha1(path)
            if file_signature == self.sha1():
                return

        ensure_dir_exists(self.entity_dir)
        content = self.serialized_content()
        with open(path, 'w') as outfile:
            outfile.write(content)

        return True
