import datetime
import random
from six import moves

from tempest_lib.common.utils import data_utils

from tempest.api.billcenter import base
from tempest import test

_LOOP_TIMES = 3
_PAYMENT_MIN = 1
_PAYMENT_MAX = 10


class BillcenterChargeTestJson(base.BaseBillcenterTest):
    credentials = ['primary', 'admin']

    @classmethod
    def setup_clients(cls):
        super(BillcenterChargeTestJson, cls).setup_clients()
        cls.identity_client = cls.os_adm.identity_client

    @classmethod
    def resource_setup(cls):
        super(BillcenterChargeTestJson, cls).resource_setup()
        region = data_utils.rand_name(name='region')
        last_time = datetime.datetime.now()
        tenant_name = data_utils.rand_name(name='t-charge')
        tenant = cls.identity_client.create_tenant(tenant_name)
        cls.tenant_ids.append(tenant['id'])
        cls.get_center_conn()
        cls.cost_all = 0

        for i in moves.xrange(_LOOP_TIMES):
            delta = datetime.timedelta(minutes=10 * (i + 1))
            flow_date = last_time + delta
            cls.flow_date = flow_date.strftime("%Y%m%d%H%M")
            cost = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
            cls.cost_all += cost
            flow = [{
                "datetime": cls.flow_date,
                "resource_name": "tempest_test",
                "type": "vm",
                "run_time": 10,
                "status": "active",
                "cost": cost,
                "version": 1,
                "resource_id": "tempest_test",
                "tenant_id": tenant['id'],
                "detail": "{\"cpu_number\":{\"1\":{\"1\":9}}}"
            },
                {
                    "datetime": flow_date,
                    "resource_name": "tempest_test",
                    "type": "bill",
                    "run_time": 10,
                    "status": "",
                    "cost": cost,
                    "version": 1,
                    "resource_id": "tempest_test",
                    "tenant_id": tenant['id'],
                    "detail": "{\"cpu_number\":{\"1\":{\"1\":9}}}"
                }]
            cls.billcenter_client.charge_bill(region, flow_date, flow)

    @classmethod
    def resource_cleanup(cls):
        super(BillcenterChargeTestJson, cls).resource_cleanup()
        cls.cleanup_resources(cls.identity_client.delete_tenant,
                              cls.tenant_ids)
        cls.center_conn.delete_consume()
        cls.center_conn.delete_flow()
        cls.center_conn.delete_balance(cls.tenant_ids[0])

    @test.idempotent_id('8c9ad94f-7093-11e5-92bc-00e06665338b')
    def test_cost_bill(self):
        # get the cost
        t_id = self.tenant_ids[0]
        query = ('tenant_id', 'eq', t_id)
        body = self.billcenter_client.get_cost(query)
        self.assertEqual(2, len(body))
        for cost in body:
            if cost['type'] == 'bill':
                self.assertEqual(t_id, cost['tenant_id'])
                self.assertAlmostEqual(self.cost_all, float(cost['cost']), 4)
            else:
                self.assertEqual("tempest_test", cost['resource_id'])
                self.assertEqual("active", cost['status'])
                self.assertAlmostEqual(self.cost_all, float(cost['cost']), 4)
                self.assertEqual(self.flow_date[:8], cost['date'].replace("-", ""))

        # get the balance
        balance = self.billcenter_client.get_bill_balance(t_id)
        self.assertAlmostEqual(self.cost_all, -float(balance['balance']), 4)

