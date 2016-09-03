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

_ALARM_THRESHOLD_BALANCE = 100
_LOOP_TIMES = 3
_PAYMENT_MIN = 1
_PAYMENT_MAX = 10
_PAYMENT_MAX_THRESHOLD = 200


class TelemetryBillPayTestJson(base.BaseTelemetryTest):
    credentials = ['primary', 'admin']

    @classmethod
    def setup_clients(cls):
        super(TelemetryBillPayTestJson, cls).setup_clients()
        cls.identity_client = cls.os_adm.identity_client

    @test.idempotent_id('8c9ad94f-7093-11e5-92bc-00e06665338b')
    def test_create_bill_pay(self):
        # create payment for tenant
        tenant_name = data_utils.rand_name(name='tenant-new')
        tenant = self.identity_client.create_tenant(tenant_name)

        self.addCleanup(self.identity_client.delete_tenant, tenant['id'])
        payment = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
        body = self.telemetry_client.create_bill_pay(tenant['id'], payment)

        self.assertEqual(tenant['id'], body['tenant_id'])
        self.assertEqual(201, body.response.status)

    @test.idempotent_id('bbb56980-7093-11e5-b36a-00e06665338b')
    def test_list_bill_pay(self):
        # list all the payments of tenants
        tenants = []
        for _ in moves.xrange(_LOOP_TIMES):
            tenant_name = data_utils.rand_name(name='tenant-new')
            tenant = self.identity_client.create_tenant(tenant_name)
            self.addCleanup(self.identity_client.delete_tenant, tenant['id'])
            tenants.append(tenant)
        tenant_ids = map(lambda x: x['id'], tenants)

        for tenant in tenants:
            payment = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            self.telemetry_client.create_bill_pay(tenant['id'], payment)

        body = self.telemetry_client.list_bill_pay()
        found = [p for p in body if p['tenant_id'] in tenant_ids]
        self.assertEqual(len(found), len(tenants), 'bill pay not create')

    @test.idempotent_id('c97f3a4f-7093-11e5-b223-00e06665338b')
    def test_pay_history(self):
        # payment history of a specific tenant
        payments = []
        tenant_name = data_utils.rand_name(name='tenant-history')
        tenant = self.identity_client.create_tenant(tenant_name)

        for _ in moves.xrange(_LOOP_TIMES):
            payment = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            payments.append(payment)
            self.telemetry_client.create_bill_pay(tenant['id'], payment)

        self.addCleanup(self.identity_client.delete_tenant, tenant['id'])

        query = ('tenant_id', 'eq', tenant['id'])
        body = self.telemetry_client.list_bill_pay(query)

        self.assertEqual(tenant['id'], body[0]['tenant_id'])
        self.assertEqual(_LOOP_TIMES, len(body))
        for i in range(_LOOP_TIMES):
            self.assertAlmostEqual(payments[i], float(body[i]['payment']), 5)

    @test.idempotent_id('e81d79b0-8464-11e5-b1c7-00e06665338b')
    def test_bill_pay_total(self):
        # verify the total amount of payment of tenant is correct
        payments = []
        tenant_name = data_utils.rand_name(name='tenant-new')
        tenant = self.identity_client.create_tenant(tenant_name)
        for _ in moves.xrange(_LOOP_TIMES):
            payment = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            payments.append(payment)
            self.telemetry_client.create_bill_pay(tenant['id'], payment)

        self.addCleanup(self.identity_client.delete_tenant, tenant['id'])
        body = self.telemetry_client.list_bill_pay()
        expected_total_payment = sum(payments)
        actual_total_payment = [total_pay['payment'] for total_pay in body if
                                total_pay['tenant_id'] == tenant['id']]
        actual_total_payment = map(float, actual_total_payment)
        self.assertAlmostEqual(expected_total_payment,
                               sum(actual_total_payment),
                               5)

    @test.idempotent_id('e677c321-7093-11e5-a8ed-00e06665338b')
    def test_balance_accumulate(self):
        # test the balance accumulate correctly
        payments = []
        tenant_name = data_utils.rand_name(name='tenant-balance')
        tenant = self.identity_client.create_tenant(tenant_name)

        for _ in moves.xrange(_LOOP_TIMES):
            payment = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            payments.append(payment)
            self.telemetry_client.create_bill_pay(tenant['id'], payment)

        self.addCleanup(self.identity_client.delete_tenant, tenant['id'])
        body = self.telemetry_client.get_bill_balance(tenant['id'])

        expected_balance = sum(payments)
        actual_balance = body['balance']
        self.assertAlmostEqual(expected_balance, float(actual_balance), 5)

    @test.idempotent_id('eb93bee1-7093-11e5-a84a-00e06665338b')
    def test_bill_balance(self):
        # list the balance of specific tenants
        tenants = []
        payments = []

        for _ in moves.xrange(_LOOP_TIMES):
            tenant_name = data_utils.rand_name(name='tenant-new')
            tenant = self.identity_client.create_tenant(tenant_name)
            self.addCleanup(self.identity_client.delete_tenant, tenant['id'])
            tenants.append(tenant)
        tenant_ids = map(lambda x: x['id'], tenants)

        for tenant in tenants:
            payment = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            payments.append(payment)
            self.telemetry_client.create_bill_pay(tenant['id'], payment)

        for i in range(_LOOP_TIMES):
            body = self.telemetry_client.get_bill_balance(tenant_ids[i])
            self.assertEqual(tenant_ids[i], body['tenant_id'])
            self.assertAlmostEqual(payments[i], float(body['balance']), 5)

    @test.idempotent_id('f5c833f0-7093-11e5-b03c-00e06665338b')
    def test_balance_alarm(self):
        # list the tenants whose balance below a specified threshold
        pre_tenants = []
        low_payments = []

        for _ in moves.xrange(_LOOP_TIMES + 1):
            tenant_name = data_utils.rand_name(name='tenant-new')
            tenant = self.identity_client.create_tenant(tenant_name)
            self.addCleanup(self.identity_client.delete_tenant, tenant['id'])
            pre_tenants.append(tenant)
        pre_tenant_ids = map(lambda x: x['id'], pre_tenants)

        for pre_t_ids in pre_tenant_ids:
            payment = random.randrange(_PAYMENT_MIN, _ALARM_THRESHOLD_BALANCE)
            low_payments.append(payment)
            self.telemetry_client.create_bill_pay(pre_t_ids, payment)

        post_tenants = []
        high_payments = []

        for _ in moves.xrange(_LOOP_TIMES):
            tenant_name = data_utils.rand_name(name='tenant-new')
            tenant = self.identity_client.create_tenant(tenant_name)
            self.addCleanup(self.identity_client.delete_tenant, tenant['id'])
            post_tenants.append(tenant)
        post_tenant_ids = map(lambda x: x['id'], post_tenants)

        for post_t_ids in post_tenant_ids:
            payment = random.uniform(_ALARM_THRESHOLD_BALANCE,
                                     _PAYMENT_MAX_THRESHOLD)
            high_payments.append(payment)
            self.telemetry_client.create_bill_pay(post_t_ids, payment)

        param = {'threshold': _ALARM_THRESHOLD_BALANCE}
        body = self.telemetry_client.get_balance_alarm(param)

        fetch_balance = [float(b['balance']) for b in body]
        fetch_tenants = [t['tenant_id'] for t in body]

        missing_balance = [b for b in low_payments if b not in fetch_balance]
        missing_tenants = [t for t in pre_tenant_ids if t not in fetch_tenants]
        not_in_balance = [b for b in high_payments if b not in fetch_balance]
        not_in_tenants = [t for t in post_tenant_ids if t not in fetch_tenants]

        self.assertEqual(0, len(missing_tenants))
        self.assertEqual(3, len(not_in_balance))
        self.assertEqual(3, len(not_in_tenants))
        self.assertEqual(0, len(missing_balance), "balance alarm is invalid")
