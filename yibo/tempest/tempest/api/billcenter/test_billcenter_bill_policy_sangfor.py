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

import json
import random
from six import moves
from tempest_lib.common.utils import data_utils

from tempest.api.billcenter import base
from tempest import test

_LOOP_TIMES = 3
_PAYMENT_MIN = 1
_PAYMENT_MAX = 100


class BillcenterBillPolicyTestJson(base.BaseBillcenterTest):

    def _help_batch_policy_create(self):
        policies = []
        self.meter_names = []
        for _ in moves.xrange(_LOOP_TIMES):
            meter_name = data_utils.rand_name(name='meter-policy')
            self.meter_names.append(meter_name)
            price = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            meter_price = (meter_name, price)
            policies.append(meter_price)
        return policies

    def _help_single_policy_create(self):
        policies = []
        meter_name = data_utils.rand_name(name='meter-policy')
        price = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
        meter_price = (meter_name, price)
        policies.append(meter_price)
        return policies

    @test.idempotent_id('fe9ca3cf-7093-11e5-9f65-00e06665338b')
    def test_policy_create_with_region(self):
        policies = self._help_batch_policy_create()
        region = "guangdong"
        body = self.billcenter_client.create_bill_policy(region, policies)
        self.assertEqual(201, body.response.status)
        self.assertEqual(region, body['region'],
                         'region incorrect in response')
        self.assertEqual("sync", body['status'])

        get_body = self.billcenter_client.get_bill_policy(region)
        self.assertEqual(region, get_body['region'],
                         'region incorrect in lookup')

    @test.idempotent_id('1a167be1-7094-11e5-9f3a-00e06665338b')
    def test_bill_policy_region_create_list(self):
        # create policies for several regions and list them
        regions = []
        policies = self._help_batch_policy_create()
        for _ in moves.xrange(_LOOP_TIMES):
            region = "guangdong"
            self.billcenter_client.create_bill_policy(
                region, policies)
            regions.append(region)

        body = self.billcenter_client.list_bill_policy()
        found = [p for p in body if p['region'] in regions]
        self.assertEqual(len(found), 1, 'policy not created')

    @test.idempotent_id('297da900-7094-11e5-a589-00e06665338b')
    def test_policy_create_with_description(self):
        # Create policy with a description
        policies = self._help_single_policy_create()
        region = "guangdong"
        desc = data_utils.rand_name(name='desc')
        body = self.billcenter_client.create_bill_policy(
            region, policies, description=desc)

        self.assertEqual(desc, body['description'])
        self.assertEqual("sync", body['status'])

        get_body = self.billcenter_client.get_bill_policy(region)
        self.assertEqual(desc, get_body['description'],
                         'description incorrect in lookup')

    @test.idempotent_id('3333c651-7094-11e5-8f17-00e06665338b')
    def test_bill_policy_create_enabled(self):
        # Create policy with enabled:True
        policies = self._help_single_policy_create()
        region = "guangdong"
        body = self.billcenter_client.create_bill_policy(
            region, policies, enabled=True)

        en1 = body['policy'][0]['enabled']
        self.assertTrue(en1, 'Enable should be True in response')
        self.assertEqual("sync", body['status'])

        get_body = self.billcenter_client.get_bill_policy(region)
        en2 = get_body['policy'][0]['enabled']
        self.assertTrue(en2, 'Enable should be True in lookup')

    @test.idempotent_id('3b45a980-7094-11e5-a20b-00e06665338b')
    def test_bill_policy_create_not_enabled(self):
        # Create policy with enabled:False
        policies = self._help_single_policy_create()
        region = "guangdong"
        body = self.billcenter_client.create_bill_policy(
            region, policies, enabled=False)

        en1 = body['policy'][0]['enabled']
        self.assertEqual('false', str(en1).lower(),
                         'Enable should be False in response')
        self.assertEqual("sync", body['status'])

        get_body = self.billcenter_client.get_bill_policy(region)
        en2 = get_body['policy'][0]['enabled']
        self.assertEqual('false', str(en2).lower(),
                         'Enable should be False in lookup')

    @test.idempotent_id('452bb070-7094-11e5-807c-00e06665338b')
    def test_bill_policy_update(self):
        # Update policy attribute of a bill
        policies = []
        prices = []
        for _ in moves.xrange(_LOOP_TIMES):
            meter_name = data_utils.rand_name(name='meter-policy')
            price = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            prices.append(price)
            meter_price = [meter_name, price]
            policies.append(meter_price)
        region = "guangdong"
        self.billcenter_client.create_bill_policy(region, policies)

        get_body = self.billcenter_client.list_bill_policy()
        found = [p for p in get_body if p['region'] == region]

        resp1_price = found[0]['policy'][0]['price']
        resp2_price = found[0]['policy'][1]['price']
        resp_meter = found[0]['policy'][0]['meter']
        # resp1_desc = found[0]['policy'][0]['description']

        # Updating some fields with new values
        new_policies = policies

        new_policies[0][1] += 1
        new_policies[1][1] += 2
        new_price1 = new_policies[0][1]
        new_price2 = new_policies[1][1]
        self.billcenter_client.update_bill_policy(region, new_policies)

        get_body = self.billcenter_client.list_bill_policy()
        found = [p for p in get_body if p['region'] == region]

        resp_new_price1 = found[0]['policy'][0]['price']
        resp_new_price2 = found[0]['policy'][1]['price']
        resp_new_meter = found[0]['policy'][0]['meter']
        # resp2_desc = found[0]['policy'][0]['description']

        self.assertNotEqual(float(resp1_price), float(new_price1))
        self.assertNotEqual(float(resp2_price), float(new_price2))
        # self.assertNotEqual(resp1_desc, resp2_desc)
        self.assertAlmostEqual(new_price1, float(resp_new_price1), )
        self.assertAlmostEqual(new_price1, float(resp_new_price2), 4)
        self.assertEqual(resp_meter, resp_new_meter)
        # self.assertEqual(desc2, resp2_desc)
        # self.assertEqual(False, found[0]['enabled'])
