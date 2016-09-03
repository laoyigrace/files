
import time

from oslo_log import log as logging
from tempest.api.sfpool import sf_base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test

CONF = config.CONF
LOG = logging.getLogger(__name__)

class SfpoolTest(sf_base.SfBaseSfpoolTest):
    """testcase for sfpool api """

    @test.attr(type='smoke')
    @test.idempotent_id('b2c8c6fa-b279-4cd9-8bfa-6d2ff3f52700')
    def test_pool_self(self):
        """ self operations: create,delete,detail """
        print("YJZ: BEGIN")

        poolname = data_utils.rand_name('pool')
        print("YJZ: create pool: ", poolname)
        result = self.sfpool_client.pool_create(poolname)
        print("YJZ: result: ", result)
        self.assertIn('status', result)
        self.assertEqual(result['status'], "success")

        print("YJZ: show this pool")
        result = self.sfpool_client.pool_detail(poolname)
        print("YJZ: result: ", result)
        self.assertIn('status', result)
        self.assertIn('detail', result)
        self.assertEqual(result['status'], "success")
        self.assertEqual(len(result['detail']), 1)

        print("YJZ: check pool detail")
        result = result['detail'][0]
        self.assertIn('pool', result)
        self.assertIn('hosts', result)
        self.assertIn('storages', result)
        self.assertEqual(result['pool'], poolname)
        self.assertEqual(len(result['hosts']), 0)
        self.assertEqual(len(result['storages']), 0)

        print("YJZ: delete pool")
        result = self.sfpool_client.pool_delete(poolname)
        print("YJZ: result: ", result)
        self.assertIn('status', result)
        self.assertEqual(result['status'], "success")

        print("YJZ: check pool list")
        result = self.sfpool_client.pool_detail()
        print("YJZ: result: ", result)
        self.assertIn('status', result)
        self.assertIn('detail', result)
        self.assertEqual(result['status'], "success")
        for d in result['detail']:
            self.assertIn('pool', d)
            self.assertNotEqual(d['pool'], poolname)

        print("YJZ: PASS")
        return

    @test.attr(type='smoke')
    @test.idempotent_id('7cb322f9-abc9-4d44-ae26-85390b8ed4bf')
    def test_pool_host_storage(self):
        """ operations: add/delete host/storage """
        print("YJZ: BEGIN")

        poolname = data_utils.rand_name('pool')
        print("YJZ: create pool: ", poolname)
        result = self.sfpool_client.pool_create(poolname)
        print("YJZ: result: ", result)
        self.assertIn('status', result)
        self.assertEqual(result['status'], "success")
        self.addCleanup(self.sfpool_client.pool_delete, poolname)

        storage = data_utils.rand_name('storage')
        print("YJZ: add storage: ", storage)
        result = self.sfpool_client.pool_add_storage(poolname, storage)
        print("YJZ: result: ", result)
        self.assertIn('status', result)
        self.assertEqual(result['status'], "success")

        host = data_utils.rand_name('host')
        print("YJZ: add host: ", host)
        result = self.sfpool_client.pool_add_host(poolname, host)
        print("YJZ: result: ", result)
        self.assertIn('status', result)
        self.assertEqual(result['status'], "success")

        print("YJZ: show this pool")
        result = self.sfpool_client.pool_detail(poolname)
        print("YJZ: result: ", result)
        self.assertIn('status', result)
        self.assertIn('detail', result)
        self.assertEqual(result['status'], "success")
        self.assertEqual(len(result['detail']), 1)

        print("YJZ: check pool detail, should be with storage and host")
        result = result['detail'][0]
        self.assertIn('pool', result)
        self.assertIn('hosts', result)
        self.assertIn('storages', result)
        self.assertEqual(result['pool'], poolname)
        self.assertEqual(len(result['hosts']), 1)
        self.assertEqual(len(result['storages']), 1)
        result1 = result['hosts'][0]
        self.assertIn('host', result1)
        self.assertEqual(result1['host'], host)
        result2 = result['storages'][0]
        self.assertIn('storage', result2)
        self.assertEqual(result2['storage'], storage)

        print("YJZ: del storage")
        result = self.sfpool_client.pool_del_storage(poolname, storage)
        print("YJZ: result: ", result)
        self.assertIn('status', result)
        self.assertEqual(result['status'], "success")

        print("YJZ: del host")
        result = self.sfpool_client.pool_del_host(poolname, host)
        print("YJZ: result: ", result)
        self.assertIn('status', result)
        self.assertEqual(result['status'], "success")

        print("YJZ: show this pool")
        result = self.sfpool_client.pool_detail(poolname)
        print("YJZ: result: ", result)
        self.assertIn('status', result)
        self.assertIn('detail', result)
        self.assertEqual(result['status'], "success")
        self.assertEqual(len(result['detail']), 1)

        print("YJZ: check pool detail, should be clean")
        result = result['detail'][0]
        self.assertIn('pool', result)
        self.assertIn('hosts', result)
        self.assertIn('storages', result)
        self.assertEqual(result['pool'], poolname)
        self.assertEqual(len(result['hosts']), 0)
        self.assertEqual(len(result['storages']), 0)

        print("YJZ: PASS")
        return
