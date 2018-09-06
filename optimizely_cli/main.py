import click
import datetime

from . import repo
from . import version


def format_date(dt):
    if type(dt) == str:
        dt = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.%fZ')
    return datetime.datetime.strftime(dt, '%b %m, %Y')


def print_table(columns, items):
    template_items = []
    labels = []
    for column in columns:
        width = column.get('width') or column.get('truncate')
        template_items.append('{:<%d.%d}' % (width, width))
        if column.get('label'):
            labels.append(column.get('label'))
        else:
            labels.append(column.get('field').upper().replace('_', ' '))
    template = '   '.join(template_items)
    click.echo(template.format(*labels))

    for item in items:
        row = []
        for column in columns:
            if column.get('accessor'):
                value = column.get('accessor')(item)
            else:
                value = getattr(item, column.get('field'))
            if column.get('type') == 'date':
                value = format_date(value)
            else:
                value = str(value)

            truncate_chars = column.get('truncate')
            if truncate_chars and len(value) > truncate_chars - 3:
                value = value[:truncate_chars - 3] + '...'

            row.append(value)

        click.echo(template.format(*row))


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Version {}'.format(version.__version__))
    ctx.exit()


@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help='Show the version and exit')
@click.option('--root', type=click.Path(exists=True),
              help='Project root directory override')
@click.pass_context
def cli(ctx, root):
    """Optimizely Full Stack command-line utility for managing experiments"""
    ctx.obj = repo.Repo(root)
