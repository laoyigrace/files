from tempest.api.volume import sf_base
from tempest import test


class IscsiV2AddTestJson(sf_base.BaseShareStorageTest):

    @classmethod
    def setup_clients(cls):
        super(IscsiV2AddTestJson, cls).setup_clients()
        cls.client = cls.storage_client

    @test.attr(type=["smoke", "cloud"])
    @test.idempotent_id('fa83bff8-2310-45dd-a221-594d37cf65ba')
    def test_iscsi_add(self):
        iscsi_ip = "200.200.114.1"
        iscsi_port = self._iscsi_port
        self.iscsi_ips.append(iscsi_ip)
        body = self.client.add_iscsi_server(iscsi_ip, iscsi_port)

        self.assertEqual(self._status, body)


# now test case for AddDupTest has come to a negative case, so add comment
# class IscsiV2AddDupTestJson(sf_base.BaseShareStorageTest):
#
#     @classmethod
#     def setup_clients(cls):
#         super(IscsiV2AddDupTestJson, cls).setup_clients()
#         cls.client = cls.storage_client
#
#     @test.attr(type="smoke")
#     @test.idempotent_id('226c5439-89dc-4d42-bf9b-4789f175df17')
#     def test_add_duplicate(self):
#         iscsi_ip = "200.200.114.1"
#         iscsi_port = self._iscsi_port
#         self.iscsi_ips.append(iscsi_ip)
#         # create iscsi_server once
#         body = self.client.add_iscsi_server(iscsi_ip, iscsi_port)
#         self.assertEqual(self._status, body)
#
#         # create iscsi_server twice
#         body = self.client.add_iscsi_server(iscsi_ip, iscsi_port)
#         self.assertEqual(self._error_status, body)
