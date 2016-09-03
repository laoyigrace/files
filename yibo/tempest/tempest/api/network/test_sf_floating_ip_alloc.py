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

from tempest_lib import exceptions as lib_exc
from tempest.api.network import base
from tempest.api.network import sf_base
from tempest import config
from tempest import test

CONF = config.CONF

class SfMutiAllocJson(base.BaseAdminNetworkTest,
                      sf_base.SfBaseNetworkTest):

    @test.idempotent_id('db5bd580-8853-11e5-975b-bc5ff49ce9ad')
    def test_create_floating_ip_alloc_same_ext_net_diff_network(self):
        # Create a network
        ext_net_id = CONF.network.public_network_id
        self.network = self.create_network()
        self.subnet = self.create_subnet(self.network)
        ext_net = self.admin_client.show_network(network_id=ext_net_id)
        subnet1 = ext_net['network']['subnets'][0]
        exsubnet = self.admin_client.create_subnet(network_id=ext_net['network']['id'],
                                                  cidr='192.168.66.0/24',
                                                  ip_version=4,
                                                  name='mysubnet',
                                                  allocation_pools=[{'start': '192.168.66.10',
                                                                     'end': '192.168.66.250'}],
                                                  gateway_ip='192.168.66.1')
        subnet2 = exsubnet['subnet']['id']
        # Creates two floating IP allocs
        body = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=ext_net_id,
            tenant_id=self.network['tenant_id'])
        created_floating_ip1 = body['sf_fip_alloc']
        body = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=ext_net_id,
            tenant_id=self.network['tenant_id'])
        created_floating_ip2 = body['sf_fip_alloc']
        self.assertTrue(exsubnet['subnet']['enable_dhcp'])
        self.addCleanup(self.sf_network_client.delete_floatingip_alloc,
                        created_floating_ip1['id'][0])
        self.addCleanup(self.sf_network_client.delete_floatingip_alloc,
                        created_floating_ip2['id'][0])
        self.assertEqual(created_floating_ip1['tenant_id'],
                         created_floating_ip2['tenant_id'])
        self.assertIsNotNone(created_floating_ip1['id'])
        self.assertIsNotNone(created_floating_ip2['id'])

