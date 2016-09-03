# Copyright 2013 OpenStack Foundation
# Copyright 2013 IBM Corp
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

import random

from six import moves

from oslo_log import log as logging
from tempest.api.image import base
from tempest.common.utils import data_utils
from tempest.common.utils.linux import sf_remote_client
from tempest import config
from tempest import test

CONF = config.CONF
LOG = logging.getLogger(__name__)


class SfBasicOperationsImagesTest(base.BaseV2ImageTest):
    """Here we test the basic operations of images"""

    @classmethod
    def _exec_command(cls, cmd):
        linux_client = sf_remote_client.SfRemoteClient(
            server=CONF.sf_common_info.ctl_host,
            username=CONF.sf_common_info.ctl_ssh_username,
            password=CONF.sf_common_info.ctl_ssh_password)
        return linux_client.exec_command(cmd)

    @classmethod
    def _check_image_suffix_is_qcow2(cls, image_id):
        cmd = 'ls /var/lib/glance/images/ | grep %s.qcow2' % image_id
        output_data = cls._exec_command(cmd)
        if output_data:
            return True
        return False

    @classmethod
    def _check_image_file_not_exist(cls, image_id):
        image_file = '/var/lib/glance/images/%s.qcow2' % image_id
        cmd = 'if [ ! -f %s ]; then echo "ok"; fi' % image_file
        output_data = cls._exec_command(cmd)
        if output_data == 'ok\n':
            return True
        return False

    @classmethod
    def _create_sf_image(cls, image_name, os_type='windows',
                         os_common='true', os_image_size='1073741824',
                         container_format='bare', disk_format='qcow2',
                         visibility='private'):
        # Regiser a image
        body = cls.create_image(name=image_name,
                                container_format=container_format,
                                disk_format=disk_format,
                                visibility=visibility,
                                os_type=os_type,
                                os_common=os_common,
                                os_image_size=os_image_size)
        image_id = body.get('id')

        # Now try uploading an image file
        cls.file_content = data_utils.random_bytes()
        image_file = moves.cStringIO(cls.file_content)
        cls.client.store_image_file(image_id, image_file)

        return body

    @test.attr(type='smoke')
    @test.idempotent_id('42c45fd4-78d2-4c31-96fc-723031d976af')
    def test_sf_create_image(self):
        """
        sangfor create image include two steps: Register image, and upload the
        image file.
        """
        image_name = data_utils.rand_name('image')
        os_type = 'windows'
        os_common = 'true'
        os_image_size = '1073741824'
        container_format = CONF.image.container_formats[3]
        disk_format = CONF.image.disk_formats[6]
        body = self._create_sf_image(image_name, os_type=os_type,
                                     os_common=os_common,
                                     os_image_size=os_image_size,
                                     disk_format=disk_format,
                                     container_format=container_format)
        self.assertIn('id', body)
        image_id = body.get('id')
        self.assertIn('name', body)
        self.assertEqual(image_name, body['name'])
        self.assertIn('status', body)
        self.assertEqual('queued', body['status'])

        # Now try to get image details
        body = self.client.show_image(image_id)
        self.assertEqual(image_id, body['id'])
        self.assertEqual(image_name, body['name'])
        self.assertIn('size', body)
        self.assertEqual(1024, body.get('size'))
        self.assertIn('os_type', body)
        self.assertEqual(os_type, body['os_type'])
        self.assertIn('os_common', body)
        self.assertEqual(os_common, body['os_common'])
        self.assertIn('os_image_size', body)
        self.assertEqual(os_image_size, body['os_image_size'])
        self.assertIn('disk_format', body)
        self.assertEqual('qcow2', body['disk_format'])

        # Now try get image file, and Verifying the image's file data
        body = self.client.show_image_file(image_id)
        self.assertEqual(self.file_content, body.data)

        # Checking image's suffix is qcow2
        self.assertEquals(True, self._check_image_suffix_is_qcow2(image_id))

    @test.attr(type='smoke')
    @test.idempotent_id('25c67e17-9d33-4716-8b51-7f77c4eb9e0f')
    def test_sf_delete_image(self):
        # Deletes an image by image_id

        # Create image
        image_name = data_utils.rand_name('image')
        body = self._create_sf_image(image_name)
        image_id = body['id']

        # Delete Image
        self.client.delete_image(image_id)
        self.client.wait_for_resource_deletion(image_id)

        # Verifying deletion
        images = self.client.list_images()['images']
        images_id = [item['id'] for item in images]
        self.assertNotIn(image_id, images_id)

        # Checking image's file dosen't exist
        self.assertEqual(True, self._check_image_file_not_exist(image_id))

    @test.attr(type='smoke')
    @test.idempotent_id('709a4a2c-3cb7-4103-8115-f126d9f38e8b')
    def test_update_image_name(self):
        # Updates an image by image_id

        # Create image
        image_name = data_utils.rand_name('image')
        body = self._create_sf_image(image_name)
        image_id = body['id']

        # Update Image
        new_image_name = data_utils.rand_name('new-image')
        body = self.client.update_image(image_id, [
            dict(replace='/name', value=new_image_name)])

        # Verifying updating
        body = self.client.show_image(image_id)
        self.assertEqual(image_id, body['id'])
        self.assertEqual(new_image_name, body['name'])

    @test.attr(type='smoke')
    @test.idempotent_id('eb82ff3d-d589-4e7c-bcce-26a3b51b63db')
    def test_update_image_attribute(self):
        # Updates an image by image_id

        # Create image
        image_name = data_utils.rand_name('image')
        body = self._create_sf_image(image_name)
        image_id = body['id']

        # Update image attribute
        os_type = 'linux'
        os_common = 'false'
        os_image_size = '1024'

        body = self.client.update_image(image_id, [
            dict(replace='/os_type', value=os_type),
            dict(replace='/os_common', value=os_common),
            dict(replace='/os_image_size', value=os_image_size)
        ])

        # Verifying updating
        body = self.client.show_image(image_id)
        self.assertEqual(image_id, body['id'])
        self.assertEqual(os_type, body['os_type'])
        self.assertEqual(os_common, body['os_common'])
        self.assertEqual(os_image_size, body['os_image_size'])


