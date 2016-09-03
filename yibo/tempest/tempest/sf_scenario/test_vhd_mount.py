
import collections
import re
import six
import time

from oslo_log import log as logging
from tempest import config
from tempest import exceptions
from tempest import test
from tempest.common import waiters
from tempest.common.utils import data_utils
from tempest.common.utils.linux import sf_remote_client
from tempest.sf_scenario import sf_manager
from tempest.scenario import manager
from tempest.services.network import resources as net_resources
from tempest_lib import exceptions as lib_exc
from tempest_lib.common import ssh as ssh_client

CONF = config.CONF
LOG = logging.getLogger(__name__)

Floating_IP_tuple = collections.namedtuple('Floating_IP_tuple',
                                           ['floating_ip', 'server'])


class TestVhdMount(sf_manager.SfScenarioTest, manager.NetworkScenarioTest):

    credentials = ['primary', 'admin']

    @classmethod
    def skip_checks(cls):
        super(TestVhdMount, cls).skip_checks()
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
        super(TestVhdMount, cls).setup_credentials()

    def setUp(self):
        super(TestVhdMount, self).setUp()
        self.keypairs = {}
        self.servers = []

    @classmethod
    def resource_setup(cls):
        super(TestVhdMount, cls).resource_setup()
        cls.server_id = None
        cls.volumes = []
        cls.routers = []
        cls.fip_allocs = []
        cls.ext_net_id = CONF.network.public_network_id
        cls.net, cls.subnet = cls._create_net()
        cls.router = cls.create_router(data_utils.rand_name('router-'),
                                       admin_state_up=True,
                                       external_network_id=cls.ext_net_id)
        cls.sf_network_client.add_router_interface(
            router_id=cls.router['id'],
            subnet_id=cls.subnet['subnet']['id'])

    @classmethod
    def resource_cleanup(cls):
        # if we don't delete the server first, the port will still be part of
        # the subnet and we'll get a 409 from Neutron when trying to delete
        # the subnet.
        cls.cleanup_resources(cls.port_delete, cls.routers)
        super(TestVhdMount, cls).resource_cleanup()
        cls.cleanup_resources(cls._clean_up_volumes, cls.volumes)
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
                         block_device_mapping_v2=None, **kwargs):
        name = data_utils.rand_name('yjz-host')
        if block_device_mapping_v2 is None:
            block_device_mapping_v2 = [
                {
                    'boot_index': '0',
                    'uuid': u'%s' % CONF.compute.image_ref,
                    'source_type': 'image',
                    'device_name': 'vda',
                    'volume_size': u'%s' % sys_disk,
                    'destination_type': 'volume',
                    'volume_type': 'high-speed',
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
            'disk_config': 'AUTO'
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
        super(TestVhdMount, self).check_public_network_connectivity(
            fip, ssh_login, None, should_connect, msg,
            self.servers)

    @classmethod
    def _clean_up_volumes(self, volume_id):
        try:
            # print("YJZ: cleaning: %s", volume_id)
            self.volumes_client.detach_volume(volume_id)
            self.volumes_client.wait_for_volume_status(volume_id, 'available')
            self.volumes_client.delete_volume(volume_id)
        except Exception as ex:
            print("YJZ: Exception: %s", ex)
            pass

    def test_disk_post_attach(self):
        """ S6 disks are attached after both disks and servers are created """
        print("YJZ: BEGIN")

        print("YJZ: create server")
        server = self.create_sf_server(qos_uplink=20480, qos_downlink=20480)
        LOG.debug("+++sf ,server = %s", server)
        self.assertTrue(server)

        print("YJZ: get address")
        fixed_ip = self._get_fixed_ip(server['id'])
        sfip_alloc = self._get_fip(fixed_ip)
        fip = sfip_alloc['external_ip']
        LOG.debug("+++sf ,fip = %s", fip)
        self.assertTrue(fip)

        print("YJZ: IPPPPPPP = %s", fip)

        print("YJZ: ssh connect")
        ssh = ssh_client.Client(fip, "cirros", "cubswin:)")
        LOG.debug("+++sf ,ssh = %s", ssh)
        self.assertTrue(ssh)
        print("YJZ: ssh authrize")
        ssh.test_connection_auth()

        print("YJZ: check disk count == 1")
        result = ssh.exec_command('lsblk | grep -w disk | wc -l')
        LOG.debug("+++sf ,result = %s", result)
        self.assertEqual(result, "1\n")

        print("YJZ: stop host")
        self.servers_client.stop(server['id'])
        waiters.wait_for_server_status(self.servers_client, server['id'], 'SHUTOFF')

        self.server_id = server['id']
        self.mountpoint = ['b','c','d','e']
        print("YJZ: create and attach volumes")
        for i in range(4):
            kwargs = {'volume_type': 'low-speed'}
            new_volume = self.volumes_client.create_volume(10, **kwargs)
            self.volumes.append(new_volume['id'])
            print("volume[%s]: %s", i, new_volume['id'])
            self.volumes_client.wait_for_volume_status(new_volume['id'], 'available')
            self._check_backend_name(new_volume['id'], "low_speed")
            self.servers_client.attach_volume(server['id'],
                                              new_volume['id'],
                                              '/dev/vd%s' % self.mountpoint[i])
            self.volumes_client.wait_for_volume_status(new_volume['id'], 'in-use')

        print("YJZ: start host")
        self.servers_client.start(server['id'])
        waiters.wait_for_server_status(self.servers_client, server['id'], 'ACTIVE')

        print("YJZ: ssh authrize")
        ssh.test_connection_auth()
        print("YJZ: check disk count == 5")
        result = ssh.exec_command('lsblk | grep -w disk | wc -l')
        LOG.debug("+++sf ,result = %s", result)
        print("+++sf ,result = %s", result)
        self.assertEqual(result, "5\n")

        print("YJZ: check size in vm == 20G")
        result = ssh.exec_command('lsblk | grep -w disk | awk \'{print $4}\'')
        LOG.debug("+++sf ,result = %s", result)
        print("YJZ: result = %s", result)
        self.assertEqual(result, "1G\n10G\n10G\n10G\n10G\n")

        print("YJZ: PASS")
        return

    def test_disk_pre_alloc(self):
        """ S5 disks are created when server is creating """
        print("YJZ: BEGIN")
        block_device_mapping_v2 = [
            {
                'boot_index': '0',
                'uuid': '%s' % CONF.compute.image_ref,
                'source_type': 'image',
                'device_name': 'vda',
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': '1',
                'volume_size': 2,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': '2',
                'volume_size': 3,
                'destination_type': 'volume',
                'volume_type': 'low-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': '3',
                'volume_size': 4,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': '4',
                'volume_size': 5,
                'destination_type': 'volume',
                'volume_type': 'low-speed',
                'delete_on_termination': 1
            },
        ]

        print("YJZ: create server")
        server = self.create_sf_server(qos_uplink=20480, qos_downlink=20480, 
                                       block_device_mapping_v2=block_device_mapping_v2)
        LOG.debug("+++sf ,server = %s", server)
        self.assertTrue(server)

        print("YJZ: get address")
        fixed_ip = self._get_fixed_ip(server['id'])
        sfip_alloc = self._get_fip(fixed_ip)
        fip = sfip_alloc['external_ip']
        LOG.debug("+++sf ,fip = %s", fip)
        self.assertTrue(fip)

        print("YJZ: IPPPPPPP = %s", fip)

        print("YJZ: ssh connect")
        ssh = ssh_client.Client(fip, "cirros", "cubswin:)")
        LOG.debug("+++sf ,ssh = %s", ssh)
        self.assertTrue(ssh)
        print("YJZ: ssh authrize")
        ssh.test_connection_auth()

        print("YJZ: check disk count == 5")
        result = ssh.exec_command('lsblk | grep -w disk | wc -l')
        LOG.debug("+++sf ,result = %s", result)
        self.assertEqual(result, "5\n")

        print("YJZ: PASS")
        return

    def _find_volume_id_by_name(self, display_name):
        volume_list = self.volumes_client.list_volumes()
        for volume in volume_list:
            if display_name == volume.get('display_name'):
                return volume.get('id')
        return None

    def _check_backend_name(self, volume_id, substr):
        show = self.os_adm.volumes_client.show_volume(volume_id)
        self.assertIn('os-vol-host-attr:host', show)
        backend = show['os-vol-host-attr:host']
        print("YJZ: backend:", backend)
        result = backend.find(substr)
        self.assertTrue(result > -1)

    def _check_size(self, volume_id, capacity=10):
        show = self.os_adm.volumes_client.show_volume(volume_id)
        self.assertIn('size', show)
        self.assertEqual(show['size'], capacity)

    def _expand_volume(self, volume_id, capacity=20):
        self.volumes_client.extend_volume(volume_id, capacity)
        self.volumes_client.wait_for_volume_status(volume_id, 'available')
        return

    def test_disk_create_attach_extend(self):
        """ S3 S4 different types of disks are attached 
        after both disks and servers are created """
        """ S7 S8 extend it and check """
        print("YJZ: BEGIN")

        print("YJZ: create server")
        server = self.create_sf_server(qos_uplink=20480, qos_downlink=20480)
        LOG.debug("+++sf ,server = %s", server)
        self.assertTrue(server)

        print("YJZ: get address")
        fixed_ip = self._get_fixed_ip(server['id'])
        sfip_alloc = self._get_fip(fixed_ip)
        fip = sfip_alloc['external_ip']
        LOG.debug("+++sf ,fip = %s", fip)
        self.assertTrue(fip)

        print("YJZ: IPPPPPPP = %s", fip)

        print("YJZ: ssh connect")
        ssh = ssh_client.Client(fip, "cirros", "cubswin:)")
        LOG.debug("+++sf ,ssh = %s", ssh)
        self.assertTrue(ssh)
        print("YJZ: ssh authrize")
        ssh.test_connection_auth()

        print("YJZ: check disk count == 1")
        result = ssh.exec_command('lsblk | grep -w disk | wc -l')
        LOG.debug("+++sf ,result = %s", result)
        self.assertEqual(result, "1\n")

        print("YJZ: stop host")
        self.servers_client.stop(server['id'])
        waiters.wait_for_server_status(self.servers_client, server['id'], 'SHUTOFF')

        print("YJZ: create and attach volumes")
        high_volume_name = data_utils.rand_name("yjz-high")
        low_volume_name = data_utils.rand_name("yjz-low")
        print("YJZ: names: high: %s, low: %s." % (high_volume_name, low_volume_name))
        kwargs1 = {"volume_type": "high-speed", "size": 10, "display_name": high_volume_name}
        kwargs2 = {"volume_type": "low-speed", "size": 10, "display_name": low_volume_name}
        self.servers_client.create_attach_volume(server['id'], **kwargs1)
        self.servers_client.create_attach_volume(server['id'], **kwargs2)
        high_volume_id = self._find_volume_id_by_name(high_volume_name)
        low_volume_id = self._find_volume_id_by_name(low_volume_name)
        print("YJZ: ids: high: %s, low: %s." % (high_volume_id, low_volume_id))
        self.assertTrue(high_volume_id)
        self.assertTrue(low_volume_id)
        self.volumes.append(high_volume_id)
        self.volumes.append(low_volume_id)
        self.volumes_client.wait_for_volume_status(high_volume_id, 'in-use')
        self.volumes_client.wait_for_volume_status(low_volume_id, 'in-use')

        print("YJZ: check backend name")
        self._check_backend_name(high_volume_id, "high_speed")
        self._check_backend_name(low_volume_id, "low_speed")

        print("YJZ: check size == 10")
        self._check_size(high_volume_id, 10)
        self._check_size(low_volume_id, 10)

        print("YJZ: start host")
        self.servers_client.start(server['id'])
        waiters.wait_for_server_status(self.servers_client, server['id'], 'ACTIVE')

        print("YJZ: ssh authrize")
        ssh.test_connection_auth()
        print("YJZ: check disk count == 3")
        result = ssh.exec_command('lsblk | grep -w disk | wc -l')
        LOG.debug("+++sf ,result = %s", result)
        print("YJZ: result = %s", result)
        self.assertEqual(result, "3\n")

        print("YJZ: check size in vm == 10G")
        result = ssh.exec_command('lsblk | grep -w disk | awk \'{print $4}\'')
        LOG.debug("+++sf ,result = %s", result)
        print("YJZ: result = %s", result)
        self.assertEqual(result, "1G\n10G\n10G\n")

        print("YJZ: stop host")
        self.servers_client.stop(server['id'])
        waiters.wait_for_server_status(self.servers_client, server['id'], 'SHUTOFF')

        print("YJZ: detach volume")
        self.servers_client.detach_volume(server['id'], high_volume_id)
        self.servers_client.detach_volume(server['id'], low_volume_id)
        self.volumes_client.wait_for_volume_status(high_volume_id, 'available')
        self.volumes_client.wait_for_volume_status(low_volume_id, 'available')

        print("YJZ: expand volume")
        self._expand_volume(high_volume_id, 20)
        self._expand_volume(low_volume_id, 20)

        print("YJZ: attach volume")
        self.servers_client.attach_volume(server['id'], high_volume_id, '/dev/vdm')
        self.servers_client.attach_volume(server['id'], low_volume_id, '/dev/vdn')
        self.volumes_client.wait_for_volume_status(high_volume_id, 'in-use')
        self.volumes_client.wait_for_volume_status(low_volume_id, 'in-use')

        print("YJZ: start host")
        self.servers_client.start(server['id'])
        waiters.wait_for_server_status(self.servers_client, server['id'], 'ACTIVE')

        print("YJZ: ssh authrize")
        ssh.test_connection_auth()
        print("YJZ: check size in vm == 20G")
        result = ssh.exec_command('lsblk | grep -w disk | awk \'{print $4}\'')
        LOG.debug("+++sf ,result = %s", result)
        print("YJZ: result = %s", result)
        self.assertEqual(result, "1G\n20G\n20G\n")

        print("YJZ: PASS")
        return

    def test_disk_attach_detach(self):
        """ nova attach-detach """
        print("YJZ: BEGIN")

        print("YJZ: create server")
        server = self.create_sf_server(qos_uplink=20480, qos_downlink=20480)
        LOG.debug("+++sf ,server = %s", server)
        self.assertTrue(server)

        print("YJZ: get address")
        fixed_ip = self._get_fixed_ip(server['id'])
        sfip_alloc = self._get_fip(fixed_ip)
        fip = sfip_alloc['external_ip']
        LOG.debug("+++sf ,fip = %s", fip)
        self.assertTrue(fip)

        print("YJZ: IPPPPPPP = %s", fip)

        print("YJZ: ssh connect")
        ssh = ssh_client.Client(fip, "cirros", "cubswin:)")
        LOG.debug("+++sf ,ssh = %s", ssh)
        self.assertTrue(ssh)
        print("YJZ: ssh authrize")
        ssh.test_connection_auth()

        print("YJZ: check disk count == 1")
        result = ssh.exec_command('lsblk | grep -w disk | wc -l')
        LOG.debug("+++sf ,result = %s", result)
        self.assertEqual(result, "1\n")

        print("YJZ: stop host")
        self.servers_client.stop(server['id'])
        waiters.wait_for_server_status(self.servers_client, server['id'], 'SHUTOFF')

        print("YJZ: create and attach volumes")
        high_volume_name = data_utils.rand_name("yjz-high")
        low_volume_name = data_utils.rand_name("yjz-low")
        print("YJZ: names: high: %s, low: %s." % (high_volume_name, low_volume_name))
        kwargs1 = {"volume_type": "high-speed", "size": 10, "display_name": high_volume_name}
        kwargs2 = {"volume_type": "low-speed", "size": 10, "display_name": low_volume_name}
        self.servers_client.create_attach_volume(server['id'], **kwargs1)
        self.servers_client.create_attach_volume(server['id'], **kwargs2)
        high_volume_id = self._find_volume_id_by_name(high_volume_name)
        low_volume_id = self._find_volume_id_by_name(low_volume_name)
        print("YJZ: ids: high: %s, low: %s." % (high_volume_id, low_volume_id))
        self.assertTrue(high_volume_id)
        self.assertTrue(low_volume_id)
        self.volumes.append(high_volume_id)
        self.volumes.append(low_volume_id)
        self.volumes_client.wait_for_volume_status(high_volume_id, 'in-use')
        self.volumes_client.wait_for_volume_status(low_volume_id, 'in-use')

        print("YJZ: create another volume")
        another_volume = self.volumes_client.create_volume(5)
        self.assertIn('id', another_volume)
        self.volumes.append(another_volume['id'])
        self.volumes_client.wait_for_volume_status(another_volume['id'], 'available')

        print("YJZ: attach detach volumes")
        kwargs3 = {
            "attach_volumes": [
                {"volumeAttachment": {"volumeId": another_volume['id']}}
            ], 
            "detach_volumes": [
                {"volumeid": high_volume_id},
                {"volumeid": low_volume_id}
            ]
        }
        self.servers_client.attach_detach_volumes(server['id'], **kwargs3)
        self.volumes_client.wait_for_volume_status(high_volume_id, 'available')
        self.volumes_client.wait_for_volume_status(low_volume_id, 'available')
        self.volumes_client.wait_for_volume_status(another_volume['id'], 'in-use')

        print("YJZ: start host")
        waiters.wait_for_server_status(self.servers_client, server['id'], 'SHUTOFF')
        self.servers_client.start(server['id'])
        waiters.wait_for_server_status(self.servers_client, server['id'], 'ACTIVE')

        print("YJZ: ssh authrize")
        ssh.test_connection_auth()
        print("YJZ: check disk count == 2")
        result = ssh.exec_command('lsblk | grep -w disk | wc -l')
        LOG.debug("+++sf ,result = %s", result)
        print("YJZ: result = %s", result)
        self.assertEqual(result, "2\n")

        print("YJZ: PASS")
        return
