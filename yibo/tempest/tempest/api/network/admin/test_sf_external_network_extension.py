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

from tempest.api.network import base
from tempest.common.utils import data_utils
from tempest import test


class SfExternalNetworksTestJSON(base.BaseAdminNetworkTest):

    @classmethod
    def resource_setup(cls):
        super(SfExternalNetworksTestJSON, cls).resource_setup()
        cls.network = cls.create_network()

    def _create_network(self, external=True):
        # Public method to create an external network
        post_body = {'name': data_utils.rand_name('network-')}
        if external:
            post_body['router:external'] = external
        body = self.admin_client.create_network(**post_body)
        network = body['network']
        self.addCleanup(self.admin_client.delete_network, network['id'])
        return network

    @test.idempotent_id('93cd06c0-5c4e-11e5-b6fe-00e0666de3ce')
    def test_sf_create_dup_name_external_network(self):
        # Create a network as an admin user specifying the
        # external network extension attribute
        ext_network1 = self._create_network()
        # Verifies router:external parameter
        self.assertIsNotNone(ext_network1['id'])
        self.assertTrue(ext_network1['router:external'])
        # Create the same name external network, verify network create success
        ext_network2 = self._create_network()
        self.assertIsNotNone(ext_network2['id'])
        self.assertTrue(ext_network2['router:external'])
