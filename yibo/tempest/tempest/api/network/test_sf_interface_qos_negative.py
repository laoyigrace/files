from tempest.api.network import sf_base
from tempest import config
from tempest import test
from tempest_lib import exceptions as lib_exc

CONF = config.CONF


class SfQOSNegativeTestJSON(sf_base.SfBaseNetworkTest):

    @classmethod
    def resource_setup(cls):
        super(SfQOSNegativeTestJSON, cls).resource_setup()
        cls.ext_net_id = CONF.network.public_network_id
        cls.network = cls.create_network()
        cls.tenant_id = cls.network['tenant_id']
        cls.subnet = cls.create_subnet(cls.network)
        cls.port = cls.create_port(cls.network)
        cls.update_port(cls.port, device_owner='compute:nova')

    @test.attr(type=['negative'])
    @test.idempotent_id('d1cd92e1-8850-11e5-8be6-bc5ff49ce9ad')
    def test_create_qos_not_vm_port(self):
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_qos,
                          port_id=49846548946)

    @test.attr(type=['negative'])
    @test.idempotent_id('005ae1c0-8852-11e5-9fd4-bc5ff49ce9ad')
    def test_create_qos_invalid(self):
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_qos,
                          port_id=self.port['id'],
                          tenant_id=64121652)
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_qos,
                          port_id=self.port['id'],
                          tenant_id=self.tenant_id,
                          qos_uplink=-1)

        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_qos,
                          port_id=self.port['id'],
                          tenant_id=self.tenant_id,
                          qos_downlink=-1)
        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_qos,
                          port_id=self.port['id'],
                          tenant_id=self.tenant_id,
                          qos_uplink=4564444444444444444444)

        self.assertRaises(lib_exc.BadRequest,
                          self.sf_network_client.create_qos,
                          port_id=self.port['id'],
                          tenant_id=self.tenant_id,
                          qos_downlink=489414649154649841651496)

    @test.attr(type=['negative'])
    @test.idempotent_id('84527380-8852-11e5-a9b7-bc5ff49ce9ad')
    def test_update_no_exist_qos(self):
        self.assertRaises(lib_exc.ServerFault,
                          self.sf_network_client.update_qos,
                          qos_id=325423543325)

    @test.attr(type=['negative'])
    @test.idempotent_id('f74f8df0-8852-11e5-8411-bc5ff49ce9ad')
    def test_show_no_exist_qos(self):
        self.assertRaises(lib_exc.ServerFault,
                          self.sf_network_client.show_qos,
                          qos_id=325423543325)

    @test.attr(type=['negative'])
    @test.idempotent_id('2db66761-8853-11e5-84bf-bc5ff49ce9ad')
    def test_list_no_exist_qos(self):
        res = self.sf_network_client.list_portmaps()
        self.assertEqual(len(res['port_maps']), 0)

    @test.attr(type=['negative'])
    @test.idempotent_id('be1c2700-8852-11e5-8548-bc5ff49ce9ad')
    def test_delete_no_exist_qos(self):
        self.assertRaises(lib_exc.ServerFault,
                          self.sf_network_client.delete_qos,
                          qos_id=325423543325)
