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


from tempest_lib import exceptions as lib_exc

from tempest.api.telemetry import sf_base
from tempest_lib.common.utils import data_utils
from tempest import test


class TelemetryAlarmTestJSON(sf_base.SfBaseTelemetryTest):

    # test alarm of three meters including cpu, memory and disk
    def test_create_alarm_all_params(self):
        tenant = self.create_tenant()
        params = {
            'tenant_id': tenant['id'],
            'name': data_utils.rand_name('sf_alarm'),
            'description': data_utils.rand_name('sf_desc'),
            'period': 1,
            'enabled': True,
            'cpu_enabled': True,
            'memory_enabled': True,
            'disk_enabled': True,
            'cpu_threshold': 90,
            'memory_threshold': 90,
            'disk_threshold': 90,
            'email_enabled': True,
            'sms_enabled': True
            }
        alarm_body = self.sf_create_alarm(**params)

        for k, v in zip(alarm_body, self.meters):
            self.assertEqual(self.policy["%s_threshold" % v],
                             alarm_body['rule']['threshold'])
            self.assertEqual(self.action, alarm_body['alarm_actions'])

    # test cpu alarm and evaluation period
    def test_create_alarm_cpu_period(self):
        tenant = self.create_tenant()
        params = {
            'tenant_id': tenant['id'],
            'name': data_utils.rand_name('sf_alarm'),
            'period': 5,
            'enabled': True,
            'cpu_enabled': True,
            'cpu_threshold': 90,
            'email_enabled': True
            }
        alarm_body = self.sf_create_alarm(**params)

        for k, v in zip(alarm_body, self.meters):
            self.assertEqual(self.policy["%s_threshold" % v],
                             alarm_body['rule']['threshold'])

    # test cpu alarm and memory alarm
    def test_create_alarm_cpu_memory(self):
        tenant = self.create_tenant()
        params = {
            'tenant_id': tenant['id'],
            'name': data_utils.rand_name('sf_alarm'),
            'description': data_utils.rand_name('sf_desc'),
            'period': 5,
            'enabled': True,
            'cpu_enabled': True,
            'cpu_threshold': 80,
            'memory_enabled': True,
            'memory_threshold': 50,
            'sms_enabled': True
            }
        alarm_body = self.sf_create_alarm(**params)

        for k, v in zip(alarm_body, self.meters):
            self.assertEqual(self.policy["%s_threshold" % v],
                             alarm_body['rule']['threshold'])

    # test alarm no notify
    def test_create_alarm_no_notify(self):
        tenant = self.create_tenant()
        params = {
            'tenant_id': tenant['id'],
            'name': data_utils.rand_name('sf_alarm'),
            'period': 1,
            'enabled': True,
            'memory_enabled': True,
            'memory_threshold': 90,
            }
        alarm_body = self.sf_create_alarm(**params)

        alarm = alarm_body[2]
        self.assertEqual(90, alarm['rule']['threshold'])



