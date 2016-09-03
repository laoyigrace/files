# -*- coding:utf-8 -*-
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

from tempest.api.compute import base
from tempest.common import waiters
from tempest import test


class SfEvacuateTestJSON(base.BaseV2ComputeAdminTest):
    _host_key = 'OS-EXT-SRV-ATTR:host'

    @classmethod
    def setup_clients(cls):
        super(SfEvacuateTestJSON, cls).setup_clients()
        cls.servers_client = cls.os_adm.servers_client
        cls.hosts_client = cls.os_adm.hosts_client

    def tearDown(self):
        self.clear_servers()
        super(SfEvacuateTestJSON, self).tearDown()

    def _get_compute_host_names(self):
        body = self.hosts_client.list_hosts()
        return [
            host_record['host_name']
            for host_record in body
            if host_record['service'] == 'compute'
        ]

    def _get_server_details(self, server_id):
        body = self.servers_client.show_server(server_id)
        return body

    def _get_host_for_server(self, server_id):
        return self._get_server_details(server_id)[self._host_key]

    def _get_host_other_than(self, host):
        for target_host in self._get_compute_host_names():
            if host != target_host:
                return target_host

    @test.idempotent_id('dd057580-5aae-11e5-83f5-408d5c0827d0')
    def test_sf_evacuate_server(self):
        """Tests sf_evacuate a server without specific target host.

        Requires two available hosts.

        """
        if len(self._get_compute_host_names()) < 2:
            raise self.skipTest(
                "Less than 2 compute nodes, skipping sf_evacuate test.")

        server = self.create_test_server(wait_until='ACTIVE')
        server = self.servers_client.show_server(server['id'])

        # Get the original host id of the created server above,
        # which using to compare with the host id after evacuated.
        host_id_before_evacuate = server['hostId']

        # API sf-evacuate requires the server in STOP status.
        self.servers_client.stop(server['id'])
        waiters.wait_for_server_status(self.servers_client,
                                       server['id'], 'SHUTOFF')

        # Do the evacuate action.
        self.servers_client.sf_evacuate_server(server['id'])
        waiters.wait_for_server_status(self.servers_client,
                                       server['id'], 'SHUTOFF')

        # Get the host id after evacuate.
        server = self.servers_client.show_server(server['id'])
        host_id_after_evacuate = server['hostId']

        # If these two host id are different, means the evacuate action
        # executed successfully.
        self.assertNotEqual(host_id_before_evacuate, host_id_after_evacuate)

    @test.idempotent_id('dd7be88f-5aaf-11e5-9736-408d5c0827d0')
    def test_sf_evacuate_server_to_specific_host(self):
        """Tests sf_evacuate a server with specific target host.

        Requires two available hosts.

        """
        if len(self._get_compute_host_names()) < 2:
            raise self.skipTest(
                "Less than 2 compute nodes, skipping sf_evacuate test.")

        server = self.create_test_server(wait_until='ACTIVE')
        server = self.servers_client.show_server(server['id'])

        # API sf-evacuate requires the server in STOP status.
        self.servers_client.stop(server['id'])
        waiters.wait_for_server_status(self.servers_client,
                                       server['id'], 'SHUTOFF')

        actual_host = self._get_host_for_server(server['id'])
        target_host = self._get_host_other_than(actual_host)

        # Do the evacuate action.
        self.servers_client.sf_evacuate_server_to_specific_host(
            server['id'], target_host)
        waiters.wait_for_server_status(self.servers_client,
                                       server['id'], 'SHUTOFF')

        # If actual host equals target host, means the evacuate action
        # executed successfully.
        actual_host = self._get_host_for_server(server['id'])

        self.assertEqual(target_host, actual_host)


