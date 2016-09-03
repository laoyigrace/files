import datetime
import random
from six import moves

from tempest_lib.common.utils import data_utils

from tempest.api.billcenter import base
from tempest import test

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
        tenant_name = data_utils.rand_name(name='t-charge')
        tenant = cls.identity_client.create_tenant(tenant_name)
        cls.tenant_ids.append(tenant['id'])
        cls.get_center_conn()

    @classmethod
    def resource_cleanup(cls):
        super(BillcenterChargeTestJson, cls).resource_cleanup()
        cls.cleanup_resources(cls.identity_client.delete_tenant,
                              cls.tenant_ids)
        cls.center_conn.delete_consume()
        cls.center_conn.delete_flow()
        cls.conn.delete_balance(cls.tenant_ids[0])

    @test.idempotent_id('8c9ad94f-7093-11e5-92bc-00e06665338b')
    def test_charge_bill(self):
        # create payment for tenant and get the cost
        tenant_id = self.tenant_ids[0]
        region = data_utils.rand_name(name='region')
        last_time = datetime.datetime.now()
        flow_date = last_time.strftime("%Y%m%d%H%M")
        cost = random.uniform(_PAYMENT_MIN, _PAYMENT_MAX)
        flows = [{
            "datetime": flow_date,
            "resource_name": "tempest_test",
            "type": "vm",
            "run_time": 10,
            "status": "active",
            "cost": cost,
            "version": 1,
            "resource_id": "tempest_test",
            "tenant_id": tenant_id,
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
                "tenant_id": tenant_id,
                "detail": "{\"cpu_number\":{\"1\":{\"1\":9}}}"
            }]

        body = self.billcenter_client.charge_bill(region, last_time, flows)
        self.assertEqual("True", body['status'])

        # query the flow table
        count = self.conn.get_flow()
        self.assertEqual(2, count)
