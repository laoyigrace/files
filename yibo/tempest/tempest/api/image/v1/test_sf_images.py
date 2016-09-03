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

from six import moves

from tempest.api.image import base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test

CONF = config.CONF


class SfCreateRegisterImagesTest(base.BaseV1ImageTest):
    """Here we test the registration and creation of images."""

    @test.attr(type='smoke')
    @test.idempotent_id('ef38b220-8ce4-40fb-ab76-55185707436e')
    def test_register_then_upload(self):
        # Register a qcow2 image, then upload an image

        image_name = data_utils.rand_name("image-v1")
        disk_format = 'qcow2'
        properties = {'os_type': 'windows', 'os_common': 'true'}
        body = self.create_image(name=image_name,
                                 container_format='bare',
                                 disk_format=disk_format,
                                 is_public=False,
                                 properties=properties)
        self.assertIn('id', body)
        image_id = body.get('id')
        self.assertEqual(image_name, body.get('name'))
        self.assertFalse(body.get('is_public'))
        self.assertEqual('queued', body.get('status'))
        for key, val in properties.items():
            self.assertEqual(val, body.get('properties')[key])

        # Now try uploading an image file
        image_file = moves.cStringIO(data_utils.random_bytes(1024))
        body = self.client.update_image(image_id, data=image_file)['image']

        self.assertIn('size', body)
        self.assertEqual(1024, body.get('size'))

