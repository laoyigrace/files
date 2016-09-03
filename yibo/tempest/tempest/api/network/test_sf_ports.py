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

import socket

import netaddr

from tempest.api.network import base
from tempest.api.network import base_security_groups as sec_base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test

CONF = config.CONF


class PortsTestJSON(sec_base.BaseSecGroupTest):
    """
    Test the following operations for ports:

        port create
        port delete
        port list
        port show
        port update
    """

    @classmethod
    def resource_setup(cls):
        super(PortsTestJSON, cls).resource_setup()
        cls.network = cls.create_network()
        cls.port = cls.create_port(cls.network)

    def _delete_port(self, port_id):
        self.client.delete_port(port_id)
        body = self.client.list_ports()
        ports_list = body['ports']
        self.assertFalse(port_id in [n['id'] for n in ports_list])

    @test.attr(type='smoke')
    @test.idempotent_id('af45f280-c49b-11e5-a4d7-00e0666de3ce')
    def test_sf_create_port(self):
        # Verify port creation
        port_name = "sf-port"
        body = self.client.create_port(network_id=self.network['id'],
                                       name=port_name)
        port = body['port']
        # Schedule port deletion
        self.addCleanup(self._delete_port, port['id'])
        self.assertEqual(port['name'], port_name)
        self.assertTrue(port['admin_state_up'])

    @test.attr(type='smoke')
    @test.idempotent_id('ab15e08f-c49f-11e5-ac31-00e0666de3ce')
    def test_sf_update_port(self):
        # Create and update port
        # Verify port creation
        body = self.client.create_port(network_id=self.network['id'])
        port = body['port']
        # Schedule port deletion
        self.addCleanup(self._delete_port, port['id'])
        self.assertTrue(port['admin_state_up'])
        # Update port
        port_new_name = "sf-new-port"
        body = self.client.update_port(port['id'],
                                       name=port_new_name,
                                       admin_state_up=False)
        updated_port = body['port']
        # Verify updated information
        self.assertEqual(updated_port['name'], port_new_name)
        self.assertFalse(updated_port['admin_state_up'])

    @test.attr(type='smoke')
    @test.idempotent_id('dc86f900-c4a1-11e5-84d8-00e0666de3ce')
    def test_sf_create_bulk_port(self):
        # Create two network
        network1 = self.network
        name = "sf-network"
        network2 = self.create_network(network_name=name)
        network_list = [network1['id'], network2['id']]
        # Create corresponding ports
        port_list = [{'network_id': net_id} for net_id in network_list]
        body = self.client.create_bulk_port(port_list)
        created_ports = body['ports']
        port1 = created_ports[0]
        port2 = created_ports[1]
        # Do environmental cleaning
        self.addCleanup(self._delete_port, port1['id'])
        self.addCleanup(self._delete_port, port2['id'])
        self.assertEqual(port1['network_id'], network1['id'])
        self.assertEqual(port2['network_id'], network2['id'])
        self.assertTrue(port1['admin_state_up'])
        self.assertTrue(port2['admin_state_up'])

    @test.attr(type='smoke')
    @test.idempotent_id('80c64c4f-c4a7-11e5-9364-00e0666de3ce')
    def test_sf_delete_port(self):
        # Created port
        port_name = "sf-port"
        body = self.client.create_port(network_id=self.network['id'],
                                       name=port_name)
        port = body['port']
        port_id = port['id']
        self.assertEqual(port['name'], port_name)
        self.assertTrue(port['admin_state_up'])
        # Delete created port
        self.client.delete_port(port_id)
        # Check port is not in the list
        body = self.client.list_ports()
        ports_list = body['ports']
        self.assertFalse(port_id in [n['id'] for n in ports_list])

    @classmethod
    def _get_ipaddress_from_tempest_conf(cls):
        """Return first subnet gateway for configured CIDR """
        cls._ip_version == 4
        cidr = netaddr.IPNetwork(CONF.network.tenant_network_cidr)

        return netaddr.IPAddress(cidr)

    @test.idempotent_id('a1f85d1e-c4c8-11e5-95b0-00e0666de3ce')
    def test_sf_create_port_in_allowed_ip_pools(self):
        network = self.create_network()
        net_id = network['id']
        address = self._get_ipaddress_from_tempest_conf()
        ip_pools = {'allocation_pools': [{'start': str(address + 4),
                                          'end': str(address + 4)}]}
        subnet = self.create_subnet(network, **ip_pools)
        # Delete environment
        self.addCleanup(self.client.delete_subnet, subnet['id'])
        # Create port
        body = self.client.create_port(network_id=net_id)
        self.addCleanup(self.client.delete_port, body['port']['id'])
        port = body['port']
        ip_address = port['fixed_ips'][0]['ip_address']
        start_ip_address = ip_pools['allocation_pools'][0]['start']
        end_ip_address = ip_pools['allocation_pools'][0]['end']
        # Check ip_address in the range
        ip_range = netaddr.IPRange(start_ip_address, end_ip_address)
        self.assertIn(ip_address, ip_range)

    @test.attr(type='smoke')
    @test.idempotent_id('aa2816a1-c4ca-11e5-bbd1-00e0666de3ce')
    def test_sf_show_port(self):
        # Verify the details of port
        body = self.client.show_port(self.port['id'])
        port = body['port']
        # Check key-value
        self.assertIn('id', port)
        for key in ['id', 'name']:
            self.assertEqual(port[key], self.port[key])

    @test.idempotent_id('34126d5e-c4d1-11e5-a9a9-00e0666de3ce')
    def test_sf_show_port_fields(self):
        # Verify specific fields of a port
        fields = ['id', 'mac_address']
        body = self.client.show_port(self.port['id'],
                                     fields=fields)
        # Verify field
        port = body['port']
        self.assertEqual(sorted(port.keys()), sorted(fields))
        for field_name in fields:
            self.assertEqual(port[field_name], self.port[field_name])

    @test.idempotent_id('a8cdeec0-c4d3-11e5-b187-00e0666de3ce')
    def test_sf_list_ports(self):
        # Verify the port exists in the list of all ports
        body = self.client.list_ports()
        ports = [port['id'] for port in body['ports']
                 if port['id'] == self.port['id']]
        self.assertNotEmpty(ports, "Created port not found in the list")

    @test.idempotent_id('29f8d680-c4d5-11e5-9ee7-00e0666de3ce')
    def test_sf_port_list_filter_by_ip(self):
        # Create network and subnet
        network = self.create_network()
        subnet = self.create_subnet(network)
        self.addCleanup(self.client.delete_network, network['id'])
        self.addCleanup(self.client.delete_subnet, subnet['id'])
        # Create two ports specifying a fixed_ips
        address = self._get_ipaddress_from_tempest_conf()
        _fixed_ip_1 = str(address + 3)
        _fixed_ip_2 = str(address + 4)
        fixed_ips_1 = [{'ip_address': _fixed_ip_1}]
        port_1 = self.client.create_port(network_id=network['id'],
                                         fixed_ips=fixed_ips_1)
        self.addCleanup(self.client.delete_port, port_1['port']['id'])
        fixed_ips_2 = [{'ip_address': _fixed_ip_2}]
        port_2 = self.client.create_port(network_id=network['id'],
                                         fixed_ips=fixed_ips_2)
        self.addCleanup(self.client.delete_port, port_2['port']['id'])
        # List ports filtered by fixed_ips
        fixed_ips = 'ip_address=' + _fixed_ip_1
        port_list = self.client.list_ports(fixed_ips=fixed_ips)
        ports = port_list['ports']
        self.assertEqual(len(ports), 1)
        self.assertEqual(ports[0]['id'], port_1['port']['id'])
        self.assertEqual(ports[0]['fixed_ips'][0]['ip_address'],
                         _fixed_ip_1)
        self.assertEqual(ports[0]['network_id'], network['id'])

    @test.idempotent_id('6aefeeb0-c4d7-11e5-a326-00e0666de3ce')
    def test_sf_create_list_port_with_router(self):
        # Create a router
        network = self.create_network()
        self.addCleanup(self.client.delete_network, network['id'])
        subnet = self.create_subnet(network)
        self.addCleanup(self.client.delete_subnet, subnet['id'])
        router = self.create_router(data_utils.rand_name('sf-router'))
        self.addCleanup(self.client.delete_router, router['id'])
        port = self.client.create_port(network_id=network['id'])
        # Add router interface to port created above
        self.client.add_router_interface_with_port_id(
            router['id'], port['port']['id'])
        self.addCleanup(self.client.remove_router_interface_with_port_id,
                        router['id'], port['port']['id'])
        # List ports filtered by router_id
        port_list = self.client.list_ports(device_id=router['id'])
        ports = port_list['ports']
        self.assertEqual(len(ports), 1)
        self.assertEqual(ports[0]['id'], port['port']['id'])
        self.assertEqual(ports[0]['device_id'], router['id'])

    @test.idempotent_id('304ad9e1-c4d8-11e5-a594-00e0666de3ce')
    def test_sf_list_ports_fields(self):
        # Verify specific fields of ports
        fields = ['id', 'mac_address']
        body = self.client.list_ports(fields=fields)
        ports = body['ports']
        self.assertNotEmpty(ports, "Port list is empty")
        # Checking the fields
        for port in ports:
            self.assertEqual(sorted(fields), sorted(port.keys()))

    @test.idempotent_id('314587f0-c564-11e5-8044-00e0666de3ce')
    def test_sf_create_port_designed_mac(self):
        # Create a port for a legal mac
        body = self.client.create_port(network_id=self.network['id'])
        src_port = body['port']
        design_mac_address = src_port['mac_address']
        self.client.delete_port(src_port['id'])
        # Create a new port with designed mac
        body = self.client.create_port(network_id=self.network['id'],
                                       mac_address=design_mac_address)
        # Delete environment
        self.addCleanup(self.client.delete_port, body['port']['id'])
        port = body['port']
        body = self.client.show_port(port['id'])
        show_port = body['port']
        self.assertEqual(design_mac_address,
                         show_port['mac_address'])

    @test.idempotent_id('b3ecaf6e-c565-11e5-ab3e-00e0666de3ce')
    def test_sf_show_port_designed_mac(self):
        # Create a port for a legal mac
        mac_address = "aa-b2-c3-d4-e5-f6"
        # Create a port with legal mac
        body = self.client.create_port(network_id=self.network['id'],
                                       mac_address=mac_address)
        self.addCleanup(self.client.delete_port, body['port']['id'])
        port = body['port']
        body = self.client.show_port(port['id'])
        show_port = body['port']
        self.assertEqual(mac_address,
                         show_port['mac_address'])


