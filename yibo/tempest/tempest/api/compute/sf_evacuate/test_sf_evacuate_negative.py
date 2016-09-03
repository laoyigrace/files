# Copyright 2015 Sangfor Technologies Co., Ltd
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

from tempest_lib.common.utils import data_utils
from tempest_lib import exceptions as lib_exc

from tempest.api.compute import base
from tempest.common import waiters
from tempest import test


class SfEvacuateNegativeTestJSON(base.BaseV2ComputeAdminTest):

    @classmethod
    def setup_clients(cls):
        super(SfEvacuateNegativeTestJSON, cls).setup_clients()
        cls.client = cls.os_adm.servers_client

    def tearDown(self):
        self.clear_servers()
        super(SfEvacuateNegativeTestJSON, self).tearDown()

    @test.idempotent_id('dd9e0c00-5aae-11e5-84c2-408d5c0827d0')
    def test_sf_evacuate_with_non_exists_server(self):
        # Evacuate a server which doesn't exists at all, API should raise a
        # NotFound exception.
        self.assertRaises(lib_exc.NotFound,
                          self.client.sf_evacuate_server,
                          data_utils.rand_uuid())

    @test.idempotent_id('dd4552c0-5ab0-11e5-a28f-408d5c0827d0')
    def test_sf_evacuate_server_to_non_exists_host(self):
        server = self.create_test_server(wait_until='ACTIVE')

        # API sf-evacuate requires the server in STOP status.
        self.client.stop(server['id'])
        waiters.wait_for_server_status(self.servers_client,
                                       server['id'], 'SHUTOFF')

        host_name = data_utils.rand_name('rand_hostname')
        self.assertRaises(lib_exc.NotFound,
                          self.client.sf_evacuate_server_to_specific_host,
                          server['id'],
                          host_name)

    @test.idempotent_id('dddde940-5ab0-11e5-8ba4-408d5c0827d0')
    def test_sf_evacuate_server_to_same_host(self):
        server = self.create_test_server(wait_until='ACTIVE')
        server = self.client.show_server(server['id'])
        host_id = server['hostId']

        # API sf-evacuate requires the server in STOP status.
        self.client.stop(server['id'])
        waiters.wait_for_server_status(self.servers_client,
                                       server['id'], 'SHUTOFF')

        # API should raise an exception when trying to evacuate a
        # server to the same host of itself.
        self.assertRaises(
            lib_exc.NotFound,
            self.client.sf_evacuate_server_to_specific_host,
            server['id'], host_id)

    @test.idempotent_id('ddc71b00-5ab2-11e5-a993-408d5c0827d0')
    def test_sf_evacuate_an_active_server(self):
        server = self.create_test_server(wait_until='ACTIVE')

        # Can't evacuate an ACTIVE server.
        self.assertRaises(lib_exc.Conflict,
                          self.client.sf_evacuate_server,
                          server['id'])
