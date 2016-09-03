# Copyright 2014 IBM Corp.
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

import testtools

from tempest.api.compute import sf_base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test

CONF = config.CONF


class SfNetworksTestJSON(sf_base.SfBaseV2ComputeTest):
    @classmethod
    def skip_checks(cls):
        super(SfNetworksTestJSON, cls).skip_checks()
        if not CONF.service_available.neutron:
            raise cls.skipException('neutron is not available.')

    @test.attr(type='smoke')
    @test.idempotent_id('30320275-7812-47d1-9886-6bb08ac666ab')
    def test_sf_attach_detach_net(self):
        # test case for 'nova access-networks'
        server = self.create_sf_server()
        self.stop_server(server['id'])

        attach_networks = []
        detach_networks = []

        # create subnet to access
        net, subnet = self._create_net()
        network_id = {'net_id': net['network']['id']}
        attach_networks.append(network_id)

        self.sf_tenant_networks_client.access_networks(
            server['id'], attach_networks=attach_networks)

        # server  has the allocated address when accessing network successfully
        spec_server = self.servers_client.show_server(server['id'])
        self.assertIn(self.name_net, spec_server['addresses'])

        # find the port id correspond to the server ip to detach
        body = self.network_client.list_ports()
        ports = body['ports']
        for port in ports:
            if port['fixed_ips'][0]['ip_address'] == \
                    spec_server['addresses'][self.name_net][0]['addr']:
                detach_networks.append(port['id'])

        self.sf_tenant_networks_client.access_networks(
            server['id'], detach_networks=detach_networks)

        spec_server = self.servers_client.show_server(server['id'])
        self.assertNotIn(self.name_net, spec_server['addresses'])


class SfBulkNetworksTestJSON(sf_base.SfBaseV2ComputeTest):
    @classmethod
    def skip_checks(cls):
        super(SfBulkNetworksTestJSON, cls).skip_checks()
        if not CONF.service_available.neutron:
            raise cls.skipException('neutron is not available.')

    @testtools.skip('not requirement')
    @test.attr(type='smoke')
    @test.idempotent_id('2f68454f-3895-481a-ba52-fabbc53e3801')
    def test_sf_bulk_attach_detach_net(self):
        server = self.create_sf_server()
        self.stop_server(server['id'])

        attach_networks = []
        detach_networks = []
        net_names = []

        # create multiple subnet to access
        for i in range(2):
            net, subnet = self._create_net()
            network_id = {'net_id': net['network']['id']}
            attach_networks.append(network_id)
            net_names.append(self.name_net)

        self.sf_tenant_networks_client.access_networks(
            server['id'], attach_networks=attach_networks)

        # server  has the allocated address when accessing network successfully
        spec_server = self.servers_client.show_server(server['id'])
        found = [name for name in net_names
                 if name in spec_server['addresses']]
        self.assertEqual(len(found), len(net_names))

        # find the port id correspond to the server ip to detach
        body = self.network_client.list_ports()
        ports = body['ports']
        for port in ports:
            for net_name in net_names:
                if port['fixed_ips'][0]['ip_address'] == \
                        spec_server['addresses'][net_name][0]['addr']:
                    detach_networks.append(port['id'])

        self.sf_tenant_networks_client.access_networks(
            server['id'], detach_networks=detach_networks)

        spec_server = self.servers_client.show_server(server['id'])
        found = [name for name in net_names
                 if name in spec_server['addresses']]
        self.assertFalse(any(found))
