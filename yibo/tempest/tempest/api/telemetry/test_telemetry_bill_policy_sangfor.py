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

import random
from six import moves
from tempest_lib.common.utils import data_utils

from tempest.api.telemetry import base
from tempest import test

_LOOP_TIMES = 3
_PAYMENT_MIN = 1
_PAYMENT_MAX = 100


class TelemetryBillPolicyTestJson(base.BaseTelemetryTest):
    @test.idempotent_id('fe9ca3cf-7093-11e5-9f65-00e06665338b')
    def test_bill_policy_batch_create(self):
        array = []
        meter_names = []
        for _ in moves.xrange(_LOOP_TIMES):
            meter_name = data_utils.rand_name(name='meter-new')
            meter_names.append(meter_name)
            price = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            desc = data_utils.rand_name(name='desc')
            meter_price = (meter_name, price, desc)
            array.append(meter_price)
        body = self.telemetry_client.create_batch_policy(array)

        for meter in meter_names:
            self.addCleanup(
                self.telemetry_client.delete_bill_policy, meter)

        self.assertEqual(201, body.response.status)

    @test.idempotent_id('1a167be1-7094-11e5-9f3a-00e06665338b')
    def test_bill_policy_list_delete(self):
        # create several policy and delete them
        meter_names = []
        for _ in moves.xrange(_LOOP_TIMES):
            meter_name = data_utils.rand_name(name='meter-new')
            price = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            self.telemetry_client.create_bill_policy(
                meter_name, price)
            meter_names.append(meter_name)

        body = self.telemetry_client.list_bill_policy()
        found = [p for p in body if p['meter'] in meter_names]
        self.assertEqual(len(found), len(meter_names), 'policy not created')

        for meter in meter_names:
            self.telemetry_client.delete_bill_policy(meter)
        body = self.telemetry_client.list_bill_policy()
        found = [p for p in body if p['meter'] in meter_names]
        self.assertFalse(any(found), 'policy failed to delete')

    @test.idempotent_id('297da900-7094-11e5-a589-00e06665338b')
    def test_bill_policy_create_with_description(self):
        # Create policy with a description
        meter_name = data_utils.rand_name(name='meter-new')
        price = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
        meter_desc = data_utils.rand_name(name='desc')
        self.telemetry_client.create_bill_policy(meter_name, price,
                                                 description=meter_desc)

        self.addCleanup(
            self.telemetry_client.delete_bill_policy, meter_name)
        body = self.telemetry_client.list_bill_policy()
        found = [p for p in body if p['description'] == meter_desc]
        self.assertTrue(any(found), 'description not create')

    @test.idempotent_id('3333c651-7094-11e5-8f17-00e06665338b')
    def test_bill_policy_create_enabled(self):
        # Create policy with enabled:True
        meter_name = data_utils.rand_name(name='meter-new')
        price = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
        self.telemetry_client.create_bill_policy(meter_name, price,
                                                 enabled=True)

        body = self.telemetry_client.list_bill_policy()
        found = [p for p in body if p['meter'] == meter_name]
        self.assertTrue(found[0]['enabled'],
                        'Enable should be True in response')
        self.telemetry_client.delete_bill_policy(meter_name)

    @test.idempotent_id('3b45a980-7094-11e5-a20b-00e06665338b')
    def test_bill_policy_create_not_enabled(self):
        # Create policy with enabled:False
        meter_name = data_utils.rand_name(name='meter-new')
        price = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
        self.telemetry_client.create_bill_policy(meter_name, price,
                                                 enabled=False)
        body = self.telemetry_client.list_bill_policy()
        found = [p for p in body if p['meter'] == meter_name]
        self.assertFalse(found[0]['enabled'],
                         'Enable should be False in response')
        self.telemetry_client.delete_bill_policy(meter_name)

    @test.idempotent_id('452bb070-7094-11e5-807c-00e06665338b')
    def test_bill_policy_update(self):
        # Update policy attribute of a bill
        meter_name = data_utils.rand_name(name='meter-new')
        price1 = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
        desc1 = data_utils.rand_name(name='desc1')
        self.telemetry_client.create_bill_policy(meter_name, price1,
                                                 description=desc1,
                                                 enabled=True)
        # Delete the bill policy at the end of this method
        self.addCleanup(
            self.telemetry_client.delete_bill_policy, meter_name)

        body = self.telemetry_client.list_bill_policy()
        found = [p for p in body if p['meter'] == meter_name]

        resp1_price = found[0]['price']
        resp1_desc = found[0]['description']

        # Updating some fields with new values
        price2 = price1 + 1
        desc2 = data_utils.rand_name(name='desc2')
        self.telemetry_client.update_bill_policy(meter_name,
                                                 price=price2,
                                                 description=desc2,
                                                 enabled=False)

        body = self.telemetry_client.list_bill_policy()
        found = [p for p in body if p['meter'] == meter_name]

        resp2_price = found[0]['price']
        resp2_desc = found[0]['description']

        self.assertNotEqual(resp1_price, float(resp2_price))
        self.assertNotEqual(resp1_desc, resp2_desc)
        self.assertAlmostEqual(price2, float(resp2_price), 5)
        self.assertEqual(desc2, resp2_desc)
        self.assertEqual(False, found[0]['enabled'])