class SfListImagesTest(base.BaseV2ImageTest):
    """Here we test the listing of image information"""

    @classmethod
    def _create_sf_image(cls, image_name, os_type='windows',
                         os_common='true', os_image_size='1073741824',
                         container_format='bare', disk_format='qcow2',
                         visibility='private'):
        # Regiser a image
        body = cls.create_image(name=image_name,
                                container_format=container_format,
                                disk_format=disk_format,
                                visibility=visibility,
                                os_type=os_type,
                                os_common=os_common,
                                os_image_size=os_image_size)
        image_id = body.get('id')

        # Now try uploading an image file
        cls.file_content = data_utils.random_bytes()
        image_file = moves.cStringIO(cls.file_content)
        cls.client.store_image_file(image_id, image_file)

        return body

    @test.attr(type='smoke')
    @test.idempotent_id('ad346674-b0bc-46f3-a569-5e09f5d7b653')
    def test_sf_list_images(self):
        # Test to get all images

        for image in range(2):
            image_name = data_utils.rand_name('image')
            self._create_sf_image(image_name)

        images_list = self.client.list_images()['images']
        image_list = map(lambda x: x['id'], images_list)
        for image in self.created_images:
            self.assertIn(image, image_list)

    @test.attr(type='smoke')
    @test.idempotent_id('aeb32db5-9c06-4629-a18c-b54dd8a33e13')
    def test_sf_get_image_detail(self):
        # Test to get image detail

        # Create image
        image_name = data_utils.rand_name('image')
        body = self._create_sf_image(image_name)
        image_id = body['id']
        image_detail = self.client.show_image(image_id)
        self.assertEqual(image_name, image_detail['name'])
        self.assertEqual(image_id, image_detail['id'])

