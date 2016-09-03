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

from tempest.api.billcenter import base
from tempest import test

_ALARM_THRESHOLD_BALANCE = 100
_LOOP_TIMES = 3
_PAYMENT_MIN = 1
_PAYMENT_MAX = 10
_PAYMENT_MAX_THRESHOLD = 200


class BillcenterBillPayTestJson(base.BaseBillcenterTest):
    credentials = ['primary', 'admin']

    @classmethod
    def setup_clients(cls):
        super(BillcenterBillPayTestJson, cls).setup_clients()
        cls.identity_client = cls.os_adm.identity_client

    @classmethod
    def resource_setup(cls):
        super(BillcenterBillPayTestJson, cls).resource_setup()
        cls.get_region_conn()
        cls.get_center_conn()

    @test.idempotent_id('8c9ad94f-7093-11e5-92bc-00e06665338b')
    def test_create_bill_pay(self):
        # create  tenant for payment
        tenant_name = data_utils.rand_name(name='tenant-new')
        tenant = self.identity_client.create_tenant(tenant_name)
        author = data_utils.rand_name(name='sangfor')
        remark = data_utils.rand_name(name='charge')

        # delete tenant, pay,balance after teardown
        self.addCleanup(self.identity_client.delete_tenant, tenant['id'])
        self.addCleanup(self.region_conn.region_balance_delete, tenant['id'])
        self.addCleanup(self.center_conn.delete_balance, tenant['id'])
        self.addCleanup(self.center_conn.delete_pay, tenant['id'])

        base_account_pay = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
        free_account_pay = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
        payment = base_account_pay + free_account_pay

        body = self.billcenter_client.create_bill_pay(
            tenant['id'], author, base_account_pay=base_account_pay,
            free_account_pay=free_account_pay, remark=remark)

        self.assertEqual(tenant['id'], body['tenant_id'])
        self.assertEqual(author, body['author'])
        self.assertEqual(remark, body['remarks'])
        self.assertAlmostEqual(base_account_pay,
                               float(body['base_account_pay']), 4)
        self.assertAlmostEqual(free_account_pay,
                               float(body['free_account_pay']), 4)
        self.assertEqual(201, body.response.status)

        # verify if balance equal to payment
        balance = self.billcenter_client.get_bill_balance(tenant['id'])
        self.assertAlmostEqual(payment, float(balance['balance']), 4)
        self.assertAlmostEqual(base_account_pay,
                               float(balance['base_account_balance']), 4)
        self.assertAlmostEqual(free_account_pay,
                               float(balance['free_account_balance']), 4)

        # verify if region balance is synchronized
        region_balance = self.region_conn.region_balance_get(tenant['id'])
        self.assertEqual(float(balance['balance']), float(region_balance.balance))

    def test_create_base_pay(self):
        # create base payment for tenant
        tenant_name = data_utils.rand_name(name='tenant-new')
        tenant = self.identity_client.create_tenant(tenant_name)
        author = data_utils.rand_name(name='sangfor')

        self.addCleanup(self.identity_client.delete_tenant, tenant['id'])
        base_account_pay = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
        payment = base_account_pay

        body = self.billcenter_client.create_bill_pay(
            tenant['id'], author, base_account_pay=base_account_pay)

        self.addCleanup(self.region_conn.region_balance_delete, tenant['id'])
        self.addCleanup(self.center_conn.delete_balance, tenant['id'])
        self.addCleanup(self.center_conn.delete_pay, tenant['id'])

        self.assertEqual(tenant['id'], body['tenant_id'])
        self.assertEqual(author, body['author'])
        self.assertAlmostEqual(base_account_pay,
                               float(body['base_account_pay']), 4)
        self.assertEqual(201, body.response.status)

        # verify if balance equal to payment
        balance = self.billcenter_client.get_bill_balance(tenant['id'])
        self.assertAlmostEqual(payment, float(balance['balance']), 4)
        self.assertAlmostEqual(base_account_pay,
                               float(balance['base_account_balance']), 4)
        self.assertEqual(0, float(balance['free_account_balance']))

        # verify if region balance is synchronized
        region_balance = self.region_conn.region_balance_get(tenant['id'])
        self.assertEqual(float(balance['base_account_balance']),
                         float(region_balance.base_account_balance))

    def test_create_free_pay(self):
        # create free payment for tenant
        tenant_name = data_utils.rand_name(name='tenant-new')
        tenant = self.identity_client.create_tenant(tenant_name)
        author = data_utils.rand_name(name='sangfor')

        self.addCleanup(self.identity_client.delete_tenant, tenant['id'])
        free_account_pay = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
        payment = free_account_pay

        body = self.billcenter_client.create_bill_pay(
            tenant['id'], author, free_account_pay=free_account_pay)

        self.addCleanup(self.region_conn.region_balance_delete, tenant['id'])
        self.addCleanup(self.center_conn.delete_balance, tenant['id'])
        self.addCleanup(self.center_conn.delete_pay, tenant['id'])

        self.assertEqual(tenant['id'], body['tenant_id'])
        self.assertEqual(author, body['author'])
        self.assertAlmostEqual(free_account_pay,
                               float(body['free_account_pay']), 4)
        self.assertEqual(201, body.response.status)

        # verify if balance equal to payment
        balance = self.billcenter_client.get_bill_balance(tenant['id'])
        self.assertAlmostEqual(payment, float(balance['balance']), 4)
        self.assertAlmostEqual(0, float(balance['base_account_balance']), 4)
        self.assertAlmostEqual(free_account_pay,
                               float(balance['free_account_balance']), 4)

        # verify if region balance is synchronized
        region_balance = self.region_conn.region_balance_get(tenant['id'])

        # change the string type and  Decimal type to float to compare
        self.assertEqual(float(balance['free_account_balance']),
                         float(region_balance.free_account_balance))

    def test_list_bill_pay(self):
        # list all the payments of tenants
        tenants = []
        author = data_utils.rand_name(name='sangfor')
        remark = data_utils.rand_name(name='charge')
        for _ in moves.xrange(_LOOP_TIMES):
            tenant_name = data_utils.rand_name(name='tenant-new')
            tenant = self.identity_client.create_tenant(tenant_name)
            self.addCleanup(self.identity_client.delete_tenant, tenant['id'])
            tenants.append(tenant)
        tenant_ids = map(lambda x: x['id'], tenants)

        for tenant in tenants:
            base_account_pay = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            free_account_pay = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            self.billcenter_client.create_bill_pay(
                tenant['id'], author, base_account_pay=base_account_pay,
                free_account_pay=free_account_pay, remark=remark)

            self.addCleanup(self.region_conn.region_balance_delete, tenant['id'])
            self.addCleanup(self.center_conn.delete_balance, tenant['id'])
            self.addCleanup(self.center_conn.delete_pay, tenant['id'])

        body = self.billcenter_client.list_bill_pay()
        found = [p for p in body if p['tenant_id'] in tenant_ids]
        self.assertEqual(len(found), len(tenants), 'bill pay not create')

    def test_pay_history(self):
        # payment history of a specific tenant
        payments = []
        pay_all = 0
        base_account_pays = []
        author = data_utils.rand_name(name='sangfor')
        remark = data_utils.rand_name(name='charge')
        tenant_name = data_utils.rand_name(name='tenant-history')
        tenant = self.identity_client.create_tenant(tenant_name)

        self.addCleanup(self.identity_client.delete_tenant, tenant['id'])
        self.addCleanup(self.region_conn.region_balance_delete, tenant['id'])
        self.addCleanup(self.center_conn.delete_balance, tenant['id'])
        self.addCleanup(self.center_conn.delete_pay, tenant['id'])

        for _ in moves.xrange(_LOOP_TIMES):
            base_account_pay = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            free_account_pay = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            payment = base_account_pay + free_account_pay

            payments.append(payment)
            pay_all += payment
            base_account_pays.append(base_account_pay)
            self.billcenter_client.create_bill_pay(
                tenant['id'], author, base_account_pay=base_account_pay,
                free_account_pay=free_account_pay, remark=remark)

        query = ('tenant_id', 'eq', tenant['id'])
        body = self.billcenter_client.list_bill_pay(query)

        self.assertEqual(tenant['id'], body[0]['tenant_id'])
        self.assertEqual(_LOOP_TIMES, len(body))
        for i in range(_LOOP_TIMES):
            self.assertAlmostEqual(base_account_pays[i],
                                   float(body[i]['base_account_pay']), 4)
            self.assertEqual(remark, body[i]['remarks'])
            self.assertEqual(author, body[i]['author'])

        # verify if balance equal to payment
        balance = self.billcenter_client.get_bill_balance(tenant['id'])
        self.assertAlmostEqual(pay_all, float(balance['balance']), 4)

    def test_bill_balance(self):
        # list the balance of all tenants
        tenants = []
        payments = []
        base_account_pays = []
        free_account_pays = []
        author = data_utils.rand_name(name='sangfor')
        remark = data_utils.rand_name(name='charge')

        for _ in moves.xrange(_LOOP_TIMES):
            tenant_name = data_utils.rand_name(name='tenant-new')
            tenant = self.identity_client.create_tenant(tenant_name)
            self.addCleanup(self.identity_client.delete_tenant, tenant['id'])
            tenants.append(tenant)
        tenant_ids = map(lambda x: x['id'], tenants)

        for tenant in tenants:
            base_account_pay = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            free_account_pay = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            payment = base_account_pay + free_account_pay
            payments.append(payment)
            base_account_pays.append(base_account_pay)
            free_account_pays.append(free_account_pay)
            self.billcenter_client.create_bill_pay(
                tenant['id'], author, base_account_pay=base_account_pay,
                free_account_pay=free_account_pay, remark=remark)
            self.addCleanup(self.region_conn.region_balance_delete, tenant['id'])
            self.addCleanup(self.center_conn.delete_balance, tenant['id'])
            self.addCleanup(self.center_conn.delete_pay, tenant['id'])

        for i in range(_LOOP_TIMES):
            body = self.billcenter_client.get_bill_balance(tenant_ids[i])
            self.assertEqual(tenant_ids[i], body['tenant_id'])
            self.assertAlmostEqual(payments[i],
                                   float(body['balance']), 5)
            self.assertAlmostEqual(base_account_pays[i],
                                   float(body['base_account_balance']), 5)
            self.assertAlmostEqual(free_account_pays[i],
                                   float(body['free_account_balance']), 5)
