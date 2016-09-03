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

import six

from tempest_lib import exceptions as lib_exc
from tempest.api.compute import sf_base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test

CONF = config.CONF


class SfFipServersTestJSON(sf_base.SfBaseV2ComputeTest):
    """testcase for update server cpu and ram"""

    # @classmethod
    # def setup_credentials(cls):
    #     cls.prepare_instance_network()
    #     super(SfUpdateServersTestJSON, cls).setup_credentials()

    @classmethod
    def resource_setup(cls):
        super(SfFipServersTestJSON, cls).resource_setup()
        cls.routers = []
        cls.fip_allocs = []
        cls.ext_net_id = CONF.network.public_network_id
        cls.net, cls.subnet = cls._create_net()
        cls.router = cls.create_router(data_utils.rand_name('router-'),
                                       external_network_id=cls.ext_net_id)
        cls.sf_network_client.add_router_interface(
            router_id=cls.router['id'],
            subnet_id=cls.subnet['subnet']['id'])

    @classmethod
    def fip_alloc_delete(cls, fip_alloc_id):
        cls.sf_network_client.delete_floatingip_alloc(fip_alloc_id)

    @classmethod
    def port_delete(cls, router_id):
        body = cls.network_client.list_router_interfaces(router_id)
        print('+++sf, body = %s', body)
        interfaces = body['ports']
        for i in interfaces:
            try:
                cls.network_client.remove_router_interface_with_subnet_id(
                    router_id, i['fixed_ips'][0]['subnet_id'])
            except lib_exc.NotFound:
                pass

    @classmethod
    def router_delete(cls, router_id):
        cls.network_client.delete_router(router_id)

    @classmethod
    def resource_cleanup(cls):
        # if we don't delete the server first, the port will still be part of
        # the subnet and we'll get a 409 from Neutron when trying to delete
        # the subnet.

        cls.cleanup_resources(cls.port_delete, cls.routers)
        super(SfFipServersTestJSON, cls).resource_cleanup()
        cls.cleanup_resources(cls.fip_alloc_delete, cls.fip_allocs)
        cls.cleanup_resources(cls.router_delete, cls.routers)

    @classmethod
    def create_sf_server(cls, sys_disk=1, data_disk=1, cpu=1, ram=512,
                         **kwargs):
        networks = []
        network = {'uuid': cls.net['network']['id']}
        flavor = cls._create_flavor(sys_disk, ram, cpu)
        if kwargs.get('qos_uplink'):
            network['qos_uplink'] = kwargs.get('qos_uplink')
        if kwargs.get('qos_downlink'):
            network['qos_downlink'] = kwargs.get('qos_downlink')
        networks.append(network)

        cls.subnet_id = cls.subnet['subnet']['id']

        # create a server with specified flavor,data_disk and networks
        server = cls._create_sf_server(sys_disk, data_disk, flavor['id'],
                                       networks, **kwargs)
        return server

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

    @test.attr(type='smoke')
    @test.idempotent_id('11836a18-0b15-4327-a50b-f0d9dc66bddd')
    def test_create_server_with_fip(self):
        # If an admin password is provided on server creation, the server's
        # root password should be set to that password.
        qos_uplink=20480
        qos_downlink=20480

        print("+++sf, begin to create server")
        server = self.create_sf_server(qos_uplink=qos_uplink,
                                       qos_downlink=qos_downlink)

        print("+++sf, success server = %s", server)

        self.assertTrue(server)
        all_instances = server.get('all_instances')
        self.assertTrue(all_instances)
        self.assertTrue(len(all_instances) >= 1)
        fixed_ip = self._get_fixed_ip(all_instances[0]['uuid'])

        print("+++sf, fixed_ip = %s", fixed_ip)
        sfip_alloc = self._get_fip(fixed_ip)
        print("+++sf, sfip_alloc = %s", sfip_alloc)

        self.assertIsNotNone(sfip_alloc)
        self.assertEqual(sfip_alloc['qos_uplink'], qos_uplink)
        self.assertEqual(sfip_alloc['qos_downlink'], qos_downlink)

    @test.attr(type='smoke')
    @test.idempotent_id('11836a18-0b15-4327-a50b-f0d9dc66bddf')
    def test_create_server_with_fip2(self):
        # If an admin password is provided on server creation, the server's
        # root password should be set to that password.
        qos_uplink=102480
        qos_downlink=20480
        server = self.create_sf_server(qos_uplink=qos_uplink,
                                       qos_downlink=qos_downlink)

        self.assertTrue(server)
        all_instances = server.get('all_instances')
        self.assertTrue(all_instances)
        self.assertTrue(len(all_instances) >= 1)
        fixed_ip = self._get_fixed_ip(all_instances[0]['uuid'])
        sfip_alloc = self._get_fip(fixed_ip)

        self.assertIsNotNone(sfip_alloc)
        self.assertEqual(sfip_alloc['qos_uplink'], qos_uplink)
        self.assertEqual(sfip_alloc['qos_downlink'], qos_downlink)

    @test.attr(type='smoke')
    @test.idempotent_id('11836a18-0b15-4327-a50b-f0d9dc66bdde')
    def test_create_server_without_fip(self):
        # If an admin password is provided on server creation, the server's
        # root password should be set to that password.
        qos_uplink=0
        qos_downlink=0
        server = self.create_sf_server(qos_uplink=qos_uplink,
                                       qos_downlink=qos_downlink)

        self.assertTrue(server)
        all_instances = server.get('all_instances')
        self.assertTrue(all_instances)
        self.assertTrue(len(all_instances) >= 1)
        fixed_ip = self._get_fixed_ip(all_instances[0]['uuid'])
        sfip_alloc = self._get_fip(fixed_ip)

        self.assertIsNone(sfip_alloc)
