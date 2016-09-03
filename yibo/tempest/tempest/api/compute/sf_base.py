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

from tempest.api.compute import base
from tempest.common import waiters
from tempest.common.utils import data_utils
from oslo_log import log as logging
import time
from tempest import exceptions
from tempest import config
import json

LOG = logging.getLogger(__name__)
CONF = config.CONF


class SfBaseV2ComputeTest(base.BaseV2ComputeTest):
    """extend the base.BaseV2ComputeTest"""

    @classmethod
    def setup_clients(cls):
        super(SfBaseV2ComputeTest, cls).setup_clients()
        cls.sf_snapshot_client = cls.os.sf_snapshot_client
        cls.network_client = cls.os.network_client
        cls.sf_tenant_networks_client = cls.os.sf_tenant_networks_client
        cls.sf_network_client = cls.os.sf_network_client

    @classmethod
    def resource_setup(cls):
        super(SfBaseV2ComputeTest, cls).resource_setup()
        cls.ssh_password = CONF.compute.ssh_cirros_password
        cls.snapshot_id = []
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
        cls.cleanup_resources(cls.sf_snapshot_client.delete_snapshot,
                              cls.snapshot_id)

        super(SfBaseV2ComputeTest, cls).resource_cleanup()
        cls.cleanup_resources(cls.network_client.delete_subnet, cls.subnet_ids)
        cls.cleanup_resources(cls.network_client.delete_network, cls.net_ids)

    @classmethod
    def _create_sf_server(cls, sys_disk, data_disk, flavor_id, networks,
                          **kwargs):
        name = data_utils.rand_name('sf-server')
        disk_config = 'AUTO'
        image_id = CONF.compute.image_ref
        block_device_mapping_v2 = [
            {
                'boot_index': '0',
                'uuid': u'%s' % image_id,
                'source_type': 'image',
                'device_name': 'vda',
                'volume_size': u'%s' % sys_disk,
                'destination_type': 'volume',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': '1',
                'volume_size': '%s' % data_disk,
                'destination_type': 'volume'
            }]

        cls.server_initial = cls.create_test_server(
            validatable=True,
            wait_until='ACTIVE',
            name=name,
            block_device_mapping_v2=block_device_mapping_v2,
            flavor=flavor_id,
            disk_config=disk_config,
            networks=networks,
            **kwargs)
        for instance_id in cls.servers:
            cls.servers_id.append(instance_id['id'])
        return cls.server_initial

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
        cls.name_net = data_utils.rand_name('sf-network')
        net = cls.network_client.create_network(name=cls.name_net)
        cidr = '%s.%s.0.0/24' % (data_utils.rand_int_id(start=128, end=172),
                                   data_utils.rand_int_id(start=128, end=172))

        subnets = cls.network_client.list_subnets()
        subnets = subnets.get('subnets', [])
        find_flag = 0
        for i in xrange(100):
            for one in subnets:
                if one.get('cidr') == cidr:
                    cidr = '%s.%s.%s.0/24' % (
                        data_utils.rand_int_id(start=128, end=172),
                        data_utils.rand_int_id(start=128, end=172),
                        data_utils.rand_int_id(start=1, end=254))
                    find_flag = 1
                    break

            if not find_flag:
                break

        subnet = cls.network_client.create_subnet(
            network_id=net['network']['id'],
            cidr=cidr,
            ip_version=4)

        cls.net_ids.append(net['network']['id'])
        cls.subnet_ids.append(subnet['subnet']['id'])

        return net, subnet

    @classmethod
    def create_sf_server(cls, sys_disk=1, data_disk=1, cpu=1, ram=512,
                         **kwargs):
        flavor = cls._create_flavor(sys_disk, ram, cpu)
        net, subnet = cls._create_net()
        networks = [{'uuid': net['network']['id']}]

        cls.subnet_id = subnet['subnet']['id']

        # create a server with specified flavor,data_disk and networks
        server = cls._create_sf_server(sys_disk, data_disk, flavor['id'],
                                       networks, **kwargs)
        return server

    @classmethod
    def stop_server(cls, server_id):
        """Stop an existing server and waits for it to be stoped."""
        try:
            cls.servers_client.stop(server_id)
            waiters.wait_for_server_status(cls.servers_client,
                                           server_id, 'SHUTOFF')
        except Exception:
            LOG.exception('Failed to stop server %s' % server_id)

    @classmethod
    def sf_delete_server(cls, server_id):
        """Stop an existing server and waits for it to be deleted."""
        try:
            cls.servers_client.delete_server(server_id)
            cls.servers_client.wait_for_server_termination(server_id)
        except Exception:
            LOG.exception('Failed to delete server %s' % server_id)

    @classmethod
    def _create_snapshot(cls, server_id, **kwargs):
        resp, body = cls.sf_snapshot_client.create_snapshot(server_id,
                                                            **kwargs)
        cls.wait_for_snapshot_create(server_id)
        # set cls.snapshot_id for resource_cleanup
        cls.snapshot_id.append(body["snapshot"]["snapshot_id"])
        return resp, body

    @classmethod
    def _list_snapshot(cls, instance_id):
        resp, body = cls.sf_snapshot_client.list_snapshot(instance_id)
        # get the number of snapshots
        snapshot_cnt = len(body['snapshots'])
        return resp, body, snapshot_cnt

    @classmethod
    def _update_snapshot(cls, snapshot_id, **kwargs):
        resp = cls.sf_snapshot_client.update_snapshot(snapshot_id, **kwargs)
        return resp

    @classmethod
    def wait_for_snapshot_delete(cls, instance_id):
        # list_body_after_del is {u'snapshots': []}
        start_time = int(time.time())
        timeout = cls.build_timeout
        while True:
            time.sleep(cls.build_interval)
            resp, list_body_after_del, cnt = cls._list_snapshot(instance_id)
            if u'deleting' not in list_body_after_del["snapshots"]:
                return
            timed_out = int(time.time()) - start_time >= timeout
            if timed_out:
                message = "delete snapshot timeout"
                raise exceptions.TimeoutException(message)

    @classmethod
    def wait_for_snapshot_create(cls, instance_id):
        start_time = int(time.time())
        timeout = cls.build_timeout
        while True:
            time.sleep(cls.build_interval)
            resp, list_body_after_create, cnt = cls._list_snapshot(instance_id)
            if list_body_after_create["snapshots"][cnt - 1]["status"] \
                    != u'backuping':
                return
            timed_out = int(time.time()) - start_time >= timeout
            if timed_out:
                message = "create snapshot timeout"
                raise exceptions.TimeoutException(message)

    @classmethod
    def wait_for_snapshot_not_status(cls, instance_id, status):
        pass

    @classmethod
    def ssh_validation(cls):
        """
        Create the resources required to ssh to a VM
        """

        # create a new router
        router_name = data_utils.rand_name('router-')
        ext_gw_info = {'network_id': CONF.network.public_network_id}

        body = cls.network_client.create_router(
            router_name, external_gateway_info=ext_gw_info)

        router = body['router']

        # binding vm's subnet to router
        subnet_id = cls.subnet_id
        cls.network_client.add_router_interface_with_subnet_id(router['id'],
                                                               subnet_id)

        # create floating ip
        body = cls.sf_network_client.create_floatingip_alloc(
            CONF.network.public_network_id)
        floating_id = body['sf_fip_alloc']['id'][0]
        tenant_id = body['sf_fip_alloc']['tenant_id']
        cls.floating_ip = body['sf_fip_alloc']['external_ip']

        # The name of the method to associate a floating IP to as server is too
        # long for PEP8 compliance so:
        assoc = cls.sf_network_client.create_floatingip

        # binding floating ip
        # need params: router, vm'ip, floating_id, tenant_id
        spec_server = cls.servers_client.show_server(cls.server_initial['id'])
        intranet_ip = spec_server['addresses'][cls.name_net][0]['addr']
        assoc(router_id=router['id'], sffip_id=floating_id,
              tenant_id=tenant_id, intranet_ip=intranet_ip)
