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

from tempest_lib.common.utils import data_utils
from tempest_lib import exceptions as lib_exc
from tempest.api.network import sf_base
from tempest import config
from tempest import test

CONF = config.CONF


class FloatingIPNegativeTestJSON(sf_base.SfBaseNetworkTest):

    """
    Test the following negative  operations for floating ips:

        Create floatingip in private network

    """

    @classmethod
    def resource_setup(cls):
        super(FloatingIPNegativeTestJSON, cls).resource_setup()
        if not test.is_extension_enabled('router', 'network'):
            msg = "router extension not enabled."
            raise cls.skipException(msg)
        cls.ext_net_id = CONF.network.public_network_id
        cls.ext_subnet_id = cls.sf_network_client.show_network(network_id=cls.ext_net_id)
        cls.ext_subnet_id = cls.ext_subnet_id['network']['subnets'][0]
        # Create a network with a subnet connected to a router.
        cls.network = cls.create_network()
        cls.subnet = cls.create_subnet(cls.network)
        cls.router = cls.create_router(data_utils.rand_name('router-'),
                                       external_network_id=cls.ext_net_id)
        cls.floating_ip_alloc = cls.sf_network_client.create_floatingip_alloc(
            floating_network_id=cls.ext_net_id,
            tenant_id=cls.network['tenant_id'])
        cls.floating_ip_alloc = cls.floating_ip_alloc['sf_fip_alloc']

    @test.attr(type=['negative'])
    @test.idempotent_id('bed9551e-8855-11e5-9926-bc5ff49ce9ad')
    def test_create_floatingip_with_router_donot_exsit(self):
        self.assertRaises(lib_exc.NotFound,
                          self.sf_network_client.create_floatingip,
                          router_id='50b9aeb4-9f0b-48ee-aa31-fa955a48ff59',
                          sffip_id=self.floating_ip_alloc['id'][0],
                          tenant_id=self.network['tenant_id'])

    @test.attr(type=['negative'])
    @test.idempotent_id('d6f0c84f-8855-11e5-b6b8-bc5ff49ce9ad')
    def test_create_floatingip_with_external_ip_donot_exsit(self):
        self.assertRaises(lib_exc.ServerFault,
                          self.sf_network_client.create_floatingip,
                          router_id=self.router['id'],
                          sffip_id='a6f0c84f-8855-11e5-b6b8-bc5ff49ce9ad',
                          tenant_id=self.network['tenant_id'])

    @test.attr(type=['negative'])
    @test.idempotent_id('f709cb00-8855-11e5-9200-bc5ff49ce9ad')
    def test_create_floatingip_tenant_donot_exsit(self):
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_floatingip,
                          router_id=self.router['id'],
                          sffip_id=self.floating_ip_alloc['id'][0],
                          tenant_id='50b9aeb4-9f0b-49ee-aa31-fa955a48ff53')

    @test.attr(type=['negative'])
    @test.idempotent_id('22579bc0-8856-11e5-834c-bc5ff49ce9ad')
    def test_create_floatingip_intranet_ip_error(self):
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_floatingip,
                          self.router['id'],
                          self.floating_ip_alloc['id'][0],
                          self.network['tenant_id'],
                          intranet_ip='256.0.0.1')

    @test.attr(type=['negative'])
    @test.idempotent_id('337e2c1e-8856-11e5-a1b0-bc5ff49ce9ad')
    def test_delete_floatingip_donot_exsit(self):
        self.sf_network_client.create_floatingip(
            router_id=self.router['id'],
            external_ip=self.floating_ip_alloc['external_ip'],
            tenant_id=self.network['tenant_id'],
            sffip_id=self.floating_ip_alloc['id'][0])['one_to_one_nat']
        self.assertRaises(lib_exc.ServerFault,
                          self.sf_network_client.delete_floatingip,
                          floating_id='50b9aeb4-9f0b-48ee-aa31-fa955a48ff14')
