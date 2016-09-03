from tempest.api.network import sf_base
from tempest import config
from tempest import test

CONF = config.CONF


class SfInterfaceQosTestJSON(sf_base.SfBaseNetworkTest):

    @classmethod
    def skip_checks(cls):
        super(SfInterfaceQosTestJSON, cls).skip_checks()
        if not test.is_extension_enabled('router', 'network'):
            msg = "router extension not enabled."
            raise cls.skipException(msg)

    @classmethod
    def resource_setup(cls):
        super(SfInterfaceQosTestJSON, cls).resource_setup()
        cls.ext_net_id = CONF.network.public_network_id
        cls.network = cls.create_network()
        cls.tenant_id = cls.network['tenant_id']
        cls.subnet = cls.create_subnet(cls.network)
        cls.port = cls.create_port(cls.network)
        cls.update_port(cls.port, device_owner='compute:nova')

    @test.attr(type='smoke')
    @test.idempotent_id('84e1e9a1-884f-11e5-9f9e-bc5ff49ce9ad')
    def test_create_list_show_update_delete_qos(self):
        body = self.sf_network_client.create_qos(
            port_id=self.port['id'],
            tenant_id=self.tenant_id)
        created_qos = body['interface_qos']
        self.addCleanup(self.sf_network_client.delete_qos,
                        created_qos['id'])
        interface_qos = self.sf_network_client.show_qos(created_qos['id'])
        shown_qos = interface_qos['interface_qos']
        self.assertEqual(shown_qos['id'], created_qos['id'])
        self.assertEqual(shown_qos['port_id'], self.port['id'])
        self.assertEqual(shown_qos['qos_uplink'], 500)
        self.assertEqual(shown_qos['qos_downlink'], 1000)
        self.sf_network_client.update_qos(
            created_qos['id'])
        interface_qoss = self.sf_network_client.list_qoss()
        updated_qos = interface_qoss['interface_qoss'][0]
        self.assertEqual(updated_qos['id'], created_qos['id'])
        self.assertEqual(updated_qos['port_id'], self.port['id'])
        self.assertEqual(updated_qos['qos_uplink'], 100)
        self.assertEqual(updated_qos['qos_downlink'], 200)

    @test.idempotent_id('e6f76640-89b4-11e5-8865-bc5ff49ce9ad')
    def test_delete_multi_qos(self):
        self.port1 = self.create_port(self.network)
        self.update_port(self.port1, device_owner='compute:nova')
        body1 = self.sf_network_client.create_qos(
            port_id=self.port['id'],
            tenant_id=self.tenant_id)
        body2 = self.sf_network_client.create_qos(
            port_id=self.port1['id'],
            tenant_id=self.tenant_id)
        created_qos1 = body1['interface_qos']
        created_qos2 = body2['interface_qos']
        interface_qoss = self.sf_network_client.list_qoss()
        self.assertEqual(len(interface_qoss['interface_qoss']), 2)
        interface_qos1 = self.sf_network_client.show_qos(created_qos1['id'])
        shown_qos1 = interface_qos1['interface_qos']
        self.assertEqual(shown_qos1['id'], created_qos1['id'])
        self.assertEqual(shown_qos1['port_id'], self.port['id'])
        self.assertEqual(shown_qos1['qos_uplink'], 500)
        self.assertEqual(shown_qos1['qos_downlink'], 1000)
        interface_qos2 = self.sf_network_client.show_qos(created_qos2['id'])
        shown_qos2 = interface_qos2['interface_qos']
        self.assertEqual(shown_qos2['id'], created_qos2['id'])
        self.assertEqual(shown_qos2['port_id'], self.port1['id'])
        self.assertEqual(shown_qos2['qos_uplink'], 500)
        self.assertEqual(shown_qos2['qos_downlink'], 1000)
        self.sf_network_client.delete_qos(created_qos1['id'])
        self.sf_network_client.delete_qos(created_qos2['id'])
        interface_qoss = self.sf_network_client.list_qoss()
        self.assertEqual(len(interface_qoss['interface_qoss']), 0)
