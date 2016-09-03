import testtools

from tempest.api.compute import base
from tempest.common import waiters
from tempest.common.utils import data_utils
from tempest import test


class BulkDeleteServersTestJSON(base.BaseV2ComputeTest):

    # delete multiple servers on active and stop status

    _name = 'multiple-create'

    def _generate_name(self):
        return data_utils.rand_name(self._name)

    def _create_multiple_servers(self, name=None, wait_until=None, **kwargs):
        kwargs['name'] = name if name else self._generate_name()
        if wait_until:
            kwargs['wait_until'] = wait_until
        body = self.create_test_server(**kwargs)

        return body

    @classmethod
    def setup_clients(cls):
        super(BulkDeleteServersTestJSON, cls).setup_clients()
        cls.client = cls.servers_client

    @test.attr(type='smoke')
    @test.idempotent_id('b0374d85-2b70-4b98-8aef-bb523bbd5a61')
    def test_delete_active_stop_servers(self):
        # Delete a server while it's VM state is Active
        body = self._create_multiple_servers(wait_until='ACTIVE',
                                             min_count=1,
                                             max_count=2)
        server_to_stop = self.servers[0]
        self.client.stop(server_to_stop['id'])
        waiters.wait_for_server_status(self.client,
                                       server_to_stop['id'], 'SHUTOFF')

        for server in self.servers:
            self.client.delete_server(server['id'])
            self.client.wait_for_server_termination(server['id'])

    @test.attr(type='smoke')
    @test.idempotent_id('bb6a8294-0829-4edf-87cc-5878a1d32c68')
    def test_get_server(self):
        s_name = data_utils.rand_name('testGet')
        server = self._create_multiple_servers(name=s_name,
                                               wait_until='ACTIVE')
        body = self.client.show_server(server['id'])
        self.assertEqual(s_name, body['name'])
        self.assertEqual('ACTIVE', body['status'])

