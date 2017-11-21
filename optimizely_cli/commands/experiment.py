import click
import re

from optimizely_cli import main

API_NAME_REGEX = re.compile('^[a-z0-9_\-]+$', re.IGNORECASE)


@main.cli.group()
def experiment():
    """List, create, and manage Optimizely experiments"""


@experiment.command()
@click.option(
    '-p', '--project-id',
    type=click.INT,
    help='Project ID to list experiments for',
)
@click.option(
    '-s', '--sort',
    default='key',
    show_default=True,
    type=click.Choice(['id', 'key', 'created']),
    help='Attribute to sort by',
)
@click.option(
    '-a', '--archived', is_flag=True,
    help='Show archived experiments',
)
@click.pass_obj
def list(project, project_id, sort, archived):
    """List Experiments in a project"""
    project.require_credentials()

    if project_id is None:
        project_id = project.project_id

    click.echo('Experiments for project id: {}'.format(project_id))

    experiments = project.client.list_experiments(
        project_id,
        archived=archived
    )
    experiments = sorted(experiments, key=lambda e: getattr(e, sort))

    if not experiments:
        click.echo('Unable to list experiments')
        return

    columns = [
      {
          'field': 'id',
          'label': 'EXPERIMENT ID',
          'width': 13,
      },
      {
          'field': 'key',
          'truncate': 30,
      },
      {
          'field': 'status',
          'width': 12,
      },
      {
          'field': 'last_modified',
          'type': 'date',
          'width': 13,
      },
      {
          'field': 'created',
          'type': 'date',
          'width': 12,
      },
    ]
    main.print_table(columns, experiments)


@experiment.command()
@click.argument('key')
@click.option(
    '-d', '--description',
    help='Experiment description (optional)',
)
@click.option(
    '-p', '--percentage-included',
    default=10000,
    type=click.IntRange(0, 10000, clamp=True),
    help="""Percentage of total traffic to include in your experiment
         (expressed as a number from 0 to 10000)""",
)
@click.option(
    '-v', '--variation',
    multiple=True,
    nargs=2,
    type=click.Tuple([unicode, click.IntRange(0, 10000, clamp=True)]),
    help="""Variations (specified as: key weight) to include in the experiment.
         Weights must add up to 10000. Use '-' for auto-balanced weights""",
)
@click.option(
    '-p', '--project-id',
    type=click.INT,
    help='Project ID to create the experiments in',
)
@click.option(
    '-i', '--interactive', is_flag=True,
    help='Non-interactive mode. Uses detected platform & language',
)
@click.pass_obj
def create(project, key, description, percentage_included, variation,
           project_id, interactive):
    """
    Create a new experiment
    """
    project.require_credentials()

    if description is None and interactive:
        description = click.prompt('Description (optional)',
                                   default='', show_default=False)

    variation_list = []
    if not variation and interactive:
        while True:
            variation_key = click.prompt('Variation Key (or Enter to stop)')
            if not variation_key:
                break
            weight = click.prompt('Traffic Distribution')
            variation_list.append({
              'api_name': variation_key,
              'weight': weight,
            })

    # balance weights where needed
    unallocated_weight = 10000
    unallocated_count = 0
    for key, weight in variation:
        if weight == '' or weight == '-':
            unallocated_count += 1
            variation_list.append({
              'api_name': key,
            })
        else:
            unallocated_weight -= weight
            variation_list.append({
              'api_name': key,
              'weight': weight,
            })

    allocations = []
    if unallocated_count > 0:
        remainder = unallocated_weight % unallocated_count
        for i in xrange(0, unallocated_count):
            allocations.append(unallocated_weight / unallocated_count)

        for allocation in allocations:
            if remainder == 0:
                break
            allocation += 1
            remainder -= 1

    total_weight = 0
    for variation_dict in variation_list:
        if not variation_dict.get('weight'):
            variation_dict['weight'] = allocations.pop()
        total_weight += variation_dict.get('weight')

    if total_weight != 10000:
        raise Exception('Weights must add up to 10000')

    click.echo('\nCreating experiment...')
    new_experiment = project.client.create_experiment({
        'key': key,
        'description': description,
        'percentage_included': percentage_included,
        'variations': variation_list,
        'project_id': project_id or project.project_id,
    })

    if not new_experiment:
        click.echo('Unable to create a new experiment')
        return

    if new_experiment.id:
        click.echo('Successfully created experiment (id: {})'.format(
                   new_experiment.id))
