from tempest.api.network import base
from tempest.common.utils import data_utils
from tempest import test


class SfNetworksTestJSON(base.BaseAdminNetworkTest):
    @test.idempotent_id('03c99880-83b9-11e5-8a45-00e0666534ba')
    def test_sf_create_network_with_default_physical(self):
        # Create a network
        name = data_utils.rand_name('network-')
        network = self.admin_client.create_network(name=name)['network']
        net_id = network['id']
        self.addCleanup(self.admin_client.delete_network, net_id)
        self.assertEqual('ACTIVE', network['status'])
        self.assertFalse(network['physical'])
        self.assertNotIn(network['provider:segmentation_id'], range(0, 4097))

    @test.idempotent_id('b028abe1-8425-11e5-a94f-00e0666534ba')
    def test_sf_create_update_network_with_physical_and_segmentation_id(self):
        # Create a network
        name = data_utils.rand_name('network-')
        kwargs = {'physical': True, 'provider:segmentation_id': '123',
                  'provider:network_type': 'vxlan', 'vlanid': '10'}
        network = self.admin_client.create_network(name=name, **kwargs)['network']
        self.addCleanup(self.admin_client.delete_network, network['id'])
        self.assertEqual('ACTIVE', network['status'])
        self.assertTrue(network['physical'])
        self.assertEqual(network['provider:segmentation_id'], 123)
        self.assertEqual(network['provider:network_type'], 'vxlan')
        self.assertEqual(network['vlanid'], '10')
