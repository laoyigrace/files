# Copyright 2012 OpenStack Foundation
# Copyright 2013 Hewlett-Packard Development Company, L.P.
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
import collections
import six

from oslo_log import log as logging
from tempest_lib import exceptions as lib_exc

from tempest.common import waiters
from tempest.common.utils import data_utils
from tempest import config
from tempest import exceptions
from tempest.sf_scenario import sf_manager
from tempest.scenario import manager
from tempest import test

CONF = config.CONF
LOG = logging.getLogger(__name__)

Floating_IP_tuple = collections.namedtuple('Floating_IP_tuple',
                                           ['floating_ip', 'server'])


class TestNetworkOps(sf_manager.SfScenarioTest, manager.NetworkScenarioTest):

    """
    This smoke test suite assumes that Nova has been configured to
    boot VM's with Neutron-managed networking, and attempts to
    verify network connectivity as follows:

     There are presumed to be two types of networks: tenant and
     public.  A tenant network may or may not be reachable from the
     Tempest host.  A public network is assumed to be reachable from
     the Tempest host, and it should be possible to associate a public
     ('floating') IP address with a tenant ('fixed') IP address to
     facilitate external connectivity to a potentially unroutable
     tenant IP address.

     This test suite can be configured to test network connectivity to
     a VM via a tenant network, a public network, or both.  If both
     networking types are to be evaluated, tests that need to be
     executed remotely on the VM (via ssh) will only be run against
     one of the networks (to minimize test execution time).

     Determine which types of networks to test as follows:

     * Configure tenant network checks (via the
       'tenant_networks_reachable' key) if the Tempest host should
       have direct connectivity to tenant networks.  This is likely to
       be the case if Tempest is running on the same host as a
       single-node devstack installation with IP namespaces disabled.

     * Configure checks for a public network if a public network has
       been configured prior to the test suite being run and if the
       Tempest host should have connectivity to that public network.
       Checking connectivity for a public network requires that a
       value be provided for 'public_network_id'.  A value can
       optionally be provided for 'public_router_id' if tenants will
       use a shared router to access a public network (as is likely to
       be the case when IP namespaces are not enabled).  If a value is
       not provided for 'public_router_id', a router will be created
       for each tenant and use the network identified by
       'public_network_id' as its gateway.

    """

    @classmethod
    def skip_checks(cls):
        super(TestNetworkOps, cls).skip_checks()
        if not (CONF.network.tenant_networks_reachable
                or CONF.network.public_network_id):
            msg = ('Either tenant_networks_reachable must be "true", or '
                   'public_network_id must be defined.')
            raise cls.skipException(msg)
        for ext in ['router', 'security-group']:
            if not test.is_extension_enabled(ext, 'network'):
                msg = "%s extension not enabled." % ext
                raise cls.skipException(msg)

    @classmethod
    def setup_credentials(cls):
        # Create no network resources for these tests.
        cls.set_network_resources()
        super(TestNetworkOps, cls).setup_credentials()

    def setUp(self):
        super(TestNetworkOps, self).setUp()
        self.keypairs = {}
        self.servers = []

    @classmethod
    def resource_setup(cls):
        super(TestNetworkOps, cls).resource_setup()
        cls.routers = []
        cls.fip_allocs = []
        cls.ext_net_id = CONF.network.public_network_id
        cls.net, cls.subnet = cls._create_net()
        cls.router = cls.create_router(data_utils.rand_name('router-'),
                                       admin_state_up=True,
                                       external_network_id=cls.ext_net_id)
        cls.nameserver = cls.sf_network_client.create_nameserver(major=True, address='1.8.8.8')
        cls.sf_network_client.add_router_interface(
            router_id=cls.router['id'],
            subnet_id=cls.subnet['subnet']['id'])

    @classmethod
    def resource_cleanup(cls):
        # if we don't delete the server first, the port will still be part of
        # the subnet and we'll get a 409 from Neutron when trying to delete
        # the subnet.
        cls.cleanup_resources(cls.port_delete, cls.routers)
        super(TestNetworkOps, cls).resource_cleanup()
        cls.cleanup_resources(cls.fip_alloc_delete, cls.fip_allocs)
        cls.cleanup_resources(cls.router_delete, cls.routers)

    @classmethod
    def create_router(cls, router_name=None, admin_state_up=False,
                      external_network_id=None, enable_snat=None,
                      **kwargs):
        ext_gw_info = {}
        if external_network_id:
            ext_gw_info['network_id'] = external_network_id
        if enable_snat:
            ext_gw_info['enable_snat'] = enable_snat
        body = cls.network_client.create_router(
            router_name, external_gateway_info=ext_gw_info,
            admin_state_up=admin_state_up, **kwargs)
        router = body['router']
        print("+++sf, router = %s", router)
        cls.routers.append(router['id'])
        return router

    @classmethod
    def fip_alloc_delete(self, fip_alloc_id):
        try:
            self.sf_network_client.delete_floatingip_alloc(fip_alloc_id)
        except Exception:
            pass

    def fip_delete(self, sffip_id):
        try:
            self.sf_network_client.delete_floatingip(sffip_id)
        except Exception:
            pass

    @classmethod
    def port_delete(self, router_id):
        body = self.network_client.list_router_interfaces(router_id)
        print('+++sf, body = %s', body)
        interfaces = body['ports']
        for i in interfaces:
            try:
                self.network_client.remove_router_interface_with_subnet_id(
                    router_id, i['fixed_ips'][0]['subnet_id'])
            except lib_exc.NotFound:
                pass

    @classmethod
    def router_delete(self, router_id):
        try:
            self.network_client.delete_router(router_id)
        except Exception:
            pass

    def check_networks(self):
        """
        Checks that we see the newly created network/subnet/router via
        checking the result of list_[networks,routers,subnets]
        """

        seen_nets = self._list_networks()
        seen_names = [n['name'] for n in seen_nets]
        seen_ids = [n['id'] for n in seen_nets]
        self.assertIn(self.net['network']['name'], seen_names)
        self.assertIn(self.net['network']['id'], seen_ids)

        if self.subnet:
            seen_subnets = self._list_subnets()
            seen_net_ids = [n['network_id'] for n in seen_subnets]
            seen_subnet_ids = [n['id'] for n in seen_subnets]
            self.assertIn(self.net['network']['id'], seen_net_ids)
            self.assertIn(self.subnet['subnet']['id'], seen_subnet_ids)

        if self.router:
            seen_routers = self._list_routers()
            seen_router_ids = [n['id'] for n in seen_routers]
            seen_router_names = [n['name'] for n in seen_routers]
            self.assertIn(self.router['name'],
                          seen_router_names)
            self.assertIn(self.router['id'],
                          seen_router_ids)

    def create_sf_server(self, sys_disk=1, cpu=1, ram=512,
                         **kwargs):
        name = data_utils.rand_name('sf-server')
        disk_config = 'AUTO'
        image_id = CONF.compute.image_ref
        block_device_mapping_v2 = [
            {
                'boot_index': '0',
                'uuid': u'%s' % image_id,
                'source_type': 'image',
                'volume_size': u'%s' % sys_disk,
                'destination_type': 'volume',
                'delete_on_termination': 1
            },
        ]
        networks = []
        network = {'uuid': self.net['network']['id']}
        flavor = self._create_flavor(sys_disk, ram, cpu)
        if kwargs.get('qos_uplink'):
            network['qos_uplink'] = kwargs.get('qos_uplink')
        if kwargs.get('qos_downlink'):
            network['qos_downlink'] = kwargs.get('qos_downlink')
        networks.append(network)

        create_kwargs = {
            'networks': networks,
            'block_device_mapping_v2': block_device_mapping_v2,
            'disk_config': disk_config
        }

        server = self.create_server(name=name, flavor=flavor['id'],
                                    create_kwargs=create_kwargs)

        return server

    def _get_fixed_ip(self, instance_uuid):
        addresses = self.servers_client.list_addresses(instance_uuid)
        print("+++sf, address = %s", addresses)
        self.assertTrue(len(addresses) >= 1)
        for network_name, network_addresses in six.iteritems(addresses):
            self.assertTrue(len(network_addresses) >= 1)
            for address in network_addresses:
                self.assertTrue(address['addr'])
                return address['addr']

    def _get_fip(self, fixed_ip):
        fips = self.sf_network_client.list_floatingips()
        sffip_id = None
        for one in fips.get('one_to_one_nats', []):
            if one.get('intranet_ip') == fixed_ip:
                sffip_id = one.get('sffip_id')
                break

        if sffip_id is None:
            return None

        sfip_alloc = self.sf_network_client.show_floatingip_alloc(sffip_id)
        if sfip_alloc is None:
            return None
        sfip_alloc = sfip_alloc.get('sf_fip_alloc', {})
        if sfip_alloc.get('id'):
            self.fip_allocs.append(sfip_alloc.get('id'))
        return sfip_alloc

    def associate_floating_ip(self, server):

        floating_ip_alloc = self.sf_network_client.create_floatingip_alloc(
            floating_network_id=self.ext_net_id)
        self.assertIsNotNone(floating_ip_alloc)

        fixed_ip = self._get_fixed_ip(server['id'])

        body = self.sf_network_client.create_floatingip(
            router_id=self.router['id'],
            sffip_id=floating_ip_alloc['sf_fip_alloc']
            ['id'][0],
            tenant_id=self.tenant_id,
            intranet_ip=fixed_ip)

        created_floating_ip = body['one_to_one_nat']
        self.addCleanup(self.sf_network_client.delete_floatingip_alloc,
                        floating_ip_alloc['sf_fip_alloc']['id'][0])
        self.addCleanup(self.fip_delete,
                        created_floating_ip['id'][0])
        self.assertIsNotNone(created_floating_ip['id'])
        self.assertIsNotNone(created_floating_ip['sffip_id'])
        self.assertEqual(created_floating_ip['router_id'], self.router['id'])
        self.assertEqual(created_floating_ip['tenant_id'], self.tenant_id)
        sfip_alloc = self._get_fip(fixed_ip)
        self.assertTrue(sfip_alloc)
        return sfip_alloc

    def disassociate_floating_ip(self, server):
        fixed_ip = self._get_fixed_ip(server['id'])
        def get_one_nat():
            fips = self.sf_network_client.list_floatingips()
            id = None
            for one in fips.get('one_to_one_nats', []):
                if one.get('intranet_ip') == fixed_ip:
                    id = one.get('id')
                    break
            return id
        id = get_one_nat()
        self.assertIsNotNone(id)
        self.sf_network_client.delete_floatingip(id)
        id = get_one_nat()
        self.assertIsNone(id)

    def control_server(self):

        if self.control_server is not None:
            return

        self.check_networks()
        self.control_server = self.create_sf_server(qos_uplink=20480,
                                            qos_downlink=20480)
        LOG.debug("+++sf ,server = %s", self.control_server)

        self.assertTrue(self.control_server)
        fixed_ip = self._get_fixed_ip(self.control_server['id'])
        sfip_alloc = self._get_fip(fixed_ip)
        self.fip = sfip_alloc['external_ip']
        self.assertTrue(self.fip)
        self.check_public_network_connectivity(self.fip)

    def check_public_network_connectivity(
            self, fip, should_connect=True,
            msg=None,should_check_floating_ip_status=False):
        """Verifies connectivty to a VM via public network and floating IP,
        and verifies floating IP has resource status is correct.

        :param should_connect: bool. determines if connectivity check is
        negative or positive.
        :param msg: Failure message to add to Error message. Should describe
        the place in the test scenario where the method was called,
        to indicate the context of the failure
        :param should_check_floating_ip_status: bool. should status of
        floating_ip be checked or not
        """
        ssh_login = CONF.compute.image_ssh_user

        floatingip_status = 'DOWN'
        if should_connect:
            floatingip_status = 'ACTIVE'
        # Check FloatingIP Status before initiating a connection
        if should_check_floating_ip_status:
            self.check_floating_ip_status(fip, floatingip_status)
        # call the common method in the parent class
        super(TestNetworkOps, self).check_public_network_connectivity(
            fip, ssh_login, None, should_connect, msg,
            self.servers)

    @test.attr(type='smoke')
    def test_create_server_with_fip(self):
        server = self.create_sf_server(qos_uplink=20480, qos_downlink=20480)
        LOG.debug("+++sf ,server = %s", server)

        self.assertTrue(server)
        fixed_ip = self._get_fixed_ip(server['id'])
        sfip_alloc = self._get_fip(fixed_ip)
        fip = sfip_alloc['external_ip']
        self.assertTrue(fip)
        self.check_public_network_connectivity(fip)

    @test.attr(type='smoke')
    def test_create_server_associate_disassociate_fip(self):
        server = self.create_sf_server()
        LOG.debug("+++sf ,server = %s", server)

        self.assertTrue(server)
        sfip_alloc = self.associate_floating_ip(server)
        cur_fip = sfip_alloc['external_ip']
        self.assertTrue(cur_fip)
        self.assertTrue(cur_fip)
        self.check_public_network_connectivity(cur_fip)
        self.disassociate_floating_ip(server)
        self.check_public_network_connectivity(cur_fip, should_connect=False)

    @test.attr(type='smoke')
    def test_create_server_associate_disassociate_fip2(self):
        server = self.create_sf_server()
        LOG.debug("+++sf ,server = %s", server)

        self.assertTrue(server)

        self.servers_client.stop(server['id'])
        waiters.wait_for_server_status(self.servers_client,
                                       server['id'], 'SHUTOFF')

        sfip_alloc = self.associate_floating_ip(server)
        cur_fip = sfip_alloc['external_ip']
        self.assertTrue(cur_fip)
        self.assertTrue(cur_fip)

        self.servers_client.start(server['id'])
        waiters.wait_for_server_status(self.servers_client, server['id'], 'ACTIVE')

        self.check_public_network_connectivity(cur_fip)
        self.disassociate_floating_ip(server)
        self.check_public_network_connectivity(cur_fip, should_connect=False)

    @test.attr(type='smoke')
    def test_two_servers(self):
        server1 = self.create_sf_server(qos_uplink=20480, qos_downlink=20480)
        LOG.debug("+++sf ,server1 = %s", server1)
        server2 = self.create_sf_server(qos_uplink=20480, qos_downlink=20480)
        LOG.debug("+++sf ,server2 = %s", server2)

        self.assertTrue(server1)
        fixed_ip1 = self._get_fixed_ip(server1['id'])
        fixed_ip2 = self._get_fixed_ip(server2['id'])
        sfip_alloc1 = self._get_fip(fixed_ip1)
        fip1 = sfip_alloc1['external_ip']
        self.assertTrue(fip1)
        self.check_public_network_connectivity(fip1)

        sfip_alloc2 = self._get_fip(fixed_ip2)
        fip2 = sfip_alloc2['external_ip']
        self.assertTrue(fip2)
        self.check_public_network_connectivity(fip2)

        # two instances can ping each other
        ssh_client = self._ssh_to_server(fip1, None)
        ret = ssh_client.ping_host(host=fixed_ip2)
        LOG.debug("+++sf ,ret = %s", ret)

        dns = ssh_client.get_dns_servers()
        self.assertEqual(str(dns[0]), self.nameserver['sfnameserver']['address'])

        ssh_client = self._ssh_to_server(fip2, None)
        ret = ssh_client.ping_host(host=fixed_ip1)
        LOG.debug("+++sf ,ret = %s", ret)
