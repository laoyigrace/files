import time

from tempest_lib.common.utils import data_utils

from tempest.api.volume import sf_base
from tempest import test


class StorageV2DeleteTestJson(sf_base.BaseShareStorageTest):
    @classmethod
    def setup_clients(cls):
        super(StorageV2DeleteTestJson, cls).setup_clients()
        cls.client = cls.storage_client

    @classmethod
    def resource_setup(cls):
        super(StorageV2DeleteTestJson, cls).resource_setup()

        # Create test iscsi servers
        cls.create_iscsi(ip=cls._iscsi_ip, port=cls._iscsi_port)
        cls.iscsi_ips.append(cls._iscsi_ip)

    @test.idempotent_id('7420a2b5-6d23-4e1f-bc25-8e6e8f1e8438')
    def test_storage_delete(self):
        fetch_ids = []

        # get all storage and select one to delete
        hostname = self.find_hostname()
        disk_ids = self.get_storage_ids()
        if not (len(disk_ids) == 0):
            disk_id = disk_ids[0]

            disk_name = data_utils.rand_name(name='test-disk')
            self.client.add_iscsi_storage(disk_id, hostname,
                                          name=disk_name)

            body = self.client.delete_iscsi_storage(disk_id)
            self.assertEqual(202, body.response.status)