class FloatingIPAllocTestJSON(sf_base.SfBaseNetworkTest):
    """
    Tests the following operations in the Quantum API using the REST client for
    Neutron:

        Create a Floating IP Alloc
        Update a Floating IP Alloc
        Delete a Floating IP Alloc
        List all Floating IPs Alloc
        Show Floating IP Alloc details

    v2.0 of the Neutron API is assumed. It is also assumed that the following
    options are defined in the [network] section of etc/tempest.conf:

        public_network_id which is the id for the external network present
    """

    @classmethod
    def skip_checks(cls):
        super(FloatingIPAllocTestJSON, cls).skip_checks()
        if not test.is_extension_enabled('router', 'network'):
            msg = "router extension not enabled."
            raise cls.skipException(msg)

    @classmethod
    def resource_setup(cls):
        super(FloatingIPAllocTestJSON, cls).resource_setup()
        cls.ext_net_id = CONF.network.public_network_id
        cls.ext_net = cls.sf_network_client.show_network(network_id=cls.ext_net_id)
        cls.ext_subnet_id = cls.ext_net['network']['subnets'][0]

        # Create network, subnet, router and add interface
        cls.network = cls.create_network()
        cls.subnet = cls.create_subnet(cls.network)

    @test.attr(type='smoke')
    @test.idempotent_id('ee17fa00-8853-11e5-ace2-bc5ff49ce9ad')
    def test_create_list_show_update_delete_floating_ip_alloc(self):
        # Creates a floating IP alloc
        body = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=self.ext_net_id,
            tenant_id=self.network['tenant_id'])
        created_floating_ip = body['sf_fip_alloc']
        self.addCleanup(self.sf_network_client.delete_floatingip_alloc,
                        created_floating_ip['id'][0])
        self.assertIsNotNone(created_floating_ip['id'])
        self.assertIsNotNone(created_floating_ip['tenant_id'])
        self.assertIsNotNone(created_floating_ip['external_ip'])
        self.assertEqual(created_floating_ip['qos_downlink'], '1000')
        self.assertEqual(created_floating_ip['qos_uplink'], '1000')

        # Verifies the details of a floating_ip alloc
        floating_ip = self.sf_network_client.\
            show_floatingip_alloc(created_floating_ip['id'][0])
        shown_floating_ip = floating_ip['sf_fip_alloc']
        self.assertEqual(shown_floating_ip['id'], created_floating_ip['id'][0])
        self.assertEqual(shown_floating_ip['external_network_id'],
                         self.ext_net_id)
        self.assertEqual(shown_floating_ip['tenant_id'],
                         created_floating_ip['tenant_id'])
        self.assertEqual(shown_floating_ip['external_ip'],
                         created_floating_ip['external_ip'])

        # Verify the floating ip exists in the list of all floating_ips alloc
        floating_ips = self.sf_network_client.list_floatingips_alloc()
        floatingip_id_list = list()
        for f in floating_ips['sf_fip_allocs']:
            floatingip_id_list.append(f['id'])
        self.assertIn(created_floating_ip['id'][0], floatingip_id_list)

        floating_ip = self.sf_network_client.update_floatingip_alloc(
            created_floating_ip['id'][0])
        updated_floating_ip = floating_ip['sf_fip_alloc']
        self.assertEqual(updated_floating_ip['external_ip'],
                         created_floating_ip['external_ip'])
        self.assertEqual(updated_floating_ip['id'],
                         created_floating_ip['id'][0])
        self.assertEqual(updated_floating_ip['qos_downlink'], '4096')
        self.assertEqual(updated_floating_ip['qos_uplink'], '2048')


    @test.idempotent_id('d848f740-89b3-11e5-8393-bc5ff49ce9c9')
    def test_create_many_floating_ip_allocs_and_delete(self):
        body = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=self.ext_net_id,
            tenant_id=self.network['tenant_id'])
        floating_ip_alloc1 = body['sf_fip_alloc']
        body = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=self.ext_net_id,
            tenant_id=self.network['tenant_id'])
        floating_ip_alloc2 = body['sf_fip_alloc']
        body = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=self.ext_net_id,
            tenant_id=self.network['tenant_id'])
        floating_ip_alloc3 = body['sf_fip_alloc']
        self.assertEqual(floating_ip_alloc1['tenant_id'],
                         floating_ip_alloc2['tenant_id'])
        self.assertEqual(floating_ip_alloc1['tenant_id'],
                         floating_ip_alloc3['tenant_id'])
        self.assertIsNotNone(floating_ip_alloc1['id'])
        self.assertIsNotNone(floating_ip_alloc2['id'])
        self.assertIsNotNone(floating_ip_alloc3['id'])

        self.sf_network_client.delete_floatingip_alloc(
            floating_id=floating_ip_alloc1['id'][0])
        self.sf_network_client.delete_floatingip_alloc(
            floating_id=floating_ip_alloc2['id'][0])
        self.sf_network_client.delete_floatingip_alloc(
            floating_id=floating_ip_alloc3['id'][0])

        # Verify the floating ip alloc already deleted
        self.assertRaises(lib_exc.ServerFault,
                          self.sf_network_client.show_floatingip_alloc,
                          floating_id=floating_ip_alloc1['id'][0])
        self.assertRaises(lib_exc.ServerFault,
                          self.sf_network_client.show_floatingip_alloc,
                          floating_id=floating_ip_alloc2['id'][0])
        self.assertRaises(lib_exc.ServerFault, self.sf_network_client.show_floatingip_alloc,
                          floating_id=floating_ip_alloc3['id'][0])

    @test.idempotent_id('deee0e91-89b4-11e5-9229-bc5ff49ce9c9')
    def test_create_many_floating_ip_allocs_and_list(self):
        body = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=self.ext_net_id,
            tenant_id=self.network['tenant_id'])
        floating_ip_alloc1 = body['sf_fip_alloc']
        body = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=self.ext_net_id,
            tenant_id=self.network['tenant_id'])
        floating_ip_alloc2 = body['sf_fip_alloc']
        body = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=self.ext_net_id,
            tenant_id=self.network['tenant_id'])
        floating_ip_alloc3 = body['sf_fip_alloc']
        self.addCleanup(self.sf_network_client.delete_floatingip_alloc,
                        floating_ip_alloc1['id'][0])
        self.addCleanup(self.sf_network_client.delete_floatingip_alloc,
                        floating_ip_alloc2['id'][0])
        self.addCleanup(self.sf_network_client.delete_floatingip_alloc,
                        floating_ip_alloc3['id'][0])
        self.assertEqual(floating_ip_alloc1['tenant_id'],
                         floating_ip_alloc2['tenant_id'])
        self.assertEqual(floating_ip_alloc1['tenant_id'],
                         floating_ip_alloc3['tenant_id'])
        self.assertIsNotNone(floating_ip_alloc1['id'])
        self.assertIsNotNone(floating_ip_alloc2['id'])
        self.assertIsNotNone(floating_ip_alloc3['id'])

        # Verify the floating ip alloc list
        floating_ips = self.sf_network_client.list_floatingips_alloc()
        floatingip_id_list = list()
        for f in floating_ips['sf_fip_allocs']:
            floatingip_id_list.append(f['id'])
        self.assertIn(floating_ip_alloc1['id'][0], floatingip_id_list)
        self.assertIn(floating_ip_alloc2['id'][0], floatingip_id_list)
        self.assertIn(floating_ip_alloc3['id'][0], floatingip_id_list)
