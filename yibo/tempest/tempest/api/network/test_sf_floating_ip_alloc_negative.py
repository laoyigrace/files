# Copyright 2014 Hewlett-Packard Development Company, L.P.
# Copyright 2014 OpenStack Foundation
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
from tempest.api.network import sf_base
from tempest import config
from tempest import test

CONF = config.CONF


class FloatingIPAllocNegativeTestJSON(sf_base.SfBaseNetworkTest):

    """
    Test the following negative  operations for floating ips:

        Create floatingip alloc in private network

    """

    @classmethod
    def resource_setup(cls):
        super(FloatingIPAllocNegativeTestJSON, cls).resource_setup()
        if not test.is_extension_enabled('router', 'network'):
            msg = "router extension not enabled."
            raise cls.skipException(msg)
        cls.ext_net_id = CONF.network.public_network_id
        cls.ext_subnet_id = cls.sf_network_client.show_network(network_id=cls.ext_net_id)
        cls.ext_subnet_id = cls.ext_subnet_id['network']['subnets'][0]
        # Create a network with a subnet connected to a router.
        cls.network = cls.create_network()
        cls.subnet = cls.create_subnet(cls.network)

    @test.attr(type=['negative'])
    @test.idempotent_id('4aeb6780-8854-11e5-a79a-bc5ff49ce9ad')
    def test_create_floatingip_alloc_in_private_network(self):
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_floatingip_alloc,
                          floating_network_id=self.network['id'],
                          tenant_id=self.network['tenant_id'])

    @test.attr(type=['negative'])
    @test.idempotent_id('67cf56de-8854-11e5-b9f3-bc5ff49ce9ad')
    def test_create_floatingip_alloc_with_qos_error(self):
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_floatingip_alloc,
                          floating_network_id=self.ext_net_id,
                          tenant_id=self.network['tenant_id'],
                          qos_uplink='-1')
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_floatingip_alloc,
                          floating_network_id=self.ext_net_id,
                          tenant_id=self.network['tenant_id'],
                          qos_downlink='192168100120')

    @test.attr(type=['negative'])
    @test.idempotent_id('a11ef85e-8854-11e5-9c3e-bc5ff49ce9ad')
    def test_create_floatingip_alloc_external_net_id_donot_exsit(self):
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_floatingip_alloc,
                          floating_network_id='',
                          tenant_id=self.network['tenant_id'])

    @test.attr(type=['negative'])
    @test.idempotent_id('c3c583c0-8854-11e5-bfb3-bc5ff49ce9ad')
    def test_delete_floatingip_alloc_donot_exsit(self):
        self.assertRaises(lib_exc.NotFound,
                          self.sf_network_client.delete_floatingip_alloc,
                          floating_id='')

    @test.attr(type=['negative'])
    @test.idempotent_id('50b9aeb4-9f0b-48ee-aa31-fa955a48ff21')
    def test_update_floatingip_alloc_donot_exsit(self):
        self.assertRaises(lib_exc.ServerFault,
                          self.sf_network_client.update_floatingip_alloc,
                          floating_id='fa955a48ff21')

    @test.attr(type=['negative'])
    @test.idempotent_id('df236f61-8854-11e5-8791-bc5ff49ce9ad')
    def test_update_floatingip_alloc_qos_error(self):
        body = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=self.ext_net_id,
            tenant_id=self.network['tenant_id'])
        created_floating_ip = body['sf_fip_alloc']
        self.addCleanup(self.sf_network_client.delete_floatingip_alloc,
                        created_floating_ip['id'][0])
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.update_floatingip_alloc,
                          created_floating_ip['id'][0],
                          qos_uplink='-1',
                          qos_downlink='10086')
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.update_floatingip_alloc,
                          created_floating_ip['id'][0],
                          qos_uplink='10086',
                          qos_downlink='0.0001')
