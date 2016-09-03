# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest.api.compute import sf_base
from tempest.common.utils import data_utils
from tempest.common import waiters
from tempest import config
from tempest import test
import testtools

CONF = config.CONF


class SfCreateServersTestJSON(sf_base.SfBaseV2ComputeTest):
    # @classmethod
    # def setup_credentials(cls):
    #     cls.prepare_instance_network()
    #     super(SfCreateServersTestJSON, cls).setup_credentials()
    # if uncomment these codes, as execute create_test_server and
    # create_sf_server at the same time, it would make this testcase failed.
    # but at the cost of comments, the server of create_test_server() is error.

    @test.attr(type='smoke')
    @test.idempotent_id('748f32b7-1133-41ce-9875-5518931163e6')
    def test_sf_create_server_with_datadisk(self):
        self.create_sf_server()

    @test.attr(type='smoke')
    @test.idempotent_id('f5c22d1b-5dd4-4634-a27b-31d06843d09f')
    def test_sf_multi_create_server(self):
        # create two servers at the same time
        num = 2
        self.create_sf_server(max_count=num, min_count=num)


class SfUpdateServersTestJSON(sf_base.SfBaseV2ComputeTest):
    """testcase for update server cpu and ram"""

    # @classmethod
    # def setup_credentials(cls):
    #     cls.prepare_instance_network()
    #     super(SfUpdateServersTestJSON, cls).setup_credentials()

    @classmethod
    def resource_setup(cls):
        super(SfUpdateServersTestJSON, cls).resource_setup()
        cls.server = cls.create_sf_server()

    @test.attr(type='smoke')
    @test.idempotent_id('e6cffbdf-c4c1-4718-ae43-d1020dec2efc')
    def test_sf_update_server_cpu(self):
        cpu = 2
        self.stop_server(self.server['id'])
        server = self.servers_client.update_server(self.server['id'], cpu=cpu)
        waiters.wait_for_server_status(self.servers_client, self.server['id'],
                                       u'SHUTOFF')

        flavor = self.flavors_client.show_flavor(server['flavor']['id'])
        self.assertEqual(flavor['vcpus'], cpu)

    @test.attr(type='smoke')
    @test.idempotent_id('ae3044d4-256d-4882-9282-af54de4192e5')
    def test_sf_update_server_ram(self):
        ram = 1024
        self.stop_server(self.server['id'])
        server = self.servers_client.update_server(self.server['id'], ram=ram)
        waiters.wait_for_server_status(self.servers_client, self.server['id'],
                                       u'SHUTOFF')

        flavor = self.flavors_client.show_flavor(server['flavor']['id'])
        self.assertEqual(flavor['ram'], ram)

    def _update_server_description(self, server_id, status):
        # The server name should be changed to the the provided value
        new_desc = data_utils.rand_name('desc')
        # Update the server with a new name
        self.servers_client.update_server(server_id,
                                          desc=new_desc)
        waiters.wait_for_server_status(self.servers_client, server_id, status)

        # Verify the name of the server has changed
        server = self.servers_client.show_server(server_id)
        self.assertEqual(new_desc, server['desc'])
        return server

    @test.attr(type='smoke')
    @test.idempotent_id('a748dcb1-c0cc-4526-8913-c74ac38a8995')
    def test_update_server_description(self):
        # The server name should be changed to the the provided value
        server = self.create_sf_server()

        self._update_server_description(server['id'], 'ACTIVE')

    @test.attr(type='smoke')
    @test.idempotent_id('1d64b981-c307-46e4-abe4-18c4942cf9fe')
    def test_update_server_description_in_stop_state(self):
        # The server name should be changed to the the provided value
        server = self.create_sf_server()
        self.servers_client.stop(server['id'])
        waiters.wait_for_server_status(self.servers_client, server['id'], 'SHUTOFF')
        updated_server = self._update_server_description(server['id'], 'SHUTOFF')
        self.assertNotIn('progress', updated_server)
