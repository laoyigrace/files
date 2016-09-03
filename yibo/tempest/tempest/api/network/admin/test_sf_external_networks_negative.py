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

from tempest.api.network import base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test

CONF = config.CONF


class SfExternalNetworksAdminNegativeTestJSON(base.BaseAdminNetworkTest):

    @test.attr(type=['negative'])
    @test.idempotent_id('f6da5130-5c50-11e5-9f1f-00e0666de3ce')
    def test_sf_show_non_existent_external_networks_attribute(self):
        # Show non exist external networks attribute
        non_exist_ext_net_id = data_utils.rand_uuid()
        # Show an external network as a normal user
        # Extension attribute get fail, because no network is found
        self.assertRaises(lib_exc.NotFound,
                          self.client.show_network,
                          non_exist_ext_net_id)

    @test.attr(type=['negative'])
    @test.idempotent_id('cec0ac8f-5c54-11e5-ba53-00e0666de3ce')
    def test_sf_list_external_network_check_deleted(self):
        # Create external network is not in networks list
        external = True
        post_body = {'name': data_utils.rand_name('network-')}
        if external:
            post_body['router:external'] = external
        body = self.admin_client.create_network(**post_body)
        network = body['network']
        self.admin_client.delete_network(network['id'])
        # Verify network list, does not contain deleted network
        self.assertNotIn(network['id'], self.client.list_networks)

    @test.attr(type=['negative'])
    @test.idempotent_id('ea1c2a61-5c58-11e5-a1a1-00e0666de3ce')
    def test_sf_update_non_existent_external_network(self):
        non_exist_id = data_utils.rand_name('sf-network')
        # update data body
        update_body = {'router:external': True}
        self.assertRaises(lib_exc.NotFound,
                          self.admin_client.update_network,
                          non_exist_id, **update_body)

    @test.attr(type=['negative'])
    @test.idempotent_id('8b10aa4f-8430-11e5-b8e6-00e0666534ba')
    def test_sf_create_network_with_invalid_segmentation_id(self):
        # Create a network
        name = 'network-8b10aa4f'
        kwargs = {'physical': True, 'provider:segmentation_id': '100000',
                  'provider:network_type': 'vxlan'}
        self.assertRaises(lib_exc.BadRequest, self.admin_client.create_network,
                          name=name, **kwargs)
        kwargs = {'physical': False, 'provider:segmentation_id': '-1',
                  'provider:network_type': 'vxlan'}
        self.assertRaises(lib_exc.BadRequest, self.admin_client.create_network,
                          name=name, **kwargs)

    @test.attr(type=['negative'])
    @test.idempotent_id('5f655ad1-8431-11e5-a4dc-00e0666534ba')
    def test_sf_update_network_with_segmentation_id(self):
        # Create a network
        name = 'network-5f655ad1'
        network = self.admin_client.create_network(name=name)['network']
        net_id = network['id']
        self.addCleanup(self.admin_client.delete_network, net_id)
        kwargs = {'physical': True, 'provider:segmentation_id': '4096',
                  'provider:network_type': 'vxlan'}
        self.assertRaises(lib_exc.BadRequest, self.admin_client.update_network,
                          net_id, **kwargs)
        kwargs = {'physical': False, 'provider:segmentation_id': '4196',
                  'provider:network_type': 'vxlan'}
        self.assertRaises(lib_exc.BadRequest, self.admin_client.update_network,
                          net_id, **kwargs)
