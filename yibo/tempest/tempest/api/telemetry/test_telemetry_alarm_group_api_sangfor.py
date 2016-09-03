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

from tempest.api.telemetry import base
from tempest_lib.common.utils import data_utils
from tempest import test


_LOOP_TIMES = 2


class TelemetryAlarmGroupAPITestJSON(base.BaseTelemetryTest):
    @classmethod
    def resource_setup(cls):
        super(TelemetryAlarmGroupAPITestJSON, cls).resource_setup()
        cls.rule = {'meter_name': 'bill/tenant//balance',
                    'comparison_operator': 'lt',
                    'threshold': 10.0,
                    'period': 70}
        for i in range(_LOOP_TIMES):
            cls.create_alarm(threshold_rule=cls.rule)

    @test.attr(type="smoke")
    @test.idempotent_id('b29463b0-6d87-11e5-b3a0-00e06665338b')
    def test_update_get_alarms(self):
        # update alarming object of an alarm policy
        alarm_body = self.create_alarm(threshold_rule=self.rule)
        alarms = ['vm.test', 'tenant.tenant']
        body = self.telemetry_client.get_alarm(alarm_body['alarm_id'])
        self.assertEqual([], body['id'])

        self.telemetry_client.update_alarm_group(
            alarm_body['alarm_id'], alarms)
        body = self.telemetry_client.get_alarm(alarm_body['alarm_id'])
        self.assertEqual(alarms, body['id'])
        self.assertEqual('null', body['detail'])

    @test.idempotent_id('71ede5c0-6ef4-11e5-b10c-00e06665338b')
    def test_loop_update_alarms(self):
        # Loop to update alarming object
        alarm_body = self.create_alarm(threshold_rule=self.rule)
        alarm_object = []

        for i in range(_LOOP_TIMES):
            alarm_name = data_utils.rand_name('vm.')
            alarms = [alarm_name]
            self.telemetry_client.update_alarm_group(
                alarm_body['alarm_id'], alarms)
            body = self.telemetry_client.get_alarm(alarm_body['alarm_id'])
            alarm_object.append(body)

        self.assertNotIn(alarm_object[0]['id'], alarm_object[1]['id'])
        self.assertEqual(alarms, alarm_object[1]['id'])

    @test.attr(type="smoke")
    @test.idempotent_id('fa85da9e-6ef4-11e5-9b17-00e06665338b')
    def test_get_alarm_group(self):
        alarms = []
        for i in range(_LOOP_TIMES):
            alarm_name = data_utils.rand_name('vm.')
            alarm = [alarm_name]
            alarms.extend(alarm)
            self.telemetry_client.update_alarm_group(self.alarm_ids[i], alarm)

        body = self.telemetry_client.get_alarm_group()

        for i in range(_LOOP_TIMES):
            self.assertEqual((self.alarm_ids[i]),
                             (eval(body[0]['detail'])[alarms[i]][0]))
        self.assertEqual(alarms.sort(), body[0]['id'].sort())

    @test.idempotent_id('0fab36f0-6ef5-11e5-83c5-00e06665338b')
    def test_get_multi_alarms(self):
        # alarm object has multiple alarm policy
        alarms = []
        for i in range(_LOOP_TIMES):
            alarm_name = data_utils.rand_name('vm.')
            alarms.append(alarm_name)

        for j in range(_LOOP_TIMES):
            self.telemetry_client.update_alarm_group(
                self.alarm_ids[j], alarms)

        body = self.telemetry_client.get_alarm_group()

        for i in range(_LOOP_TIMES):
            self.assertEqual(self.alarm_ids,
                             (eval(body[0]['detail']))[alarms[i]])
        self.assertEqual(alarms.sort(), body[0]['id'].sort())

    @test.idempotent_id('18093e51-6ef5-11e5-8991-00e06665338b')
    def test_get_spec_alarm(self):
        # get all alarm policy of specific alarm object
        self.create_alarm(threshold_rule=self.rule)
        alarms = []
        alarm_name = data_utils.rand_name('vm.')
        alarms.append(alarm_name)

        for i in range(_LOOP_TIMES):
            alarm = [alarm_name]
            self.telemetry_client.update_alarm_group(self.alarm_ids[i], alarm)

        body = self.telemetry_client.get_spec_alarm_policy(alarm_name)
        self.assertEqual(self.alarm_ids[:2], body['id'])

    @test.idempotent_id('1f6df191-6ef5-11e5-8db0-00e06665338b')
    def test_nonexistent_alarm(self):
        alarm_name = data_utils.rand_name('vm.')
        body = self.telemetry_client.get_spec_alarm_policy(alarm_name)
        self.assertEqual([], body['id'], "list of alarm id "
                                         "of nonexistent alarm "
                                         "object should be empty")