class PortsAdminExtendedAttrsTestJSON(base.BaseAdminNetworkTest):

    @classmethod
    def setup_clients(cls):
        super(PortsAdminExtendedAttrsTestJSON, cls).setup_clients()
        cls.identity_client = cls.os_adm.identity_client

    @classmethod
    def resource_setup(cls):
        super(PortsAdminExtendedAttrsTestJSON, cls).resource_setup()
        cls.network = cls.create_network()
        cls.host_id = socket.gethostname()

    @test.idempotent_id('2570ef0f-c572-11e5-97c1-00e0666de3ce')
    def test_sf_create_port_binding_ext_attr(self):
        post_body = {"network_id": self.network['id'],
                     "binding:host_id": self.host_id}
        body = self.admin_client.create_port(**post_body)
        port = body['port']
        self.addCleanup(self.admin_client.delete_port, port['id'])
        host_id = port['binding:host_id']
        self.assertIsNotNone(host_id)
        self.assertEqual(self.host_id, host_id)

    @test.idempotent_id('5aec08f0-c572-11e5-ba04-00e0666de3ce')
    def test_sf_update_port_binding_ext_attr(self):
        post_body = {"network_id": self.network['id']}
        body = self.admin_client.create_port(**post_body)
        port = body['port']
        self.addCleanup(self.admin_client.delete_port, port['id'])
        update_body = {"binding:host_id": self.host_id}
        body = self.admin_client.update_port(port['id'], **update_body)
        updated_port = body['port']
        host_id = updated_port['binding:host_id']
        self.assertIsNotNone(host_id)
        self.assertEqual(self.host_id, host_id)

    @test.idempotent_id('ed567ac0-c588-11e5-acd5-00e0666de3ce')
    def test_sf_show_port_binding_ext_attr(self):
        body = self.admin_client.create_port(network_id=self.network['id'])
        port = body['port']
        self.addCleanup(self.admin_client.delete_port, port['id'])
        body = self.admin_client.show_port(port['id'])
        show_port = body['port']
        self.assertEqual(port['binding:host_id'],
                         show_port['binding:host_id'])
        self.assertEqual(port['binding:vif_type'],
                         show_port['binding:vif_type'])
        self.assertEqual(port['binding:vif_details'],
                         show_port['binding:vif_details'])
