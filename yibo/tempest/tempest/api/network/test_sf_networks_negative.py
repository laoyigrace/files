# Copyright 2013 Huawei Technologies Co.,LTD.
# Copyright 2012 OpenStack Foundation
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

import netaddr
from tempest_lib import exceptions as lib_exc
from tempest import exceptions
from tempest.common import compute
from tempest.api.network import base
from tempest import config
from tempest import test

CONF = config.CONF


class SfNetworksNegativeTestJSON(base.BaseNetworkTest):
    # Public method realize

    @classmethod
    def setup_clients(cls):
        super(SfNetworksNegativeTestJSON, cls).setup_clients()
        cls.servers_client = cls.os.servers_client
        cls.admin_client = cls.os_adm.network_client

    def _create_test_server(cls, tenant_network, validatable=False, **kwargs):
        """Wrapper utility that returns a test server.

        This wrapper utility calls the common create test server and
        returns a test server. The purpose of this wrapper is to minimize
        the impact on the code of the tests already using this
        function.
        """
        tenant_network = tenant_network
        body, servers = compute.create_test_server(
            cls.os,
            validatable,
            validation_resources=cls.validation_resources,
            tenant_network=tenant_network,
            **kwargs)

        return body

    def _try_delete_network(self, net_id):
        # delete network, if it exists
        try:
            self.client.delete_network(net_id)
        # if network is not found, this means it was deleted in the test
        except lib_exc.NotFound:
            pass

    def _delete_network(self, network):
        # Deleting network also deletes its subnets if exists
        self.client.delete_network(network['id'])
        if network in self.networks:
            self.networks.remove(network)
        for subnet in self.subnets:
            if subnet['network_id'] == network['id']:
                self.subnets.remove(subnet)

    def _delete_port(self, port_id):
        self.client.delete_port(port_id)
        body = self.client.list_ports()
        ports_list = body['ports']
        self.assertFalse(port_id in [n['id'] for n in ports_list])

    @test.attr(type=['negative'])
    @test.idempotent_id('086198f0-5850-11e5-be21-00e0666de3ce')
    def test_sf_create_port_on_deleted_network(self):
        network = self.create_network()
        net_id = network['id']
        self.client.delete_network(net_id)
        # create port fail, not found network
        self.assertRaises(lib_exc.NotFound,
                          self.client.create_port,
                          network_id=net_id)

    @test.attr(type=['negative'])
    @test.idempotent_id('0290198f-5834-11e5-bcb3-00e0666de3ce')
    def test_sf_show_deleted_network_port(self):
        network = self.create_network()
        body = self.client.create_port(network_id=network['id'])
        port = body['port']
        port_id = port['id']
        self.client.delete_port(port_id)
        # Verify port not found
        self.assertRaises(lib_exc.NotFound,
                          self.client.show_port,
                          port_id)
        # clean network source
        self._try_delete_network(network['id'])

    @test.attr(type=['negative'])
    @test.idempotent_id('f555ced1-5844-11e5-8bf0-00e0666de3ce')
    def test_sf_update_deleted_network(self):
        network = self.create_network()
        net_id = network['id']
        self.client.delete_network(net_id)
        # Verify updated_network not found
        self.assertRaises(lib_exc.NotFound,
                          self.client.update_network,
                          net_id)

    @test.attr(type=['negative'])
    @test.idempotent_id('0b572ab0-582e-11e5-8c74-00e0666de3ce')
    def test_sf_show_deleted_network(self):
        network = self.create_network()
        net_id = network['id']
        self.client.delete_network(net_id)
        # Verify network not found
        self.assertRaises(lib_exc.NotFound,
                          self.client.show_network,
                          net_id)

    @test.attr(type=['negative'])
    @test.idempotent_id('84147380-5857-11e5-a141-00e0666de3ce')
    def test_sf_show_deleted_subnet(self):
        network = self.create_network()
        subnet = self.create_subnet(network)
        subnet_id = subnet['id']
        self._delete_network(network)
        # Verify subnet not found
        self.assertRaises(lib_exc.NotFound,
                          self.client.show_subnet,
                          subnet_id)

    @test.attr(type=['negative'])
    @test.idempotent_id('98bcc180-5860-11e5-8a28-00e0666de3ce')
    def test_sf_update_deleted_subnet(self):
        network = self.create_network()
        subnet = self.create_subnet(network)
        subnet_id = subnet['id']
        self._delete_network(network)
        # Verify subnet not found
        self.assertRaises(lib_exc.NotFound,
                          self.client.update_subnet,
                          subnet_id)

    @test.attr(type=['negative'])
    @test.idempotent_id('657a8b1e-5925-11e5-b67a-00e0666de3ce')
    def test_sf_create_subnet_on_non_exist_network(self):
        network = self.create_network()
        net_id = network['id']
        self.client.delete_network(net_id)
        self.assertRaises(lib_exc.BadRequest,
                          self.client.create_subnet,
                          network_id=network['id'], gateway=None, ip_version=4)

    @test.attr(type=['negative'])
    @test.idempotent_id('1058e061-c7bb-11e5-9b89-00e0666534ba')
    def test_sf_delete_network_with_server_port(self):
        # create network
        name = "sf-network"
        network = self.create_network(network_name=name)
        self.addCleanup(self._delete_network, network)
        self.assertEqual('ACTIVE', network['status'])
        self.create_subnet(network)
        # server creation
        net = [{'uuid': network['id']}]
        server = self._create_test_server(network['tenant_id'],
                                          networks=net, wait_until='ACTIVE')
        # When the port is used to delete the network(port attribute non dhcp)
        self.assertRaises(lib_exc.Conflict,
                          self.client.delete_network,
                          network['id'])
        self.servers_client.delete_server(server['id'])
        self.servers_client.wait_for_server_termination(server['id'])

    @test.attr(type=['negative'])
    @test.idempotent_id('b2cc0861-5c16-11e5-9b2e-00e0666de3ce')
    def test_sf_list_networks_deleted_network(self):
        # Deleted network is not in networks list
        name = "sf-network"
        network = self.create_network(network_name=name)
        net_id = network['id']
        self.assertEqual('ACTIVE', network['status'])
        self.client.delete_network(net_id)
        # Verify network list
        self.assertNotIn(network['id'], self.client.list_subnets)

    @test.attr(type=['negative'])
    @test.idempotent_id('26717b80-5c3d-11e5-b132-00e0666de3ce')
    def test_sf_list_subnets_deleted_subnet(self):
        # Deleted subnet is not in subnets list
        name = "sf-network"
        network = self.create_network(network_name=name)
        net_id = network['id']
        subnet = self.create_subnet(network)
        subnet_id = subnet['id']
        self.assertEqual('ACTIVE', network['status'])
        self.client.delete_subnet(subnet_id)
        self.client.delete_network(net_id)
        # Verify subnet list
        self.assertNotIn(subnet['id'], self.client.list_subnets)

    @test.attr(type=['negative'])
    @test.idempotent_id('fdaea6de-5a85-11e5-84ab-00e0666de3ce')
    def test_sf_create_dup_name_network(self):
        name = "sf_network"
        network_one = self.create_network(network_name=name)
        self.addCleanup(self._delete_network, network_one)
        self.assertEqual('ACTIVE', network_one['status'])
        # can't create the same name network
        new_name = "sf_network"
        self.assertRaises(lib_exc.BadRequest,
                          self.create_network,
                          network_name=new_name)

    @test.attr(type=['negative'])
    @test.idempotent_id('63646770-82c9-11e5-91e6-00e0666534ba')
    def test_sf_create_dup_name_subnet(self):
        name = "sf_network"
        network = self.create_network(network_name=name)
        self.addCleanup(self._delete_network, network)
        self.assertEqual('ACTIVE', network['status'])
        # Create the  same subnet_name
        sub_name = "sf-subnet"
        mask_bits = CONF.network.tenant_network_mask_bits
        subnet_cidr = netaddr.IPNetwork('192.168.0.0/28')
        subnet_cidr2 = netaddr.IPNetwork('192.168.1.0/24')
        subnet = self.create_subnet(network, cidr=subnet_cidr,
                                    name=sub_name, mask_bits=mask_bits)
        self.assertEqual(netaddr.IPNetwork(subnet['cidr']).version, 4,
                         'The created subnet is not IPv4')
        self.assertEqual(netaddr.IPNetwork(subnet['cidr']), subnet_cidr,
                         'The created subnet cidr Mismatch')
        # can't create the same name subnet
        self.assertRaises(lib_exc.BadRequest,
                          self.create_subnet,
                          network, cidr=subnet_cidr2,
                          name=sub_name, mask_bits=mask_bits)

    @test.attr(type=['negative'])
    @test.idempotent_id('1c729a00-82cc-11e5-98cb-00e0666534ba')
    def test_sf_create_dup_cidr(self):
        name = "sf_network"
        network = self.create_network(network_name=name)
        self.addCleanup(self._delete_network, network)
        self.assertEqual('ACTIVE', network['status'])
        # Create the  same subnet_name
        sub_name = "sf-subnet"
        sub_name2 = "sf-subnet2"
        mask_bits = CONF.network.tenant_network_mask_bits
        subnet_cidr = netaddr.IPNetwork('192.168.0.0/28')
        subnet = self.create_subnet(network, cidr=subnet_cidr,
                                    name=sub_name, mask_bits=mask_bits)
        self.assertEqual(netaddr.IPNetwork(subnet['cidr']).version, 4,
                         'The created subnet is not IPv4')
        self.assertEqual(netaddr.IPNetwork(subnet['cidr']), subnet_cidr,
                         'The created subnet cidr Mismatch')
        # can't create the same cidr
        self.assertRaises(exceptions.BuildErrorException,
                          self.create_subnet,
                          network, cidr=subnet_cidr,
                          name=sub_name2, mask_bits=mask_bits)

    @test.attr(type=['negative'])
    @test.idempotent_id('c95819ee-c66c-11e5-acc6-00e0666534ba')
    def test_sf_narrow_subnet_allocation_pools(self):
        name = "sf_network"
        network = self.create_network(network_name=name)
        self.addCleanup(self._delete_network, network)
        self.assertEqual('ACTIVE', network['status'])
        # Create the  same subnet_name
        sub_name = "sf-subnet"
        mask_bits = CONF.network.tenant_network_mask_bits
        subnet_cidr = netaddr.IPNetwork('192.168.0.0/28')

        subnet = self.create_subnet(network, cidr=subnet_cidr,
                                    name=sub_name, mask_bits=mask_bits)
        subnet_id = subnet['id']
        self.assertEqual(netaddr.IPNetwork(subnet['cidr']).version, 4,
                         'The created subnet is not IPv4')
        self.assertEqual(netaddr.IPNetwork(subnet['cidr']), subnet_cidr,
                         'The created subnet cidr Mismatch')
        # can't create the same cidr
        new_allocation_pools = [{'start': '192.168.0.2', 'end': '192.168.0.4'}]
        self.assertRaises(lib_exc.BadRequest,
                          self.client.update_subnet,
                          subnet_id,
                          allocation_pools=new_allocation_pools)

    @test.attr(type=['negative'])
    @test.idempotent_id('04c9038f-c7c7-11e5-86ea-00e0666534ba')
    def test_sf_overlapping_subnet_allocation_pools(self):
        name = "sf_network"
        network = self.create_network(network_name=name)
        self.addCleanup(self._delete_network, network)
        self.assertEqual('ACTIVE', network['status'])
        # Create the  same subnet_name
        sub_name = "sf-subnet"
        subnet_cidr = netaddr.IPNetwork('192.168.0.0/28')
        allocation_pools = [{'start': '192.168.0.2', 'end': '192.168.0.4'},
                            {'start': '192.168.0.3', 'end': '192.168.0.9'}]
        self.assertRaises(lib_exc.Conflict,
                          self.create_subnet,
                          network, cidr=subnet_cidr,
                          name=sub_name, allocation_pools=allocation_pools)

        allocation_pools = [{'start': '192.168.0.2', 'end': '192.168.0.4'}]
        subnet = self.create_subnet(network, cidr=subnet_cidr,
                                    name=sub_name,
                                    allocation_pools=allocation_pools)
        subnet_id = subnet['id']
        # can't create the overlapping allocation_pools
        new_allocation_pools = [{'start': '192.168.0.3', 'end': '192.168.0.9'}]
        self.assertRaises(lib_exc.BadRequest,
                          self.client.update_subnet,
                          subnet_id,
                          allocation_pools=new_allocation_pools)

    @test.attr(type=['negative'])
    @test.idempotent_id('ab536a40-c7ca-11e5-a311-00e0666534ba')
    def test_sf_create_quota_network(self):
        name = "sf_network"
        network_args = []
        network_one = self.create_network(network_name=name)
        self.assertEqual('ACTIVE', network_one['status'])
        self.addCleanup(self._delete_network, network_one)
        network_args.append(network_one)
        self.create_subnet(network_one)
        new_quotas = {'network': 1, 'subnet': 1}
        quotas_set = self.admin_client.update_quotas(network_one['tenant_id'],
                                                     **new_quotas)
        self.assertEqual(quotas_set['quota']['network'], 1)
        self.assertEqual(quotas_set['quota']['subnet'], 1)
        self.assertRaises(lib_exc.Conflict,
                          self.create_network,
                          network_name='network_quotas')
        self.assertRaises(lib_exc.Conflict,
                          self.create_subnet,
                          network_one)
