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
import re
import six

from oslo_log import log as logging

from tempest.api.compute import base
from tempest.api.compute import sf_base
from tempest.common import compute
from tempest.common import waiters
from tempest.common.utils import data_utils
from tempest.common.utils.linux import remote_client
from tempest import config
from tempest.sf_scenario import sf_manager
from tempest import test
from tempest_lib import exceptions as lib_exc

CONF = config.CONF
LOG = logging.getLogger(__name__)

Floating_IP_tuple = collections.namedtuple('Floating_IP_tuple',
                                           ['floating_ip', 'server'])


class TestSfsnapshotOps(sf_manager.SfNetworkScenarioTest, sf_base.SfBaseV2ComputeTest,
                        base.BaseV2ComputeTest, test.BaseTestCase):

    """
    1.create a power-on sfsnapshot, and check success by ssh the instance
    2.create a power-off sfsnapshot, and check success by ssh the instance
    3.revert a power-on sfsnapshot, and check successful by mkdir
    4.revert a power-off sfsnapshot
    """

    @classmethod
    def skip_checks(cls):
        super(TestSfsnapshotOps, cls).skip_checks()
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
        super(TestSfsnapshotOps, cls).setup_credentials()

    @classmethod
    def resource_setup(cls):
        super(TestSfsnapshotOps, cls).resource_setup()

        cls.routers = []
        cls.fip_allocs = []
        cls.ext_net_id = CONF.network.public_network_id
        cls.net, cls.subnet = cls._create_net()
        cls.router = cls.create_router(data_utils.rand_name('router-'),
                                       admin_state_up=True,
                                       external_network_id=cls.ext_net_id)
        cls.nameserver = cls.sf_network_client.create_nameserver(major=True,
                            address='1.8.8.8')
        cls.sf_network_client.add_router_interface(
            router_id=cls.router['id'],
            subnet_id=cls.subnet['subnet']['id'])

        cls.set_validation_resources()
        cls.name = data_utils.rand_name('server')
        disk_config = 'AUTO'
        networks = []
        network = {'uuid': cls.net['network']['id']}
        networks.append(network)
        cls.server_initial = cls.create_test_server(
            validatable=True,
            wait_until='ACTIVE',
            name=cls.name,
            networks=networks,
            disk_config=disk_config)
        cls.password = cls.server_initial['adminPass']
        cls.server = cls.admin_manager.servers_client.show_server(
            cls.server_initial['id'])

    @classmethod
    def resource_cleanup(cls):
        # if we don't delete the server first, the port will still be part of
        # the subnet and we'll get a 409 from Neutron when trying to delete
        # the subnet.
        super(TestSfsnapshotOps, cls).resource_cleanup()
        cls.cleanup_resources(cls.port_delete, cls.routers)
        cls.cleanup_resources(cls.fip_alloc_delete, cls.fip_allocs)
        cls.cleanup_resources(cls.router_delete, cls.routers)

    def setUp(self):
        super(TestSfsnapshotOps, self).setUp()
        self.keypairs = {}
        self.servers = []

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
        super(TestSfsnapshotOps, self).check_public_network_connectivity(
            fip, ssh_login, None, should_connect, msg,
            self.servers)

    def test_sfsnapshot_boot(self):

        # boot snapshot
        snapshot_name = data_utils.rand_name("snapshot_name")
        create_resp, create_body = self._create_snapshot(self.server_initial['id'],
                                                         name=snapshot_name)
        self.assertEqual("200", create_resp["status"])
        self.wait_for_snapshot_create(self.server_initial['id'])

        snapshot_id = create_body['snapshot']['snapshot_id']


        LOG.debug("+++server_detail=%s", self.server)
        compute_node = self.server['OS-EXT-SRV-ATTR:host']
        LOG.debug("+++sf, compute_node=%s", compute_node)

        ssh_client = remote_client.RemoteClient(compute_node, username='root',
                                                  pkey=None,
                                                  password='1')
        cmd = "qemu-img info /var/lib/nova/instances/%s/disk | " \
              "grep %s" % (self.server['id'], snapshot_id)
        ret = ssh_client.exec_command(cmd)
        self.assertNotEmpty(ret)
        LOG.debug("+++sf, ret=%s", ret)

        # mkdir
        sfip_alloc = self.associate_floating_ip(self.server)
        fip = sfip_alloc['external_ip']
        self.assertTrue(fip)
        self.check_public_network_connectivity(fip)
        ssh_client = self._ssh_to_server(fip, None)

        cmd = "mkdir ./mynameissf"
        ret = ssh_client.exec_command(cmd)
        LOG.debug("+++sf, ret=%s", ret)

        # revert
        rollback = self.sf_snapshot_client.revert_snapshot(self.server_initial['id'],
                                                snapshot_id)
        LOG.debug("+++sf, rollback=%s", rollback)
        ssh_client = self._ssh_to_server(fip, None)
        cmd = "ls -a| grep 'mynameissf'"
        LOG.debug("+++sf, ret=%s", ret)
        self.assertRaises(lib_exc.SSHExecCommandFailed,
                          ssh_client.exec_command,
                          cmd)

    def test_sfsnapshot_shutdown(self):
        # mkdir
        sfip_alloc = self.associate_floating_ip(self.server)
        fip = sfip_alloc['external_ip']
        self.assertTrue(fip)
        self.check_public_network_connectivity(fip)
        ssh_client = self._ssh_to_server(fip, None)

        cmd = "mkdir ./mynameissf"
        ret = ssh_client.exec_command(cmd)
        LOG.debug("+++sf, ret=%s", ret)
        # shutdown snapshot
        body = self.servers_client.stop(self.server_initial['id'])
        self.assertEqual(202, body.response.status)
        waiters.wait_for_server_status(self.servers_client,
                                           self.server_initial['id'], 'SHUTOFF')

        snapshot_name = data_utils.rand_name("snapshot_name")
        create_resp, create_body = self._create_snapshot(self.server_initial['id'],
                                                         name=snapshot_name)
        self.assertEqual("200", create_resp["status"])
        snapshot_id = create_body['snapshot']['snapshot_id']

        LOG.debug("+++server_detail=%s", self.server)
        compute_node = self.server['OS-EXT-SRV-ATTR:host']
        LOG.debug("+++sf, compute_node=%s", compute_node)

        ssh_client = remote_client.RemoteClient(compute_node, username='root',
                                                  pkey=None,
                                                  password='1')
        cmd = "qemu-img info /var/lib/nova/instances/%s/disk | " \
              "grep %s" % (self.server['id'], snapshot_id)
        ret = ssh_client.exec_command(cmd)
        self.assertNotEmpty(ret)
        LOG.debug("+++sf, ret=%s", ret)

        # start computer and delete dir
        body = self.servers_client.start(self.server_initial['id'])
        self.assertEqual(202, body.response.status)
        waiters.wait_for_server_status(self.servers_client,
                                           self.server_initial['id'], 'ACTIVE')

        ssh_client = self._ssh_to_server(fip, None)
        cmd = "rm -rf ./mynameissf"
        ret = ssh_client.exec_command(cmd)
        LOG.debug("+++sf, ret=%s", ret)

        # revert
        self.sf_snapshot_client.revert_snapshot(self.server_initial['id'],
                                                snapshot_id)
        ssh_client = self._ssh_to_server(fip, None)
        cmd = "ls -a |grep 'mynameissf'"
        ret = ssh_client.exec_command(cmd)
        self.assertNotEmpty(ret)
        LOG.debug("+++sf, ret=%s", ret)
