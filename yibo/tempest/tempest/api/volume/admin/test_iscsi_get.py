import time

from tempest.api.volume import sf_base
from tempest import test


class IscsiV2GetTestJson(sf_base.BaseShareStorageTest):
    @classmethod
    def setup_clients(cls):
        super(IscsiV2GetTestJson, cls).setup_clients()
        cls.client = cls.storage_client

    @classmethod
    def resource_setup(cls):
        super(IscsiV2GetTestJson, cls).resource_setup()

        # Create 3 test iscsi servers
        for i in range(3):
            iscsi_ip = "200.200.114.%s" % i
            cls.create_iscsi(ip=iscsi_ip)
            cls.iscsi_ips.append(iscsi_ip)

    @test.idempotent_id('1223c393-51bd-47df-b182-a436490eeeb7')
    def test_iscsi_list(self):
        # Get a list of iscsi servers
        # Fetch all iscsi
        fetched_list = self.client.list_iscsi_server()
        fetch_ips = []
        for server in fetched_list:
            fetch_ips.append(server['iscsi_ip'])
        found = [p for p in fetch_ips if p in self.iscsi_ips]
        self.assertEqual(len(self.iscsi_ips), len(found))

    @test.idempotent_id('6d402ee8-d03a-40a4-aaa3-abd999ad7895')
    def test_iscsi_show(self):
        # first Get a list of iscsi servers and their ids
        # then, fetch the specified server
        fetched_list = self.client.list_iscsi_server()
        fetch_ids = []
        fetch_ips = []
        for server in fetched_list:
            fetch_ids.append(server['id'])
            fetch_ips.append(server['iscsi_ip'])

        # Get Volume information
        for server_id, server_ip in zip(fetch_ids, fetch_ips):
            fetched_iscsi = self.client.show_iscsi_server(server_id)
            self.assertEqual(server_ip,
                             fetched_iscsi['iscsi_ip'],
                             'The fetched iscsi ip is different '
                             'from the created iscsi')
            self.assertEqual(server_id,
                             fetched_iscsi['id'],
                             'The fetched iscsi id is different '
                             'from the created iscsi')
            break

    @test.idempotent_id('e65a6408-928e-46ab-bf54-b2f9c5b06563')
    def test_iscsi_delete(self):
        iscsi_ip = "200.200.114.10"
        fetch_ids = []
        self.create_iscsi(ip=iscsi_ip)

        # get the specified iscsi server id and delete it

        iscsi_id = self.get_iscsi_id(iscsi_ip)

        body = self.client.delete_iscsi_server(iscsi_id)
        self.assertEqual(202, body.response.status)

        # fetch again and verify that the deleted iscsi is not in fetch list
        # fetched_list = self.client.list_iscsi_server()
        # for server in fetched_list:
        #     fetch_ids.append(server['id'])
        # self.assertNotIn(iscsi_id, fetch_ids)







