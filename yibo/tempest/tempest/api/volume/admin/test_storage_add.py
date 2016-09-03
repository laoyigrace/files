import time

from tempest_lib.common.utils import data_utils

from tempest.api.volume import sf_base
from tempest import test


class StorageV2AddTestJson(sf_base.BaseShareStorageTest):
    @classmethod
    def setup_clients(cls):
        super(StorageV2AddTestJson, cls).setup_clients()
        cls.client = cls.storage_client

    @classmethod
    def resource_setup(cls):
        super(StorageV2AddTestJson, cls).resource_setup()

        # Create test iscsi servers
        cls.create_iscsi(ip=cls._iscsi_ip, port=cls._iscsi_port)

    @test.idempotent_id('1b0e4b84-621d-4b1a-905c-600d13bf34bd')
    def test_storage_add(self):
        hostname = self.find_hostname()
        disk_ids = self.get_storage_ids()
        for disk_id in disk_ids:
            disk_name = data_utils.rand_name(name='test-disk')
            body = self.client.add_iscsi_storage(disk_id, hostname,
                                                 name=disk_name)
            # avoid /dev/mapper/disk_id is busy
            time.sleep(4)

            # delete the mount disk after tearDown
            self.addCleanup(self.client.delete_iscsi_storage, disk_id)
            self.assertEqual(self._status, body)

