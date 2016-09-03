#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import time
import json
import uuid

from oslo_utils import timeutils
from tempest_lib.common.utils import data_utils

from tempest import config
from tempest import exceptions
from tempest.api.telemetry import base

CONF = config.CONF


class SfBaseTelemetryTest(base.BaseTelemetryTest):
    """Base test case class for all Telemetry API tests."""
    credentials = ['primary', 'admin']

    @classmethod
    def setup_clients(cls):
        super(SfBaseTelemetryTest, cls).setup_clients()
        cls.identity_client = cls.os_adm.identity_client

    @classmethod
    def resource_setup(cls):
        super(SfBaseTelemetryTest, cls).resource_setup()
        cls.tenant_ids = []

        cls.meters = ['cpu', 'memory', 'disk']

        cls.action = ["cplog://", "email://", "sms://"]

        # NOTE(fty):
        # the meter name in base has deprecated since
        # we have modified the pipeline
        cls.vm_basic_meters = ['vm.cpu_util', 'vm.memory_capacity',
                               'vm.cpu_number', 'vm.memory_resident']

        cls.vm_disk_meters = ['vm.disk_device_capacity',
                              'vm.disk_device_allocation',
                              'vm.disk_device_usage_util ']

        cls.vm_disk_io_meters = ['vm.disk_read_bytes_rate',
                                 'vm.disk_read_requests_rate',
                                 'vm.disk_write_requests_rate',
                                 'vm.disk_write_bytes_rate']

        cls.vm_network_meters = ['vm.network_incoming_bytes_rate',
                                 'vm.network_outgoing_bytes_rate']

        cls.volume_meters = ['volume.disk_device_capacity ',
                             'volume.disk_device_usage_util',
                             'volume.disk_device_allocation']

    @staticmethod
    def _generate_threshold(
            combination_id, type, policy, action, query, meter):
        threshold = {
            'type': 'threshold',
            'alarm_id': policy['%s_id' % type],
            'name': '%s:%s' % (combination_id, type),
            'enabled': policy['enabled'] and policy['%s_enabled' % type],
            'description': json.dumps(policy),
            'project_id': policy['tenant_id'],
            'repeat_actions': True,
            'alarm_actions': action,
            'threshold_rule': {
                'evaluation_periods': int(policy['periods']),
                'meter_name': meter,
                'threshold': policy['%s_threshold' % type],
                'statistic': 'avg',
                'comparison_operator': 'gt',
                'query': query,
            }
        }
        return threshold

    @classmethod
    def sf_create_alarm(cls, **kwargs):

        combination_id = str(uuid.uuid4())
        cpu_id = str(uuid.uuid4())
        memory_id = str(uuid.uuid4())
        disk_id = str(uuid.uuid4())
        cls.policy = {
            'id': combination_id,
            'cpu_id': cpu_id,
            'memory_id': memory_id,
            'disk_id': disk_id,
            'name': kwargs.get('name'),
            'description': kwargs.get('description'),
            'type': kwargs.get('type', 'vm'),
            'tenant_id': kwargs['tenant_id'],
            'periods': kwargs.get('periods', 1),
            'enabled': kwargs.get('enabled', False),
            'cpu_enabled': kwargs.get('cpu_enabled', False),
            'memory_enabled': kwargs.get('memory_enabled', False),
            'disk_enabled': kwargs.get('disk_enabled', False),
            'cpu_threshold': kwargs.get('cpu_threshold', 0),
            'memory_threshold': kwargs.get('memory_threshold', 0),
            'disk_threshold': kwargs.get('disk_threshold', 0),
            'email_enabled': kwargs.get('email_enabled', False),
            'sms_enabled': kwargs.get('sms_enabled', False),
            'timestamp': timeutils.isotime(),
        }

        combination = {
            'type': 'sf_combination',
            'alarm_id': combination_id,
            'enabled': cls.policy['enabled'],
            'name': combination_id,
            'description': json.dumps(cls.policy),
            'project_id': cls.policy['tenant_id'],
            'sf_combination_rule': {
                'alarm_ids': [
                    cpu_id, memory_id, disk_id
                ]
            }
        }

        cls.telemetry_client.create_alarm(**combination)

        action = ['cplog://']
        if cls.policy['email_enabled']:
            action.append('email://')
        if cls.policy['sms_enabled']:
            action.append('sms://')

        query = [{
            'field': 'project_id',
            'op': 'eq',
            'value': cls.policy['tenant_id'],
        }]

        threshold_cpu = cls._generate_threshold(
            combination_id,
            type='cpu',
            policy=cls.policy,
            action=action,
            query=query,
            meter='stats/vm/resource_id/vm.cpu_util'
        )
        cpu_body = cls.telemetry_client.create_alarm(**threshold_cpu)

        threshold_memory = cls._generate_threshold(
            combination_id,
            type='memory',
            policy=cls.policy,
            action=action,
            query=query,
            meter='stats/vm/resource_id/vm.memory_usage_util'
        )
        mem_body = cls.telemetry_client.create_alarm(**threshold_memory)

        threshold_disk = cls._generate_threshold(
            combination_id,
            type='disk',
            policy=cls.policy,
            action=action,
            query=query,
            meter='stats/vm_disk/resource_id/vm.disk_device_usage_util'
        )
        disk_body = cls.telemetry_client.create_alarm(**threshold_disk)

        alarm_body = [cpu_body, mem_body, disk_body]
        return alarm_body

    @classmethod
    def create_tenant(cls):
        body = cls.identity_client.create_tenant(
            data_utils.rand_name(name='tenant-new'))
        cls.tenant_ids.append(body['id'])
        return body

    def await_statistics(self, **kwargs):
        """
        This method is to wait for statistics to add it to database.
        """
        timeout = CONF.compute.build_timeout
        start = timeutils.utcnow()
        while timeutils.delta_seconds(start, timeutils.utcnow()) < timeout:
            body = self.telemetry_client.list_stats(**kwargs)
            if body:
                return body
            time.sleep(CONF.compute.build_interval)

        raise exceptions.TimeoutException(
            'Samples has not been added to the '
            'database within %d seconds' % CONF.compute.build_timeout)
