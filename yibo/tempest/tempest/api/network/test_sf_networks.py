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
import six
from tempest_lib.common.utils import data_utils
from tempest_lib import exceptions as lib_exc
from tempest.common import compute

from tempest.api.network import base
from tempest.common import custom_matchers
from tempest import config
from tempest import test

CONF = config.CONF


class SfNetworksTestJSON(base.BaseNetworkTest):
    """
    Tests the following operations in the Neutron API using the REST client for
    Neutron:

        create a network for a tenant
        list tenant's networks
        show a tenant network details
        create a subnet for a tenant
        list tenant's subnets
        show a tenant subnet details
        network update
        subnet update
        delete a network also deletes its subnets
        list external networks

        All subnet tests are run with ipv4.

    v2.0 of the Neutron API is assumed. It is also assumed that the following
    options are defined in the [network] section of etc/tempest.conf:

    tenant_network_cidr with a block of cidr's from which smaller blocks can be
    allocated for tenant ipv4 subnets
    """

    @classmethod
    def setup_clients(cls):
        super(SfNetworksTestJSON, cls).setup_clients()
        cls.servers_client = cls.os.servers_client
        cls.admin_client = cls.os_adm.network_client

    @classmethod
    def resource_setup(cls):
        super(SfNetworksTestJSON, cls).resource_setup()
        cls.network = cls.create_network()
        cls.name = cls.network['name']
        cls.subnet = cls._create_subnet_with_last_subnet_block(cls.network)
        cls.cidr = cls.subnet['cidr']
        cls._subnet_data = {4: {'gateway':
                                str(cls._get_gateway_from_tempest_conf(4)),
                                'allocation_pools':
                                    cls._get_allocation_pools_from_gateway(4),
                                'dns_nameservers': ['8.8.4.4', '8.8.8.8'],
                                'host_routes': [{'destination': '10.20.0.0/32',
                                                 'nexthop': '10.100.1.1'}],
                                'new_host_routes': [{'destination':
                                                    '10.20.0.0/32',
                                                     'nexthop':
                                                         '10.100.1.2'}],
                                'new_dns_nameservers': ['7.8.8.8', '7.8.4.4']}}

    @classmethod
    def _create_subnet_with_last_subnet_block(cls, network):
        """Derive last subnet CIDR block from tenant CIDR and
           create the subnet with that derived CIDR
        """
        cidr = netaddr.IPNetwork(CONF.network.tenant_network_cidr)
        mask_bits = CONF.network.tenant_network_mask_bits

        subnet_cidr = list(cidr.subnet(mask_bits))[-1]
        gateway_ip = str(netaddr.IPAddress(subnet_cidr) + 1)
        return cls.create_subnet(network, gateway=gateway_ip,
                                 cidr=subnet_cidr, mask_bits=mask_bits)

    @classmethod
    def _get_gateway_from_tempest_conf(cls, ip_version):
        """Return first subnet gateway for configured CIDR """
        if ip_version == 4:
            cidr = netaddr.IPNetwork(CONF.network.tenant_network_cidr)
            mask_bits = CONF.network.tenant_network_mask_bits
        elif ip_version == 6:
            cidr = netaddr.IPNetwork(CONF.network.tenant_network_v6_cidr)
            mask_bits = CONF.network.tenant_network_v6_mask_bits

        if mask_bits >= cidr.prefixlen:
            return netaddr.IPAddress(cidr) + 1
        else:
            for subnet in cidr.subnet(mask_bits):
                return netaddr.IPAddress(subnet) + 1

    @classmethod
    def _get_allocation_pools_from_gateway(cls, ip_version):
        """Return allocation range for subnet of given gateway"""
        gateway = cls._get_gateway_from_tempest_conf(ip_version)
        return [{'start': str(gateway + 2), 'end': str(gateway + 3)}]

    def subnet_dict(self, include_keys):
        """Return a subnet dict which has include_keys and their corresponding
           value from self._subnet_data
        """
        return dict((key, self._subnet_data[self._ip_version][key])
                    for key in include_keys)

    def _compare_resource_attrs(self, actual, expected):
        exclude_keys = set(actual).symmetric_difference(expected)
        self.assertThat(actual, custom_matchers.MatchesDictExceptForKeys(
            expected, exclude_keys))

    def _delete_network(self, network):
        # Deleting network also deletes its subnets if exists
        self.client.delete_network(network['id'])
        if network in self.networks:
            self.networks.remove(network)
        for subnet in self.subnets:
            if subnet['network_id'] == network['id']:
                self.subnets.remove(subnet)

    def _create_verify_delete_subnet(self, cidr=None, mask_bits=None,
                                     **kwargs):
        network = self.create_network()
        net_id = network['id']
        gateway = kwargs.pop('gateway', None)
        subnet = self.create_subnet(network, gateway, cidr, mask_bits,
                                    **kwargs)
        compare_args_full = dict(gateway_ip=gateway, cidr=cidr,
                                 mask_bits=mask_bits, **kwargs)
        compare_args = dict((k, v) for k, v in six.iteritems(compare_args_full)
                            if v is not None)

        if 'dns_nameservers' in set(subnet).intersection(compare_args):
            self.assertEqual(sorted(compare_args['dns_nameservers']),
                             sorted(subnet['dns_nameservers']))
            del subnet['dns_nameservers'], compare_args['dns_nameservers']

        self._compare_resource_attrs(subnet, compare_args)
        self.client.delete_network(net_id)
        body = self.client.list_networks()
        networks_list = [net['id'] for net in body['networks']]
        self.assertNotIn(net_id, networks_list)
        self.networks.pop()
        self.subnets.pop()

    def _create_verify_delete_subnet_add_router_interface(self, cidr=None,
                                                          mask_bits=None,
                                                          **kwargs):
        # create network and subnet
        network = self.create_network()
        net_id = network['id']
        gateway = kwargs.pop('gateway', None)
        subnet = self.create_subnet(network, gateway, cidr, mask_bits,
                                    **kwargs)
        compare_args_full = dict(gateway_ip=gateway, cidr=cidr,
                                 mask_bits=mask_bits, **kwargs)
        compare_args = dict((k, v) for k, v in six.iteritems(compare_args_full)
                            if v is not None)

        self._compare_resource_attrs(subnet, compare_args)
        self.assertTrue(subnet['enable_dhcp'])

        # create router and add router interface
        router = self.client.create_router(
            name=data_utils.rand_name('router-'))
        router_id = router['router']['id']
        self.client.add_router_interface_with_subnet_id(
            router_id, subnet['id'])
        # remove router_interface and delete router
        self.client.remove_router_interface_with_subnet_id(
            router_id, subnet['id'])
        self.client.delete_router(router_id)
        # delete network
        self.client.delete_network(net_id)
        body = self.client.list_networks()
        networks_list = [net['id'] for net in body['networks']]
        self.assertNotIn(net_id, networks_list)
        self.networks.pop()
        self.subnets.pop()

    def _try_delete_network(self, net_id):
        # delete network, if it exists
        try:
            self.client.delete_network(net_id)
        # if network is not found, this means it was deleted in the test
        except lib_exc.NotFound:
            pass

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

    @test.idempotent_id('9b1416a1-55fd-11e5-8f81-00e0666de3ce')
    def test_sf_delete_network_without_subnet(self):
        # Creates a network
        name = data_utils.rand_name('network-')
        body = self.client.create_network(name=name)
        network = body['network']
        net_id = network['id']

        # Delete network while the subnet not exists
        body = self.client.delete_network(net_id)

        # Verify that the network got  deleted.
        self.assertRaises(lib_exc.NotFound,
                          self.client.show_network,
                          net_id)

    @test.idempotent_id('19cde411-560f-11e5-b5ea-00e0666de3ce')
    def test_sf_create_subnet_with_default_gw_v4(self):
        # Ip version is IPv4
        net = netaddr.IPNetwork(CONF.network.tenant_network_cidr)
        gateway_ip = str(netaddr.IPAddress(net.first + 1))
        name = data_utils.rand_name('network-')
        network = self.client.create_network(name=name)['network']
        self.addCleanup(self._delete_network, network)
        subnet = self.create_subnet(network,
                                    gateway=gateway_ip,
                                    ip_version=4)
        # Verifies Subnet GW in IPv4
        self.assertEqual(subnet['gateway_ip'], gateway_ip)

    @test.idempotent_id('9f2a7640-56ce-11e5-8fd4-00e0666de3ce')
    def test_sf_create_delete_subnet_with_dns_server(self):
        self._create_verify_delete_subnet(
            **self.subnet_dict(['dns_nameservers']))

    @test.idempotent_id('083e6000-56d0-11e5-9f76-00e0666de3ce')
    def test_sf_create_delete_subnet_with_dhcp_disabled(self):
        self._create_verify_delete_subnet(enable_dhcp=False)

    @test.idempotent_id('0eb18cb0-56e3-11e5-9833-00e0666de3ce')
    def test_sf_update_subnet_with_gw(self):
        name = data_utils.rand_name('network-')
        network = self.client.create_network(name=name)['network']
        self.addCleanup(self._delete_network, network)
        subnet = self.create_subnet(
            network, **self.subnet_dict(['gateway', 'allocation_pools']))
        subnet_id = subnet['id']
        new_gateway = str(netaddr.IPAddress(
            self._subnet_data[self._ip_version]['gateway']) + 1)
        # Verify subnet update
        kwargs = {'gateway_ip': new_gateway}

        new_name = "sf-new-subnet"
        body = self.client.update_subnet(subnet_id, name=new_name,
                                         **kwargs)
        updated_subnet = body['subnet']
        kwargs['name'] = new_name

        self._compare_resource_attrs(updated_subnet, kwargs)

    @test.idempotent_id('2be96930-c7c5-11e5-bdd7-00e0666534ba')
    def test_sf_show_network_and_subnet(self):
        # Creates a network and subnet
        name = data_utils.rand_name('network-')
        network = self.client.create_network(name=name)['network']
        net_id = network['id']
        self.addCleanup(self._delete_network, network)
        subnet = self.create_subnet(network)
        subnet_id = subnet['id']
        net_detail = self.client.show_network(net_id)['network']
        self.assertEqual(net_detail['name'], name)
        subnet_detail = self.client.show_subnet(subnet_id)['subnet']
        self.assertEqual(subnet_detail['network_id'], net_id)
        self.assertTrue(subnet['enable_dhcp'])

    @test.idempotent_id('8d35a521-56e9-11e5-96eb-00e0666de3ce')
    def test_sf_update_subnet_add_remove_router_interfaces(self):
        name = data_utils.rand_name('network-')
        network = self.client.create_network(name=name)['network']
        self.addCleanup(self._delete_network, network)

        subnet = self.create_subnet(
            network, **self.subnet_dict(['gateway', 'allocation_pools']))
        subnet_id = subnet['id']
        # create router and add router interface
        router = self.client.create_router(
            name=data_utils.rand_name('router-'))
        router_id = router['router']['id']
        self.client.add_router_interface_with_subnet_id(
            router_id, subnet_id)
        # remove router_interface and delete router
        self.client.remove_router_interface_with_subnet_id(
            router_id, subnet_id)
        self.client.delete_router(router_id)

    @test.idempotent_id('6ad1b9de-575e-11e5-a9ef-00e0666de3ce')
    def test_sf_update_subnet_host_routes_dhcp_disable(self):
        name = data_utils.rand_name('network-')
        network = self.client.create_network(name=name)['network']
        self.addCleanup(self._delete_network, network)

        subnet = self.create_subnet(
            network, **self.subnet_dict(['gateway', 'host_routes',
                                         'dns_nameservers',
                                         'allocation_pools']))
        subnet_id = subnet['id']
        # Verify subnet update
        new_host_routes = self._subnet_data[self._ip_version][
            'new_host_routes']

        kwargs = {'host_routes': new_host_routes, 'enable_dhcp': False}

        new_name = "sf-new-subnet"
        body = self.client.update_subnet(subnet_id, name=new_name,
                                         **kwargs)
        updated_subnet = body['subnet']
        kwargs['name'] = new_name

        self._compare_resource_attrs(updated_subnet, kwargs)

    @test.idempotent_id('e62ab50f-56eb-11e5-b695-00e0666de3ce')
    def test_sf_update_subnet_dns_server(self):
        name = data_utils.rand_name('network-')
        network = self.client.create_network(name=name)['network']
        self.addCleanup(self._delete_network, network)

        subnet = self.create_subnet(
            network, **self.subnet_dict(['gateway', 'host_routes',
                                         'dns_nameservers',
                                         'allocation_pools']))
        subnet_id = subnet['id']
        # Verify subnet update

        new_dns_nameservers = self._subnet_data[self._ip_version][
            'new_dns_nameservers']

        kwargs = {'dns_nameservers': new_dns_nameservers, 'enable_dhcp': True}

        new_name = "sf-new-subnet"
        body = self.client.update_subnet(subnet_id, name=new_name,
                                         **kwargs)
        updated_subnet = body['subnet']
        kwargs['name'] = new_name
        self.assertEqual(sorted(updated_subnet['dns_nameservers']),
                         sorted(kwargs['dns_nameservers']))
        del subnet['dns_nameservers'], kwargs['dns_nameservers']

        self._compare_resource_attrs(updated_subnet, kwargs)

    @test.attr(type='smoke')
    @test.idempotent_id('0fb0efc0-56ed-11e5-8a03-00e0666de3ce')
    def test_sf_update_subnet_gw_allocation_pools(self):
        name = data_utils.rand_name('network-')
        network = self.client.create_network(name=name)['network']
        self.addCleanup(self._delete_network, network)

        subnet = self.create_subnet(
            network, **self.subnet_dict(['gateway', 'allocation_pools']))
        subnet_id = subnet['id']
        new_gateway = netaddr.IPAddress(
            self._subnet_data[self._ip_version]['gateway']) + 1
        new_allocation_pools = [{'start': str(new_gateway + 1), 'end':
                                 str(new_gateway + 7)}]
        # Verify subnet update
        kwargs = {'gateway_ip': str(new_gateway), 'allocation_pools':
                  new_allocation_pools}

        new_name = "sf-new-subnet"
        body = self.client.update_subnet(subnet_id, name=new_name,
                                         **kwargs)
        updated_subnet = body['subnet']
        kwargs['name'] = new_name
        self._compare_resource_attrs(updated_subnet, kwargs)

    @test.idempotent_id('a4d9ec4c-0306-4111-a75c-db01a709030b')
    def test_sf_create_delete_subnet_multi_attributes(self):
        self._create_verify_delete_subnet(
            enable_dhcp=True,
            **self.subnet_dict(['gateway', 'allocation_pools']))

    @test.idempotent_id('e4d9af2e-5697-11e5-b3d1-00e0666de3ce')
    def test_sf_create_delete_subnet_gw_add_router_interfaces(self):
        self._create_verify_delete_subnet_add_router_interface(
            enable_dhcp=True,
            **self.subnet_dict(['gateway']))

    @test.idempotent_id('ceb82db0-5699-11e5-bbec-00e0666de3ce')
    def test_sf_create_delete_subnet_gw_dns(self):
        self._create_verify_delete_subnet(
            enable_dhcp=True,
            **self.subnet_dict(['gateway', 'dns_nameservers']))

    @test.idempotent_id('adb8509e-569d-11e5-9019-00e0666de3ce')
    def test_sf_create_del_subnet_with_alloc_pool_add_router_interfaces(self):
        self._create_verify_delete_subnet_add_router_interface(
            **self.subnet_dict(['gateway', 'allocation_pools']))

    @test.idempotent_id('ebd2d5c0-569f-11e5-a4d0-00e0666de3ce')
    def test_sf_create_delete_subnet_with_allocation_pools_in_all_ips(self):
        # Create a network
        name = "sf-network"
        network = self.client.create_network(name=name)['network']
        self.addCleanup(self._delete_network, network)
        self.assertEqual('ACTIVE', network['status'])
        # Create the different network with same subnet_name and same CIDR
        sub_name = "sf-subnet"
        mask_bits = CONF.network.tenant_network_mask_bits
        subnet_cidr = netaddr.IPNetwork('192.168.0.0/28')
        subnet = self.create_subnet(network, cidr=subnet_cidr,
                                    name=sub_name, mask_bits=mask_bits)

        self.assertEqual(netaddr.IPNetwork(subnet['cidr']), subnet_cidr,
                         'The created subnet cidr Mismatch')
        self.assertEqual(subnet['allocation_pools'][0]['start'], '192.168.0.2')
        self.assertEqual(subnet['allocation_pools'][0]['end'], '192.168.0.14')

    @test.attr(type='smoke')
    @test.idempotent_id('85a6ccde-56a2-11e5-b259-00e0666de3ce')
    def test_sf_create_delete_subnet_all_attributes(self):
        self._create_verify_delete_subnet(
            **self.subnet_dict(['gateway', 'allocation_pools']))

    @test.idempotent_id('cd5ccb1e-5b75-11e5-a24c-00e0666de3ce')
    def test_sf_create_same_network_subnet_diff_subname_cidr(self):
        # Create a network
        name = "sf-network"
        network = self.client.create_network(name=name)['network']
        self.addCleanup(self._delete_network, network)
        self.assertEqual('ACTIVE', network['status'])
        # Create the different network with same subnet_name and same CIDR
        sub1_name = "sf-subnet1"
        sub2_name = "sf-subnet2"
        mask_bits = CONF.network.tenant_network_mask_bits
        subnet1_cidr = netaddr.IPNetwork('10.10.0.0/28')
        subnet2_cidr = netaddr.IPNetwork('192.168.0.0/28')
        subnet1 = self.create_subnet(network, cidr=subnet1_cidr,
                                     name=sub1_name, mask_bits=mask_bits)

        self.assertEqual(netaddr.IPNetwork(subnet1['cidr']), subnet1_cidr,
                         'The created subnet cidr Mismatch')

        subnet2 = self.create_subnet(network, cidr=subnet2_cidr,
                                     name=sub2_name, mask_bits=mask_bits)

        self.assertEqual(netaddr.IPNetwork(subnet2['cidr']), subnet2_cidr,
                         'The created subnet cidr Mismatch')
        # Verifies  two  subnets in subnet list
        body = self.client.list_subnets()
        subnets = [sub['id'] for sub in body['subnets']
                   if sub['network_id'] == network['id']]
        subnet_ids = [sub['id'] for sub in (subnet1, subnet2)]
        self.assertItemsEqual(subnets, subnet_ids)

    @test.idempotent_id('0d9c9d0f-5b7f-11e5-b69b-00e0666de3ce')
    def test_sf_update_subnet_with_dup_name(self):
        # create subnet name blank
        name = data_utils.rand_name('network-')
        network = self.client.create_network(name=name)['network']
        self.addCleanup(self.client.delete_network, network['id'])
        subnet1 = self.create_subnet(network)
        subnet_id = subnet1['id']
        self.assertEqual(subnet1['name'], '')
        # Create a subnet name is not empty
        subname = 'sf-subnet'
        mask_bits = CONF.network.tenant_network_mask_bits
        subnet_cidr = netaddr.IPNetwork('192.168.0.0/22')
        subnet2 = self.create_subnet(network, cidr=subnet_cidr, name=subname,
                                     mask_bits=mask_bits)
        # Verifies subnet name is subname
        self.assertEqual(subnet2['name'], subname)
        # Verify subnet update
        new_name = "new-sf-subnet"
        body = self.client.update_subnet(subnet_id, name=new_name)
        updated_subnet = body['subnet']
        self.assertEqual(updated_subnet['name'], new_name)

    @test.idempotent_id('986ff85e-5c42-11e5-9b60-00e0666de3ce')
    def test_sf_create_update_network_without_subnet(self):
        # Create a network
        name = data_utils.rand_name('network-')
        network = self.client.create_network(name=name)['network']
        self.addCleanup(self._delete_network, network)
        net_id = network['id']
        self.assertEqual('ACTIVE', network['status'])
        # Verify network update, without the case of subnet
        new_name = "sf-network"
        body = self.client.update_network(net_id, name=new_name)
        updated_net = body['network']
        self.assertEqual(updated_net['name'], new_name)

    @test.idempotent_id('b32d7cb0-fba0-11e5-b3a4-00e0666de3ce')
    def test_sf_delete_network_without_server_port(self):
        # create network
        name = "sf-network"
        network = self.create_network(network_name=name)
        network_id = network['id']
        # self.addCleanup(self._delete_network, network)
        self.assertEqual('ACTIVE', network['status'])
        subnet = self.create_subnet(network)
        subnet_id = subnet['id']
        # server creation,network port used
        net = [{'uuid': network['id']}]
        server = self._create_test_server(network['tenant_id'],
                                          networks=net, wait_until='ACTIVE')
        # delete server,then delete subnet
        # When the port is not used to delete the subnet
        self.servers_client.delete_server(server['id'])
        self.servers_client.wait_for_server_termination(server['id'])
        # delete subnet
        self._delete_network(network)
        self.assertRaises(lib_exc.NotFound,
                          self.client.show_subnet,
                          subnet_id)
        self.assertRaises(lib_exc.NotFound,
                          self.client.show_network,
                          network_id)


