from tempest.api.network import sf_base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test
from tempest_lib import exceptions as lib_exc

CONF = config.CONF


class SfPortMapNegativeTestJSON(sf_base.SfBaseNetworkTest):

    @test.attr(type='negative')
    @test.idempotent_id('9cb8c3a1-884a-11e5-884d-bc5ff49ce9ad')
    def test_create_portmap_no_exist_routerid(self):
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_portmap,
                          router_id=49846548946)

    @test.attr(type=['negative'])
    @test.idempotent_id('e6cd4d80-884a-11e5-aff9-bc5ff49ce9ad')
    def test_create_portmap_invalid(self):
        self.ext_net_id = CONF.network.public_network_id
        self.router = self.create_router(data_utils.rand_name('router-'),
                                         external_network_id=self.ext_net_id)
        self.router_id = self.router['id']

        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_portmap,
                          router_id=self.router_id,
                          external_ip='1.1.1.300')

        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_portmap,
                          router_id=self.router_id,
                          interanet_ip='1.1.1.300')

        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_portmap,
                          router_id=self.router_id,
                          priority=555555555)

        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_portmap,
                          router_id=self.router_id,
                          external_port=0)

        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_portmap,
                          router_id=self.router_id,
                          interanet_port=0)

        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_portmap,
                          router_id=self.router_id,
                          protocol='icmp')

        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_portmap,
                          router_id=self.router_id,
                          status='aaa')

    @test.attr(type=['negative'])
    @test.idempotent_id('44ba566e-884d-11e5-9481-bc5ff49ce9ad')
    def test_update_no_exist_portmap(self):
        self.assertRaises(lib_exc.ServerFault,
                          self.sf_network_client.update_portmap,
                          portmap_id=325423543325)

    @test.attr(type=['negative'])
    @test.idempotent_id('b1899a80-884e-11e5-a416-bc5ff49ce9ad')
    def test_show_no_exist_portmap(self):
        self.assertRaises(lib_exc.ServerFault,
                          self.sf_network_client.update_portmap,
                          portmap_id=325423543325)

    @test.attr(type=['negative'])
    @test.idempotent_id('e28e6e80-884e-11e5-8c5c-bc5ff49ce9ad')
    def test_list_no_exist_portmap(self):
        res = self.sf_network_client.list_portmaps()
        self.assertEqual(len(res['port_maps']), 0)

    @test.attr(type=['negative'])
    @test.idempotent_id('16a53d70-884f-11e5-907f-bc5ff49ce9ad')
    def test_delete_no_exist_portmap(self):
        self.assertRaises(lib_exc.ServerFault,
                          self.sf_network_client.delete_portmap,
                          portmap_id=325423543325)
