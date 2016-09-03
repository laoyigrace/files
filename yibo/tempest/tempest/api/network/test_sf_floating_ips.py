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

from tempest_lib.common.utils import data_utils
from tempest.api.network import sf_base
from tempest import config
from tempest import test

CONF = config.CONF


class FloatingIPTestJSON(sf_base.SfBaseNetworkTest):

    """
    Tests the following operations in the Quantum API using the REST client for
    Neutron:

        Create a Floating IP
        Delete a Floating IP
        List all Floating IPs
        Show Floating IP details

    v2.0 of the Neutron API is assumed. It is also assumed that the following
    options are defined in the [network] section of etc/tempest.conf:

        public_network_id which is the id for the external network present
    """

    @classmethod
    def resource_setup(cls):
        super(FloatingIPTestJSON, cls).resource_setup()
        if not test.is_extension_enabled('router', 'network'):
            msg = "router extension not enabled."
            raise cls.skipException(msg)
        cls.ext_net_id = CONF.network.public_network_id
        cls.ext_subnet = cls.sf_network_client.show_network(network_id=cls.ext_net_id)
        cls.ext_subnet_id = cls.ext_subnet['network']['subnets'][0]
        cls.ext_tenant_id = cls.ext_subnet['network']['tenant_id']

        # Create network, subnet, router and add interface
        cls.network = cls.create_network()
        cls.subnet = cls.create_subnet(cls.network)
        cls.router = cls.create_router(data_utils.rand_name('router-'),
                                       external_network_id=cls.ext_net_id)

    @test.attr(type='smoke')
    @test.idempotent_id('09b62d80-8855-11e5-87d3-bc5ff49ce9ad')
    def test_create_list_show_delete_floating_ip(self):
        # Creates a floating IP
        floating_ip_alloc = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=self.ext_net_id)
        body = self.sf_network_client.create_floatingip(
            router_id=self.router['id'],
            sffip_id=floating_ip_alloc['sf_fip_alloc']
            ['id'][0],
            tenant_id=self.network['tenant_id'])
        created_floating_ip = body['one_to_one_nat']
        self.addCleanup(self.sf_network_client.delete_floatingip_alloc,
                        floating_ip_alloc['sf_fip_alloc']['id'][0])
        self.addCleanup(self.sf_network_client.delete_floatingip,
                        created_floating_ip['id'][0])
        self.assertIsNotNone(created_floating_ip['id'])
        self.assertIsNotNone(created_floating_ip['sffip_id'])
        self.assertEqual(created_floating_ip['router_id'], self.router['id'])
        self.assertEqual(created_floating_ip['tenant_id'],
                         self.network['tenant_id'])

        # Verifies the details of a floating_ip
        floating_ip = self.sf_network_client.\
            show_floatingip(created_floating_ip['id'][0])
        shown_floating_ip = floating_ip['one_to_one_nat']
        self.assertEqual(shown_floating_ip['id'], created_floating_ip['id'][0])
        self.assertEqual(shown_floating_ip['tenant_id'],
                         created_floating_ip['tenant_id'])
        self.assertEqual(shown_floating_ip['sffip_id'],
                         created_floating_ip['sffip_id'])

        # Verify the floating ip exists in the list of all floating_ips
        floating_ips = self.sf_network_client.list_floatingips()
        floatingip_id_list = list()
        for f in floating_ips['one_to_one_nats']:
            floatingip_id_list.append(f['id'])
        self.assertIn(created_floating_ip['id'][0], floatingip_id_list)

    @test.idempotent_id('6da9f240-8855-11e5-99bb-bc5ff49ce9ad')
    def test_create_floating_ip_same_network_router(self):
        # create_dup_floating_ip
        intranet_ip1 = '10.10.122.122'
        intranet_ip2 = '10.10.133.133'
        floating_ip_alloc1 = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=self.ext_net_id,
            tenant_id=self.network['tenant_id'])
        floating_ip_alloc2 = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=self.ext_net_id,
            tenant_id=self.network['tenant_id'])
        body = self.sf_network_client.create_floatingip(
            self.router['id'],
            floating_ip_alloc1['sf_fip_alloc']['id'][0],
            self.network['tenant_id'],
            intranet_ip=intranet_ip1)
        created_floating_ip1 = body['one_to_one_nat']
        body = self.sf_network_client.create_floatingip(
            self.router['id'],
            floating_ip_alloc2['sf_fip_alloc']['id'][0],
            self.network['tenant_id'],
            intranet_ip=intranet_ip2)
        created_floating_ip2 = body['one_to_one_nat']
        self.addCleanup(self.sf_network_client.delete_floatingip_alloc,
                        floating_ip_alloc1['sf_fip_alloc']['id'][0])
        self.addCleanup(self.sf_network_client.delete_floatingip_alloc,
                        floating_ip_alloc2['sf_fip_alloc']['id'][0])
        self.addCleanup(self.sf_network_client.delete_floatingip,
                        created_floating_ip1['id'][0])
        self.addCleanup(self.sf_network_client.delete_floatingip,
                        created_floating_ip2['id'][0])
        self.assertEqual(created_floating_ip1['tenant_id'],
                         created_floating_ip2['tenant_id'])
        self.assertEqual(created_floating_ip1['router_id'],
                         created_floating_ip1['router_id'])
        self.assertIsNotNone(created_floating_ip1['id'])
        self.assertIsNotNone(created_floating_ip2['id'])

        # Verify the floating ip exists in the list of all floating_ips by list
        floating_ips = self.sf_network_client.list_floatingips()
        floatingip_id_list = list()
        for f in floating_ips['one_to_one_nats']:
            floatingip_id_list.append(f['id'])
        self.assertIn(created_floating_ip1['id'][0], floatingip_id_list)
        self.assertIn(created_floating_ip2['id'][0], floatingip_id_list)

        # Verify all floating_ips by show
        floating_ips1 = self.sf_network_client.show_floatingip(
            created_floating_ip1['id'][0])
        floating_ips2 = self.sf_network_client.show_floatingip(
            created_floating_ip2['id'][0])
        self.assertEqual(created_floating_ip1['id'][0],
                         floating_ips1['one_to_one_nat']['id'])
        self.assertEqual(created_floating_ip2['id'][0],
                         floating_ips2['one_to_one_nat']['id'])
        self.assertEqual(created_floating_ip1['router_id'],
                         floating_ips1['one_to_one_nat']['router_id'])
        self.assertEqual(created_floating_ip2['router_id'],
                         floating_ips2['one_to_one_nat']['router_id'])

    @test.idempotent_id('96ee1051-8855-11e5-a5b3-bc5ff49ce9ad')
    def test_create_floating_ip_same_intranet_ip_diff_router(self):
        # create_dup_ipaddress floating_ip
        intranet_ip1 = '10.10.122.122'
        network2 = self.create_network()
        self.create_subnet(network2)
        router2 = self.create_router(data_utils.rand_name('router-'),
                                     external_network_id=self.ext_net_id)
        floating_ip_alloc1 = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=self.ext_net_id,
            tenant_id=self.network['tenant_id'])
        floating_ip_alloc2 = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=self.ext_net_id,
            tenant_id=network2['tenant_id'])
        body = self.sf_network_client.create_floatingip(
            self.router['id'],
            floating_ip_alloc1['sf_fip_alloc']['id'][0],
            self.network['tenant_id'],
            intranet_ip=intranet_ip1)
        created_floating_ip1 = body['one_to_one_nat']
        body = self.sf_network_client.create_floatingip(
            router2['id'],
            floating_ip_alloc2['sf_fip_alloc']['id'][0],
            self.network['tenant_id'],
            intranet_ip=intranet_ip1)
        created_floating_ip2 = body['one_to_one_nat']
        self.addCleanup(self.sf_network_client.delete_floatingip_alloc,
                        floating_ip_alloc1['sf_fip_alloc']['id'][0])
        self.addCleanup(self.sf_network_client.delete_floatingip_alloc,
                        floating_ip_alloc2['sf_fip_alloc']['id'][0])
        self.addCleanup(self.sf_network_client.delete_floatingip,
                        created_floating_ip1['id'][0])
        self.addCleanup(self.sf_network_client.delete_floatingip,
                        created_floating_ip2['id'][0])
        self.assertEqual(created_floating_ip1['intranet_ip'],
                         created_floating_ip2['intranet_ip'])