class BulkNetworkOpsTestJSON(base.BaseNetworkTest):
    """
    Tests the following operations in the Neutron API using the REST client for
    Neutron:

        bulk network creation
        bulk subnet creation
        bulk port creation
        list tenant's networks

    v2.0 of the Neutron API is assumed. It is also assumed that the following
    options are defined in the [network] section of etc/tempest.conf:

        tenant_network_cidr with a block of cidr's from which smaller blocks
        can be allocated for tenant networks

        tenant_network_mask_bits with the mask bits to be used to partition the
        block defined by tenant-network_cidr
    """

    def _delete_networks(self, created_networks):
        for n in created_networks:
            self.client.delete_network(n['id'])
        # Asserting that the networks are not found in the list after deletion
        body = self.client.list_networks()
        networks_list = [network['id'] for network in body['networks']]
        for n in created_networks:
            self.assertNotIn(n['id'], networks_list)

    def _delete_subnets(self, created_subnets):
        for n in created_subnets:
            self.client.delete_subnet(n['id'])
        # Asserting that the subnets are not found in the list after deletion
        body = self.client.list_subnets()
        subnets_list = [subnet['id'] for subnet in body['subnets']]
        for n in created_subnets:
            self.assertNotIn(n['id'], subnets_list)

    def _delete_ports(self, created_ports):
        for n in created_ports:
            self.client.delete_port(n['id'])
        # Asserting that the ports are not found in the list after deletion
        body = self.client.list_ports()
        ports_list = [port['id'] for port in body['ports']]
        for n in created_ports:
            self.assertNotIn(n['id'], ports_list)

    @test.idempotent_id('3245c00f-576a-11e5-99ae-00e0666de3ce')
    def test_sf_delete_multi_network(self):
        # Creates 2 networks
        network_names = [data_utils.rand_name('network-'),
                         data_utils.rand_name('network-')]
        body = self.client.create_bulk_network(network_names)
        created_networks = body['networks']

        # Asserting that the networks are found in the list after creation
        body = self.client.list_networks()
        networks_list = [network['id'] for network in body['networks']]
        for n in created_networks:
            self.assertIsNotNone(n['id'])
            self.assertIn(n['id'], networks_list)
        # Delete networks
        self._delete_networks(created_networks)

    @test.idempotent_id('bdb6fb5e-5764-11e5-9ea8-00e0666de3ce')
    def test_sf_delete_multi_subnet(self):
        networks = [self.create_network(), self.create_network()]
        # Creates 2 subnets
        # IP version 4
        cidr = netaddr.IPNetwork(CONF.network.tenant_network_cidr)
        mask_bits = CONF.network.tenant_network_mask_bits

        cidrs = [subnet_cidr for subnet_cidr in cidr.subnet(mask_bits)]

        names = [data_utils.rand_name('subnet-') for i in range(len(networks))]
        subnets_list = []
        for i in range(len(names)):
            p1 = {
                'network_id': networks[i]['id'],
                'cidr': str(cidrs[(i + 1)]),
                'name': names[i],
                'ip_version': self._ip_version
            }
            subnets_list.append(p1)
        del subnets_list[1]['name']
        body = self.client.create_bulk_subnet(subnets_list)
        created_subnets = body['subnets']
        self.addCleanup(self._delete_subnets, created_subnets)

        # Asserting that the subnets are found in the list after creation
        body = self.client.list_subnets()
        subnets_list = [subnet['id'] for subnet in body['subnets']]
        for n in created_subnets:
            self.assertIsNotNone(n['id'])
            self.assertIn(n['id'], subnets_list)
        # Delete two subnet
        self._delete_subnets

    @test.idempotent_id('cb7d9d40-5777-11e5-9b28-00e0666de3ce')
    def test_sf_delete_multi_port(self):
        networks = [self.create_network(), self.create_network()]
        # Creates 2 ports
        names = [data_utils.rand_name('port-') for i in range(len(networks))]
        port_list = []
        state = [True, False]
        for i in range(len(names)):
            p1 = {
                'network_id': networks[i]['id'],
                'name': names[i],
                'admin_state_up': state[i],
            }
            port_list.append(p1)
        del port_list[1]['name']
        body = self.client.create_bulk_port(port_list)
        created_ports = body['ports']
        self.addCleanup(self._delete_ports, created_ports)

        # Asserting that the ports are found in the list after creation
        body = self.client.list_ports()
        ports_list = [port['id'] for port in body['ports']]
        for n in created_ports:
            self.assertIsNotNone(n['id'])
            self.assertIn(n['id'], ports_list)
        # Delete ports
        self._delete_ports


