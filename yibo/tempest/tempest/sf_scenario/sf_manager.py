# Copyright 2012 OpenStack Foundation
# Copyright 2016 sangfor Corp.
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

import six

from oslo_log import log
from tempest_lib import exceptions as lib_exc

from tempest.common import fixed_network
from tempest.common.utils import data_utils
from tempest.common import waiters
from tempest import config
from tempest.scenario import manager

CONF = config.CONF

LOG = log.getLogger(__name__)


class SfScenarioTest(manager.ScenarioTest):

    @classmethod
    def setup_clients(cls):
        super(SfScenarioTest, cls).setup_clients()
        cls.sf_network_client = cls.manager.sf_network_client

    def setUp(self):
        super(SfScenarioTest, self).setUp()

    @classmethod
    def resource_setup(cls):
        super(SfScenarioTest, cls).resource_setup()
        cls.net_ids = []
        cls.subnet_ids = []
        cls.servers_id = []

    @staticmethod
    def cleanup_resources(method, list_of_ids):
        for resource_id in list_of_ids:
            try:
                method(resource_id)
            except Exception:
                pass

    @classmethod
    def resource_cleanup(cls):
        # if we don't delete the server first, the port will still be part of
        # the subnet and we'll get a 409 from Neutron when trying to delete
        # the subnet.
        # cls.cleanup_resources(cls.sf_delete_server, cls.servers_id)

        super(SfScenarioTest, cls).resource_cleanup()
        cls.cleanup_resources(cls.network_client.delete_subnet, cls.subnet_ids)
        cls.cleanup_resources(cls.network_client.delete_network, cls.net_ids)

    def create_server(self, name=None, image=None, flavor=None,
                      wait_on_boot=True, wait_on_delete=True,
                      create_kwargs=None):
        """Creates VM instance.

        @param image: image from which to create the instance
        @param wait_on_boot: wait for status ACTIVE before continue
        @param wait_on_delete: force synchronous delete on cleanup
        @param create_kwargs: additional details for instance creation
        @return: server dict
        """
        if name is None:
            name = data_utils.rand_name(self.__class__.__name__)
        if image is None:
            image = CONF.compute.image_ref
        if flavor is None:
            flavor = CONF.compute.flavor_ref
        if create_kwargs is None:
            create_kwargs = {}

        network = self.get_tenant_network()
        create_kwargs = fixed_network.set_networks_kwarg(network,
                                                         create_kwargs)

        LOG.debug("Creating a server (name: %s, image: %s, flavor: %s)",
                  name, image, flavor)
        server = self.servers_client.create_server(name, image, flavor,
                                                   **create_kwargs)
        if wait_on_delete:
            self.addCleanup(self.servers_client.wait_for_server_termination,
                            server['id'])
        self.addCleanup_with_wait(
            waiter_callable=self.servers_client.wait_for_server_termination,
            thing_id=server['id'], thing_id_param='server_id',
            cleanup_callable=self.delete_wrapper,
            cleanup_args=[self.servers_client.delete_server, server['id']])
        if wait_on_boot:
            waiters.wait_for_server_status(self.servers_client,
                                           server_id=server['id'],
                                           status='ACTIVE')
        # The instance retrieved on creation is missing network
        # details, necessitating retrieval after it becomes active to
        # ensure correct details.
        server = self.servers_client.show_server(server['id'])
        self.assertEqual(server['name'], name)
        return server

    @classmethod
    def _create_flavor(cls, sys_disk, ram, cpu):
        # create a new flavor

        flavor_id = data_utils.rand_int_id(start=1000)
        flavor_name = data_utils.rand_name('sf_flavor')
        flavor = cls.flavors_client.create_flavor(flavor_name, ram, cpu,
                                                  sys_disk, flavor_id)
        return flavor

    @classmethod
    def _create_net(cls):
        # create a network and subnet
        name_net = data_utils.rand_name('sf-network')
        net = cls.network_client.create_network(name=name_net)

        subnet = cls.network_client.create_subnet(
            network_id=net['network']['id'],
            cidr='%s.%s.0.0/24' % (data_utils.rand_int_id(start=10, end=172),
                                   data_utils.rand_int_id(start=10, end=172)),
            ip_version=4)

        cls.subnet_ids.append(subnet['subnet']['id'])
        cls.net_ids.append(net['network']['id'])

        return net, subnet

class SfNetworkScenarioTest(SfScenarioTest, manager.NetworkScenarioTest):

    @classmethod
    def resource_setup(cls):
        super(SfNetworkScenarioTest, cls).resource_setup()
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
        super(SfNetworkScenarioTest, cls).resource_cleanup()
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