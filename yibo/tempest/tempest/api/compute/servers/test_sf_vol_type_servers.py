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

import itertools

from tempest.api.compute import sf_base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test

CONF = config.CONF


class SfVolTypeServersTestJSON(sf_base.SfBaseV2ComputeTest):
    """testcase for update server cpu and ram"""

    # @classmethod
    # def setup_credentials(cls):
    #     cls.prepare_instance_network()
    #     super(SfUpdateServersTestJSON, cls).setup_credentials()

    @classmethod
    def resource_setup(cls):
        super(SfVolTypeServersTestJSON, cls).resource_setup()
        cls.net, cls.subnet = cls._create_net()
        cls.image_id = CONF.compute.image_ref

    @classmethod
    def resource_cleanup(cls):
        # if we don't delete the server first, the port will still be part of
        # the subnet and we'll get a 409 from Neutron when trying to delete
        # the subnet.
        super(SfVolTypeServersTestJSON, cls).resource_cleanup()

    @classmethod
    def create_sf_server(cls, sys_disk=1, data_disk=1, cpu=1, ram=512,
                         block_device_mapping_v2=None, **kwargs):
        name = data_utils.rand_name('sf-server')
        disk_config = 'AUTO'
        networks = [{'uuid': cls.net['network']['id']}]
        flavor = cls._create_flavor(sys_disk, ram, cpu)
        if block_device_mapping_v2 is None:
            block_device_mapping_v2 = [
                {
                    'boot_index': '0',
                    'uuid': u'%s' % cls.image_id,
                    'source_type': 'image',
                    'device_name': 'vda',
                    'volume_size': u'%s' % sys_disk,
                    'destination_type': 'volume',
                    'volume_type': 'high-speed',
                    'delete_on_termination': 1
                },
                {
                    'source_type': 'blank',
                    'boot_index': '1',
                    'volume_size': '%s' % data_disk,
                    'destination_type': 'volume',
                    'volume_type': 'high-speed',
                    'delete_on_termination': 1
                },
                {
                    'source_type': 'blank',
                    'boot_index': '2',
                    'volume_size': '%s' % data_disk,
                    'destination_type': 'volume',
                    'volume_type': 'low-speed',
                    'delete_on_termination': 1
                },
            ]

        cls.server_initial = cls.create_test_server(
            validatable=True,
            wait_until='ACTIVE',
            name=name,
            block_device_mapping_v2=block_device_mapping_v2,
            flavor=flavor['id'],
            disk_config=disk_config,
            networks=networks,
            **kwargs)

        return cls.server_initial

    def _get_attach_volumes(self, instance_uuid):
        server = self.servers_client.show_server(instance_uuid)
        return server.get('os-extended-volumes:volumes_attached', [])

    def _compare_volumes(self, server, device_mapping):

        self.assertTrue(server)
        all_instances = server.get('all_instances')
        self.assertTrue(all_instances)
        self.assertTrue(len(all_instances) >= 1)
        instance_uuid = all_instances[0]['uuid']
        self.assertTrue(instance_uuid)
        attach_volumes = self._get_attach_volumes(instance_uuid)
        print("+++sf, attach_volumes = %s", attach_volumes)

        self.assertTrue(len(attach_volumes) == len(device_mapping))

        attach_volumes.sort(key=lambda x: x['device_name'])
        print("+++sf, attach_volumes = %s", attach_volumes)
        for (volume, mapping) in itertools.izip(attach_volumes,
                                                device_mapping):
            detail_volume = self.volumes_extensions_client.show_volume(volume[
                                                                       'id'])
            self.assertTrue(detail_volume)
            self.assertIn('attachments', detail_volume)
            attachments = detail_volume['attachments']
            self.assertTrue(len(attachments) == 1)
            self.assertIn('serverId', attachments[0])
            self.assertIn('device', attachments[0])
            self.assertIn('size', detail_volume)
            self.assertEqual(volume['device_name'], attachments[0]['device'])
            self.assertEqual(mapping['volume_size'],
                             int(detail_volume['size']))
            self.assertEqual(mapping['volume_type'],
                             detail_volume['volumeType'])

    @test.attr(type='smoke')
    def test_create_server_with_one_low_speed(self):
        # If an admin password is provided on server creation, the server's
        # root password should be set to that password.

        block_device_mapping_v2 = [
            {
                'boot_index': 0,
                'uuid': u'%s' % self.image_id,
                'source_type': 'image',
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 1,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'low-speed',
                'delete_on_termination': 1
            },
        ]

        print("+++sf, begin to create server")
        server = self.create_sf_server(
            block_device_mapping_v2=block_device_mapping_v2)

        print("+++sf, success server = %s", server)

        self._compare_volumes(server, block_device_mapping_v2)

    @test.attr(type='smoke')
    def test_create_server_with_one_high_speed(self):
        # If an admin password is provided on server creation, the server's
        # root password should be set to that password.

        block_device_mapping_v2 = [
            {
                'boot_index': 0,
                'uuid': u'%s' % self.image_id,
                'source_type': 'image',
                'volume_size': 2,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 1,
                'volume_size': 2,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
        ]

        print("+++sf, begin to create server")
        server = self.create_sf_server(
            block_device_mapping_v2=block_device_mapping_v2)

        print("+++sf, success server = %s", server)

        self._compare_volumes(server, block_device_mapping_v2)

    @test.attr(type='smoke')
    def test_create_server_with_four_low_speed(self):
        # If an admin password is provided on server creation, the server's
        # root password should be set to that password.

        block_device_mapping_v2 = [
            {
                'boot_index': 0,
                'uuid': u'%s' % self.image_id,
                'source_type': 'image',
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 1,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'low-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 2,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'low-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 3,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'low-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 4,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'low-speed',
                'delete_on_termination': 1
            },
        ]

        print("+++sf, begin to create server")
        server = self.create_sf_server(
            block_device_mapping_v2=block_device_mapping_v2)

        print("+++sf, success server = %s", server)

        self._compare_volumes(server, block_device_mapping_v2)

    @test.attr(type='smoke')
    def test_create_server_with_four_low_speed(self):
        # If an admin password is provided on server creation, the server's
        # root password should be set to that password.

        block_device_mapping_v2 = [
            {
                'boot_index': 0,
                'uuid': u'%s' % self.image_id,
                'source_type': 'image',
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 1,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'low-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 2,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'low-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 3,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'low-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 4,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'low-speed',
                'delete_on_termination': 1
            },
        ]

        print("+++sf, begin to create server")
        server = self.create_sf_server(
            block_device_mapping_v2=block_device_mapping_v2)

        print("+++sf, success server = %s", server)

        self._compare_volumes(server, block_device_mapping_v2)

    @test.attr(type='smoke')
    def test_create_server_with_four_high_speed(self):
        # If an admin password is provided on server creation, the server's
        # root password should be set to that password.

        block_device_mapping_v2 = [
            {
                'boot_index': 0,
                'uuid': u'%s' % self.image_id,
                'source_type': 'image',
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 1,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 2,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 3,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 4,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
        ]

        print("+++sf, begin to create server")
        server = self.create_sf_server(
            block_device_mapping_v2=block_device_mapping_v2)

        print("+++sf, success server = %s", server)

        self._compare_volumes(server, block_device_mapping_v2)

    @test.attr(type='smoke')
    def test_create_server_with_four_fix_speed(self):
        # If an admin password is provided on server creation, the server's
        # root password should be set to that password.

        block_device_mapping_v2 = [
            {
                'boot_index': 0,
                'uuid': u'%s' % self.image_id,
                'source_type': 'image',
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 1,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'low-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 2,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'low-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 3,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
            {
                'source_type': 'blank',
                'boot_index': 4,
                'volume_size': 1,
                'destination_type': 'volume',
                'volume_type': 'high-speed',
                'delete_on_termination': 1
            },
        ]

        print("+++sf, begin to create server")
        server = self.create_sf_server(
            block_device_mapping_v2=block_device_mapping_v2)

        print("+++sf, success server = %s", server)

        self._compare_volumes(server, block_device_mapping_v2)