# Copyright 2017, Kevin Carter <kevin@cloudnull.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Get nova ram quotas."""

import click

from monitorstack import utils
from monitorstack.cli import pass_context


DOC = """Get nova ram quotas."""
COMMAND_NAME = 'os_vm_quota_ram'


@click.command(COMMAND_NAME, short_help=DOC)
@click.option('--config-file',
              help='OpenStack configuration file',
              default='openstack.ini')
@pass_context
def cli(ctx, config_file):
    """Get nova ram quotas."""
    setattr(cli, '__doc__', DOC)

    # Lower level import because we only want to load this module
    # when this plugin is called.
    from monitorstack.utils import os_utils as ost

    output = {
        'measurement_name': COMMAND_NAME,
        'meta': {
            'quotas': 'ram'
        },
        'variables': {}
    }
    nova_config = utils.read_config(config_file=config_file)['nova']
    interface = nova_config.pop('interface', 'internal')
    _ost = ost.OpenStack(os_auth_args=nova_config)
    try:
        variables = output['variables']
        for project in _ost.get_projects():
            limits = _ost.get_compute_limits(
                project_id=project.id,
                interface=interface
            )
            variables[project.name] = int(limits['quota_set']['ram'])
    except Exception as exp:
        output['exit_code'] = 1
        output['message'] = '{} failed -- {}'.format(
            COMMAND_NAME,
            utils.log_exception(exp=exp)
        )
    else:
        output['exit_code'] = 0
        output['message'] = '{} is ok'.format(COMMAND_NAME)
    finally:
        return output