class SfNetworksIpV4TestJSON(SfNetworksTestJSON):
    @test.idempotent_id('d68ee64f-578e-11e5-8bd9-00e0666de3ce')
    def test_sf_delete_subnet_with_default_gw(self):
        name = data_utils.rand_name('network-')
        network = self.client.create_network(name=name)['network']
        self.addCleanup(self.client.delete_network, network['id'])
        subnet = self.create_subnet(network)
        gateway_ip = str(netaddr.IPNetwork(subnet['cidr']).ip + 1)
        # Verifies Subnet GW in IPv4
        self.assertEqual(subnet['gateway_ip'], gateway_ip)
        subnet_id = subnet['id']
        self.client.delete_subnet(subnet_id)
        # Verify that the subnet got deleted.
        self.assertRaises(lib_exc.NotFound,
                          self.client.show_subnet,
                          subnet_id)

    @test.idempotent_id('49e5d1cf-5795-11e5-b203-00e0666de3ce')
    def test_sf_list_subnet_with_gw4_one_network(self):
        name = data_utils.rand_name('network-')
        network = self.client.create_network(name=name)['network']
        self.addCleanup(self.client.delete_network, network['id'])
        ipv4_gateway = self.subnet_dict(['gateway'])['gateway']
        subnet1 = self.create_subnet(network,
                                     ip_version=4,
                                     gateway=ipv4_gateway)
        self.assertEqual(netaddr.IPNetwork(subnet1['cidr']).version, 4,
                         'The created subnet is not IPv4')
        subnet2 = self.create_subnet(network,
                                     gateway=None,
                                     ip_version=4)
        self.assertEqual(netaddr.IPNetwork(subnet2['cidr']).version, 4,
                         'The created subnet is not IPv4')
        # Verifies Subnet GW is set in IPv4
        self.assertEqual(subnet1['gateway_ip'], ipv4_gateway)
        # Verifies Subnet GW is None in IPv4
        self.assertEqual(subnet2['gateway_ip'], None)
        # Verifies all 2 subnets in the same network
        body = self.client.list_subnets()
        subnets = [sub['id'] for sub in body['subnets']
                   if sub['network_id'] == network['id']]
        test_subnet_ids = [sub['id'] for sub in (subnet1, subnet2)]
        self.assertItemsEqual(subnets,
                              test_subnet_ids,
                              'Subnet are not in the same network')

    @test.idempotent_id('f31de170-579a-11e5-a22e-00e0666de3ce')
    def test_sf_create_subnet_with_gw4_none(self):
        name = data_utils.rand_name('network-')
        network = self.client.create_network(name=name)['network']
        self.addCleanup(self.client.delete_network, network['id'])
        subnet1 = self.create_subnet(network,
                                     gateway=None,
                                     ip_version=4)
        self.assertEqual(netaddr.IPNetwork(subnet1['cidr']).version, 4,
                         'The created subnet is not IPv4')
        # Verifies Subnet GW is None in IPv4
        self.assertEqual(subnet1['gateway_ip'], None)
        # Verifies subnet created
        body = self.client.list_subnets()
        subnets = [subnet['id'] for subnet in body['subnets']
                   if subnet['id'] == self.subnet['id']]
        self.assertNotEmpty(subnets, "Created subnet not found in the list")

    @test.idempotent_id('add42d4f-5b90-11e5-884f-00e0666de3ce')
    def test_sf_delete_network_with_router_port(self):
        # create network
        name = "sf-network"
        network = self.create_network(network_name=name)
        self.assertEqual('ACTIVE', network['status'])
        subnet = self.create_subnet(network)
        # router creation
        router = self.client.create_router(name='sf-router')
        router_id = router['router']['id']
        # subnet attach router
        self.client.add_router_interface_with_subnet_id(
            router_id, subnet['id'])
        # When the port is used to delete the network
        # remove router_interface
        # delete subnet
        subnet_id = subnet['id']
        network_id = network['id']
        self._delete_network(network)
        # Verify that the subnet and network got deleted.
        self.assertRaises(lib_exc.NotFound,
                          self.client.show_subnet,
                          subnet_id)
        self.assertRaises(lib_exc.NotFound,
                          self.client.show_network,
                          network_id)
        # delete router
        self.client.delete_router(router_id)

