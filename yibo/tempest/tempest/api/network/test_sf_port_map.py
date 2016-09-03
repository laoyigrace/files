# Copyright 2013 OpenStack Foundation
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

from tempest.api.network import sf_base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test

CONF = config.CONF


class SfPortMapTestJSON(sf_base.SfBaseNetworkTest):
    """
    Tests the following operations in the Quantum API using the REST client for
    Neutron:

        Create a Port Map
        Update a Port Map
        Delete a Port Map
        List all Port Maps
        Show Port Map details
        Associate a Floating IP with a port and then delete that port
        Associate a Floating IP with a port and then with a port on another
        router

    v2.0 of the Neutron API is assumed. It is also assumed that the following
    options are defined in the [network] section of etc/tempest.conf:

        public_network_id which is the id for the external network present
    """

    @classmethod
    def skip_checks(cls):
        super(SfPortMapTestJSON, cls).skip_checks()
        if not test.is_extension_enabled('router', 'network'):
            msg = "router extension not enabled."
            raise cls.skipException(msg)

    @classmethod
    def resource_setup(cls):
        super(SfPortMapTestJSON, cls).resource_setup()
        cls.ext_net_id = CONF.network.public_network_id
        cls.network = cls.create_network()
        cls.tenant_id = cls.network['tenant_id']

        cls.subnet = cls.create_subnet(cls.network)
        cls.router = cls.create_router(data_utils.rand_name('router-'),
                                       external_network_id=cls.ext_net_id)
        cls.router_id = cls.router['id']
        # cls.create_router_interface(cls.router['id'], cls.subnet['id'])

    @test.attr(type='smoke')
    @test.idempotent_id('620ccdcf-8847-11e5-a702-bc5ff49ce9ad')
    def test_create_list_show_update_delete_portmap(self):
        # Creates a portmap
        body = self.sf_network_client.create_portmap(
            router_id=self.router_id,
            tenant_id=self.tenant_id)
        created_portmap = body['port_map']
        self.addCleanup(self.sf_network_client.delete_portmap,
                        created_portmap['id'])
        self.assertIsNotNone(created_portmap['id'])
        self.assertEqual(created_portmap['router_id'], self.router_id)
        self.assertEqual(created_portmap['priority'], 2)
        self.assertEqual(created_portmap['external_ip'], '2.2.2.2')
        self.assertEqual(created_portmap['external_port'], 1000)
        self.assertEqual(created_portmap['interanet_ip'], '1.1.1.1')
        self.assertEqual(created_portmap['protocol'], 'udp')
        self.assertEqual(created_portmap['status'], 'enable')
        self.assertEqual(created_portmap['tenant_id'], self.tenant_id)
        self.assertEqual(created_portmap['rule_name'], 'test-rule_name')
        self.assertEqual(created_portmap['rule_desc'], 'test-rule_desc')
        self.assertEqual(created_portmap['interanet_port'], 2000)
        # Verifies the details of a portmap
        portmap = self.sf_network_client.show_portmap(created_portmap['id'])
        shown_portmap = portmap['port_map']
        self.assertEqual(shown_portmap['id'], created_portmap['id'])
        self.assertEqual(shown_portmap['router_id'],
                         self.router_id)
        self.assertEqual(shown_portmap['tenant_id'],
                         created_portmap['tenant_id'])
        self.assertEqual(shown_portmap['priority'], '2')
        self.assertEqual(shown_portmap['external_ip'],
                         created_portmap['external_ip'])
        self.assertEqual(shown_portmap['external_port'], '1000')
        self.assertEqual(shown_portmap['interanet_ip'],
                         created_portmap['interanet_ip'])
        self.assertEqual(shown_portmap['protocol'],
                         created_portmap['protocol'])
        self.assertEqual(shown_portmap['status'],
                         created_portmap['status'])
        self.assertEqual(shown_portmap['rule_name'],
                         created_portmap['rule_name'])
        self.assertEqual(shown_portmap['rule_desc'],
                         created_portmap['rule_desc'])
        self.assertEqual(shown_portmap['interanet_port'], '2000')

        # Verify the portmap exists in the list of all portmaps
        portmaps = self.sf_network_client.list_portmaps()
        portmap_id_list = list()
        for f in portmaps['port_maps']:
            portmap_id_list.append(f['id'])
        self.assertIn(created_portmap['id'], portmap_id_list)
        # Associate portmap to the other port
        portmap = self.sf_network_client.update_portmap(
            created_portmap['id'])
        updated_portmap = portmap['port_map']
        self.assertEqual(updated_portmap['router_id'], self.router_id)
        self.assertEqual(updated_portmap['priority'], 100)
        self.assertEqual(updated_portmap['external_ip'], '1.1.1.1')
        self.assertEqual(updated_portmap['external_port'], 100)
        self.assertEqual(updated_portmap['interanet_ip'], '10.10.10.10')
        self.assertEqual(updated_portmap['protocol'], 'tcp')
        self.assertEqual(updated_portmap['status'], 'enable')
        self.assertEqual(updated_portmap['tenant_id'], self.tenant_id)
        self.assertEqual(updated_portmap['rule_name'], 'test-rule_name')
        self.assertEqual(updated_portmap['rule_desc'], 'test-rule_desc')
        self.assertEqual(updated_portmap['interanet_port'], 200)

    @test.idempotent_id('c0c9e2e1-8847-11e5-b02e-bc5ff49ce9ad')
    def test_create_multi_portmap(self):
        body1 = self.sf_network_client.create_portmap(
            router_id=self.router_id,
            tenant_id=self.tenant_id,
            external_ip='100.100.100.100')
        body2 = self.sf_network_client.create_portmap(
            router_id=self.router_id,
            tenant_id=self.tenant_id,
            external_ip='11.11.11.11')
        created_portmap1 = body1['port_map']
        created_portmap2 = body2['port_map']
        self.addCleanup(self.sf_network_client.delete_portmap,
                        created_portmap1['id'])
        self.addCleanup(self.sf_network_client.delete_portmap,
                        created_portmap2['id'])
        portmaps = self.sf_network_client.list_portmaps()
        self.assertEqual(len(portmaps['port_maps']), 2)
        portmap1 = portmaps['port_maps'][0]
        portmap2 = portmaps['port_maps'][1]
        portmaps_list = list()
        portmaps_list.append(portmap1['external_ip'])
        portmaps_list.append(portmap2['external_ip'])
        self.assertIn('100.100.100.100', portmaps_list)
        self.assertIn('11.11.11.11', portmaps_list)

    @test.idempotent_id('ce8ada0f-8847-11e5-83a2-bc5ff49ce9ad')
    def test_delete_multi_portmap(self):
        body1 = self.sf_network_client.create_portmap(
            router_id=self.router_id,
            tenant_id=self.tenant_id,
            external_ip='101.100.100.100')
        body2 = self.sf_network_client.create_portmap(
            router_id=self.router_id,
            tenant_id=self.tenant_id,
            external_ip='11.11.11.11')
        created_portmap1 = body1['port_map']
        created_portmap2 = body2['port_map']
        portmaps = self.sf_network_client.list_portmaps()
        self.assertEqual(len(portmaps['port_maps']), 2)
        self.sf_network_client.delete_portmap(created_portmap1['id'])
        self.sf_network_client.delete_portmap(created_portmap2['id'])
        portmaps = self.sf_network_client.list_portmaps()
        self.assertEqual(len(portmaps['port_maps']), 0)
