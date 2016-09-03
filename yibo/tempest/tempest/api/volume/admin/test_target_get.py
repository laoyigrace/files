import time

from tempest.api.volume import sf_base
from tempest import test


class TargetV2GetTestJson(sf_base.BaseShareStorageTest):
    @classmethod
    def setup_clients(cls):
        super(TargetV2GetTestJson, cls).setup_clients()
        cls.client = cls.storage_client

    @classmethod
    def resource_setup(cls):
        super(TargetV2GetTestJson, cls).resource_setup()

        # Create test iscsi servers
        cls.create_iscsi(ip=cls._iscsi_ip, port=cls._iscsi_port)
        cls.iscsi_ips.append(cls._iscsi_ip)

    @test.idempotent_id('f7e6b3be-7b6e-4028-8565-f9999d5e2ac0')
    def test_target_list(self):

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

        target_list = self.await_target_storage(targets)
        self.assertEqual(len(targets), len(target_list))

    @test.idempotent_id('677ea63d-3767-46a5-b084-14b9b93a507d')
    def test_target_show(self):
        target_list = self.client.list_iscsi_target()
        fetch_ids = []
        fetch_names = []
        for server in target_list:
            fetch_ids.append(server['id'])
            fetch_names.append(server['name'])

        # Get target information
        for target_id, target_name in zip(fetch_ids, fetch_names):
            fetched_iscsi = self.client.show_iscsi_target(target_id)
            self.assertEqual(target_name,
                             fetched_iscsi['name'],
                             'The fetched target name is different '
                             'from the found target')
            self.assertEqual(target_id,
                             fetched_iscsi['id'],
                             'The fetched target id is different '
                             'from the found target')
            break







