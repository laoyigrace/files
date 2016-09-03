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
from tempest_lib import exceptions as lib_exc
from tempest.api.network import sf_base
from tempest import config
from tempest import test

CONF = config.CONF


class RouterUpdateNagativeTestJSON(sf_base.SfBaseNetworkTest):

    """
    Tests the following operations in the Quantum API using the REST client for
    Neutron:

        router_update

    v2.0 of the Neutron API is assumed. It is also assumed that the following
    options are defined in the [network] section of etc/tempest.conf:

        public_network_id which is the id for the external network present
    """

    @classmethod
    def resource_setup(cls):
        super(RouterUpdateNagativeTestJSON, cls).resource_setup()
        if not test.is_extension_enabled('router', 'network'):
            msg = "router extension not enabled."
            raise cls.skipException(msg)
        cls.ext_net_id = CONF.network.public_network_id

        # Create network, subnet, router and add interface
        cls.network = cls.create_network()
        cls.subnet = cls.create_subnet(cls.network)
        cls.router = cls.create_router(data_utils.rand_name('router-'),
                                       external_network_id=cls.ext_net_id)
        cls.sf_network_client.add_router_interface(router_id=cls.router['id'],\
                     subnet_id=cls.subnet['id'])

    @test.attr(type=['negative'])
    @test.idempotent_id('d9e04b26-076a-42e9-bd82-b0bf527843f4')
    def test_router_update_route_ip_not_connected(self):
        action = [{'destination':'192.168.66.0/24', 'nexthop':'192.200.42.1'}]
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.router_update,
                          router_id=self.router['id'], 
                          action=action)


    @test.attr(type=['negative'])
    @test.idempotent_id('4533f5d8-fa53-44bb-860f-3e3ca97e0247')
    def test_router_update_route_dest_nexthop_is_empty(self):
        action = [{'destination':'192.168.66.0/24', 'nexthop':''}]
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.router_update,
                          router_id=self.router['id'], 
                          action=action)

    @test.attr(type=['negative'])
    @test.idempotent_id('28f2344c-d7df-4a70-a924-5c012bd07046')
    def test_router_update_route_dest_is_empty(self):
        action = [{'destination':'', 'nexthop':'10.100.0.5'}]
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.router_update,
                          router_id=self.router['id'], 
                          action=action)

    @test.attr(type=['negative'])
    @test.idempotent_id('600624ec-9d3b-49e1-9c3a-f16776bf6711')
    def test_router_update_route_is_empty(self):
        action = [{'destination':'', 'nexthop':''}]
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.router_update,
                          router_id=self.router['id'], 
                          action=action)

