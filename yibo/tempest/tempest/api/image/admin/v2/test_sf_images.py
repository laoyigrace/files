# Copyright 2015 Red Hat, Inc.
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
from tempest_lib.common.utils import data_utils
import testtools

from tempest.api.image import base
from tempest import config
from tempest import test
from tempest_lib import exceptions as lib_exc

CONF = config.CONF


class SfBasicAdminOperationsImagesTest(base.BaseV2ImageAdminTest):
    """Here we test admin operations of images"""

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
    @test.idempotent_id('1e12d257-779e-491c-959e-df8509c7f3d8')
    def test_sf_update_image_visibility(self):

        # Create image by non-admin tenant
        image_name = data_utils.rand_name('sf-image')
        body = self._create_sf_image(image_name)
        image_id = body['id']
        visibility = 'public'

        # only admin can public image
        self.admin_client.update_image(image_id, [
            dict(replace='/visibility', value=visibility)])
        body = self.client.show_image(image_id)
        self.assertEqual("public", body['visibility'])

