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


class RouterUpdateTestJSON(sf_base.SfBaseNetworkTest):

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
        super(RouterUpdateTestJSON, cls).resource_setup()
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

    @test.attr(type='smoke')
    @test.idempotent_id('a0bf10f0-49ba-479c-a0dd-aeaf90031c35')
    def test_router_update_route(self):
        # Create a route for a router
        action = [{'destination':'192.168.66.0/24', 'nexthop':'10.100.0.5'}]
        route_info = self.sf_network_client.router_update(
            router_id=self.router['id'], action=action)
        self.assertEqual(route_info['router']['routes'], action)

        # Show the route
        router_info = self.sf_network_client.router_show(\
            router_id=self.router['id'])
        self.assertEqual(router_info['router']['routes'], action)

        # Update the route
        action = [{'destination':'192.168.88.0/24', 'nexthop':'10.100.0.6'}]
        route_info = self.sf_network_client.router_update(\
            router_id=self.router['id'], action=action)
        self.assertEqual(route_info['router']['routes'], action)

        # Delete the route
        router_update_info = self.sf_network_client.router_update(
            router_id=self.router['id'], action=None)
        self.assertEqual(router_update_info['router']['routes'], [])
        #self.sf_network_client.remove_router_interface(router_id=self.router['id'],\
        #     subnet_id=self.subnet['id'])

    @test.attr(type='smoke')
    @test.idempotent_id('2322115f-fb32-4e80-a009-a3daf34ecf81')
    def test_router_update_muti_route(self):
        # Create a route for a router
        action = [{'destination':'192.168.44.0/24', 'nexthop':'10.100.0.5'},
                  {'destination':'192.168.55.0/24', 'nexthop':'10.100.0.5'},
                  {'destination':'192.168.66.0/24', 'nexthop':'10.100.0.5'},
                  {'destination':'192.168.77.0/24', 'nexthop':'10.100.0.5'},
                  {'destination':'192.168.88.0/24', 'nexthop':'10.100.0.5'},]
        route_info = self.sf_network_client.router_update(
            router_id=self.router['id'], action=action)
        self.assertEqual(route_info['router']['routes'], action)

        # Show the route
        router_info = self.sf_network_client.router_show(\
            router_id=self.router['id'])
        self.assertEqual(router_info['router']['routes'], action)

        # Update the route
        action = [{'destination':'192.168.88.0/24', 'nexthop':'10.100.0.6'}]
        route_info = self.sf_network_client.router_update(\
            router_id=self.router['id'], action=action)
        self.assertEqual(route_info['router']['routes'], action)

        # Delete the route
        router_update_info = self.sf_network_client.router_update(
            router_id=self.router['id'], action=None)
        self.assertEqual(router_update_info['router']['routes'], [])
        #self.sf_network_client.remove_router_interface(router_id=self.router['id'],\
        #     subnet_id=self.subnet['id'])
