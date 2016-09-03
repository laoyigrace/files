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

from tempest.api.volume import base
from tempest.common.utils import data_utils
from tempest.common import waiters
from tempest import config
from tempest import test
import testtools

CONF = config.CONF


class VolumesV2AttachTest(base.BaseVolumeTest):
    @classmethod
    def setup_clients(cls):
        super(VolumesV2AttachTest, cls).setup_clients()
        cls.client = cls.volumes_client
        cls.image_client = cls.os.image_client

    @classmethod
    def resource_setup(cls):
        super(VolumesV2AttachTest, cls).resource_setup()

        # Create a test shared instance
        srv_name = data_utils.rand_name(cls.__name__ + '-Instance')
        cls.server = cls.create_server(srv_name)
        waiters.wait_for_server_status(cls.servers_client, cls.server['id'],
                                       'ACTIVE')

        # Create a test shared volume for attach/detach tests
        cls.volume = cls.create_volume()
        cls.client.wait_for_volume_status(cls.volume['id'], 'available')

    def _delete_image_with_wait(self, image_id):
        self.image_client.delete_image(image_id)
        self.image_client.wait_for_resource_deletion(image_id)

    @classmethod
    def resource_cleanup(cls):
        # Delete the test instance
        cls.servers_client.delete_server(cls.server['id'])
        cls.servers_client.wait_for_server_termination(cls.server['id'])

        super(VolumesV2AttachTest, cls).resource_cleanup()

    @test.idempotent_id('e63b0859-c81c-47de-8929-1169100eb0b7')
    @test.stresstest(class_setup_per='process')
    @test.attr(type='smoke')
    @test.services('compute')
    def test_get_volume_attachment(self):
        # Verify that a volume's attachment information is retrieved
        mountpoint = '/dev/vdc'
        self.client.attach_volume(self.volume['id'],
                                  self.server['id'],
                                  mountpoint)
        self.client.wait_for_volume_status(self.volume['id'], 'in-use')
        # NOTE(gfidente): added in reverse order because functions will be
        # called in reverse order to the order they are added (LIFO)
        self.addCleanup(self.client.wait_for_volume_status,
                        self.volume['id'],
                        'available')
        self.addCleanup(self.client.detach_volume, self.volume['id'])
        volume = self.client.show_volume(self.volume['id'])
        self.assertIn('attachments', volume)
        attachment = self.client.get_attachment_from_volume(volume)
        self.assertEqual(mountpoint, attachment['device'])
        self.assertEqual(self.server['id'], attachment['server_id'])
        self.assertEqual(self.volume['id'], attachment['id'])
        self.assertEqual(self.volume['id'], attachment['volume_id'])

    @test.idempotent_id('0257f24e-f8c7-43b2-bd60-bcda77ea11b4')
    @test.stresstest(class_setup_per='process')
    @test.attr(type='smoke')
    @test.services('compute')
    def test_get_volume_detachment(self):
        # Volume is attached and detached successfully from an instance
        mountpoint = '/dev/vdc'
        self.client.attach_volume(self.volume['id'],
                                  self.server['id'],
                                  mountpoint)
        self.client.wait_for_volume_status(self.volume['id'], 'in-use')
        self.client.detach_volume(self.volume['id'])
        self.client.wait_for_volume_status(self.volume['id'], 'available')

        volume = self.client.show_volume(self.volume['id'])
        self.assertIn('attachments', volume)
        self.assertEqual(0, len(volume['attachments']))


class VolumesV2MultiAttachTest(base.BaseVolumeTest):
    @classmethod
    def setup_clients(cls):
        super(VolumesV2MultiAttachTest, cls).setup_clients()
        cls.client = cls.volumes_client
        cls.image_client = cls.os.image_client

    @classmethod
    def resource_setup(cls):
        super(VolumesV2MultiAttachTest, cls).resource_setup()

        # Create a test shared instance
        srv_name = data_utils.rand_name(cls.__name__ + '-Instance')
        cls.server = cls.create_server(srv_name)
        waiters.wait_for_server_status(cls.servers_client, cls.server['id'],
                                       'ACTIVE')

        # Create four test shared volumes for attach tests
        cls.metadata = {'Type': 'work'}
        for i in range(3):
            cls.volume = cls.create_volume(metadata=cls.metadata)
            cls.client.wait_for_volume_status(cls.volume['id'], 'available')

    @classmethod
    def resource_cleanup(cls):
        # Delete the test instance
        cls.servers_client.delete_server(cls.server['id'])
        cls.servers_client.wait_for_server_termination(cls.server['id'])

        super(VolumesV2MultiAttachTest, cls).resource_cleanup()

    @test.idempotent_id('714394dc-767c-4853-b43a-52b21ad77e5f')
    @test.stresstest(class_setup_per='process')
    @test.services('compute')
    def test_get_volume_attachment(self):
        # Verify that a volume's attachment information is retrieved
        i = 0
        for volume in self.volumes:
            flag = ['a', 'b', 'c', 'd']
            mountpoint = '/dev/vd%s' % flag[i]
            i += 1
            self.client.attach_volume(volume['id'],
                                      self.server['id'],
                                      mountpoint)
            self.client.wait_for_volume_status(volume['id'], 'in-use')
        # NOTE(gfidente): added in reverse order because functions will be
        # called in reverse order to the order they are added (LIFO)
            self.addCleanup(self.client.wait_for_volume_status,
                            volume['id'],
                            'available')
            self.addCleanup(self.client.detach_volume, volume['id'])
            volume = self.client.show_volume(volume['id'])
            self.assertIn('attachments', volume)
            attachment = self.client.get_attachment_from_volume(volume)
            self.assertEqual(mountpoint, attachment['device'])
            self.assertEqual(self.server['id'], attachment['server_id'])
            self.assertEqual(volume['id'], attachment['id'])
            self.assertEqual(volume['id'], attachment['volume_id'])
