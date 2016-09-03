import time

from oslo_utils import timeutils

from tempest.api.volume import sf_base
from tempest import config
from tempest import exceptions
from tempest import test

CONF = config.CONF


class StorageV2GetTestJson(sf_base.BaseShareStorageTest):
    @classmethod
    def setup_clients(cls):
        super(StorageV2GetTestJson, cls).setup_clients()
        cls.client = cls.storage_client

    @classmethod
    def resource_setup(cls):
        super(StorageV2GetTestJson, cls).resource_setup()

        # Create test iscsi servers
        cls.create_iscsi(ip=cls._iscsi_ip, port=cls._iscsi_port)
        cls.iscsi_ips.append(cls._iscsi_ip)

    @test.idempotent_id('d9334501-776b-4ee7-898c-186816a3d82f')
    def test_storage_list(self):
        # get all iscsi servers ip
        fetched_list = self.client.list_iscsi_server()
        fetch_ips = []
        targets = []
        for server in fetched_list:
            fetch_ips.append(server['iscsi_ip'])

        # execute discover command on each server to get all targets
        for iscsi_ip in fetch_ips:
            ret = self.iscsi_target_discover(iscsi_ip, self._iscsi_port)
            targets.extend(ret)

        storage_flag = True
        storage_list = self.await_target_storage(targets, storage_flag)
        self.assertEqual(len(targets), len(storage_list))

    @test.idempotent_id('527c8b65-fcf6-4889-8128-bcca7e2a7c16')
    def test_storage_show(self):
        storage_list = self.client.list_iscsi_storage()
        fetch_ids = []
        fetch_names = []
        for storage in storage_list:
            fetch_ids.append(storage['id'])
            fetch_names.append(storage['name'])

        # Get storage information
        for storage_id, storage_name in zip(fetch_ids, fetch_names):
            fetched_iscsi = self.client.show_iscsi_storage(storage_id)
            self.assertEqual(storage_name,
                             fetched_iscsi['name'],
                             'The fetched storage name is different '
                             'from the found storage')
            self.assertEqual(storage_id,
                             fetched_iscsi['id'],
                             'The fetched storage id is different '
                             'from the found storage')
            break
