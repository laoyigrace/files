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

from oslo_log import log as logging

from tempest.common import waiters
from tempest.common.utils import data_utils
from tempest import config
from tempest.sf_scenario import sf_manager
from tempest import test

CONF = config.CONF
LOG = logging.getLogger(__name__)

Floating_IP_tuple = collections.namedtuple('Floating_IP_tuple',
                                           ['floating_ip', 'server'])


class TestServerOps(sf_manager.SfNetworkScenarioTest):

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
        super(TestServerOps, cls).skip_checks()
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
        super(TestServerOps, cls).setup_credentials()

    def setUp(self):
        super(TestServerOps, self).setUp()
        self.keypairs = {}
        self.servers = []

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
        self.assertTrue(self.ping_ip_address(self.fip, ping_timeout=120))

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
        super(TestServerOps, self).check_public_network_connectivity(
            fip, ssh_login, None, should_connect, msg,
            self.servers)

    @test.attr(type='smoke')
    def test_server_1cpu_1mem(self):
        cpu = 1
        ram=1024
        server = self.create_sf_server(
            cpu=cpu, ram=ram,
            qos_uplink=20480, qos_downlink=20480)
        LOG.debug("+++sf ,server = %s", server)

        self.assertTrue(server)
        fixed_ip = self._get_fixed_ip(server['id'])
        sfip_alloc = self._get_fip(fixed_ip)
        fip = sfip_alloc['external_ip']
        self.assertTrue(fip)
        self.check_public_network_connectivity(fip)
        ssh_client = self._ssh_to_server(fip, None)
        get_ram = ssh_client.get_ram_size_in_mb()
        LOG.debug("+++sf, ram = %s, get_ram = %s", ram, get_ram)
        self.assertEqual(ram, ssh_client.sf_get_ram_size_in_mb())
        self.assertEqual(cpu, ssh_client.get_number_of_vcpus())

    @test.attr(type='smoke')
    def test_server_2cpu_4mem(self):
        cpu = 2
        ram= 4096
        server = self.create_sf_server(
            cpu=cpu, ram=ram,
            qos_uplink=20480, qos_downlink=20480)
        LOG.debug("+++sf ,server = %s", server)

        self.assertTrue(server)
        fixed_ip = self._get_fixed_ip(server['id'])
        sfip_alloc = self._get_fip(fixed_ip)
        fip = sfip_alloc['external_ip']
        self.assertTrue(fip)
        self.check_public_network_connectivity(fip)
        ssh_client = self._ssh_to_server(fip, None)
        self.assertEqual(ram, ssh_client.sf_get_ram_size_in_mb())
        self.assertEqual(cpu, ssh_client.get_number_of_vcpus())

    @test.attr(type='smoke')
    def test_server_4cpu_8mem(self):
        cpu = 4
        ram = 8192

        server = self.create_sf_server(
            cpu=cpu, ram=ram,
            qos_uplink=20480, qos_downlink=20480)
        LOG.debug("+++sf ,server = %s", server)

        self.assertTrue(server)
        fixed_ip = self._get_fixed_ip(server['id'])
        sfip_alloc = self._get_fip(fixed_ip)
        fip = sfip_alloc['external_ip']
        self.assertTrue(fip)
        self.check_public_network_connectivity(fip)
        ssh_client = self._ssh_to_server(fip, None)
        self.assertEqual(ram, ssh_client.sf_get_ram_size_in_mb())
        self.assertEqual(cpu, ssh_client.get_number_of_vcpus())

        # cpu=8,ram=8192 ->cpu=1,ram=1024

        body = self.servers_client.stop(server['id'])
        self.assertEqual(202, body.response.status)
        waiters.wait_for_server_status(self.servers_client,
                                           server['id'], 'SHUTOFF')
        cpu = 1
        ram = 1024
        server = self.servers_client.update_server(server['id'],
                                                   cpu=cpu, ram=ram)
        self.assertEqual(200, server.response.status)

        body = self.servers_client.start(server['id'])
        self.assertEqual(202, body.response.status)
        waiters.wait_for_server_status(self.servers_client,
                                           server['id'], 'ACTIVE')
        ssh_client = self._ssh_to_server(fip, None)
        self.assertEqual(ram, ssh_client.sf_get_ram_size_in_mb())
        self.assertEqual(cpu, ssh_client.get_number_of_vcpus())

        # cpu=1,ram=1024 -> cpu=2,ram=2048

        body = self.servers_client.stop(server['id'])
        self.assertEqual(202, body.response.status)
        waiters.wait_for_server_status(self.servers_client,
                                           server['id'], 'SHUTOFF')

        cpu = 2
        ram = 2048
        server = self.servers_client.update_server(server['id'],
                                                   cpu=cpu, ram=ram)
        self.assertEqual(200, server.response.status)
        body = self.servers_client.start(server['id'])
        self.assertEqual(202, body.response.status)
        waiters.wait_for_server_status(self.servers_client,
                                           server['id'], 'ACTIVE')
        ssh_client = self._ssh_to_server(fip, None)
        self.assertEqual(ram, ssh_client.sf_get_ram_size_in_mb())
        self.assertEqual(cpu, ssh_client.get_number_of_vcpus())
