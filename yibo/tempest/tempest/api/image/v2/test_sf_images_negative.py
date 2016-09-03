# Copyright 2013 OpenStack Foundation
# All Rights Reserved.
# Copyright 2013 IBM Corp.
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

import uuid

from tempest import sf_exceptions as sf_exc

from tempest.api.image import base
from tempest import test


class SfImagesNegativeTest(base.BaseV2ImageTest):

    """here we have -ve tests for show_image and delete_image api

    Tests
        ** get non-existent image
        ** get image with image_id=NULL
        ** get the deleted image
        ** delete non-existent image
        ** delete rimage with  image_id=NULL
        ** delete the deleted image
     """

    @classmethod
    def _raise(cls):
        raise sf_exc.SfTest

    @test.attr(type=['negative'])
    @test.idempotent_id('0d0d5c8e-65a3-45a1-ac22-1f16cbee561c')
    def test_sf_exc(self):

        self.assertRaises(sf_exc.SfTest, self._raise)
