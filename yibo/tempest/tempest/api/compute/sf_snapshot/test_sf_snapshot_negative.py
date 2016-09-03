# -*- coding:utf-8 -*-
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

from tempest.api.compute import sf_base
from tempest import config
from tempest import test
from tempest_lib.common.utils import data_utils
from tempest_lib import exceptions as lib_exc


CONF = config.CONF


def _generate_name():
    return data_utils.rand_name("snapshot_name")


class SfSnapshotNegativeTestJSON(sf_base.SfBaseV2ComputeTest):
    """the nagative testcases for sf-snapshot api"""

    @test.attr(type='negative')
    @test.idempotent_id('f19108c0-b2df-45fe-a3b6-5a1a454efa9d')
    def test_create_snapshot_from_deleted_server(self):
        # A snapshot should not be created if the server instance is deleted
        server = self.create_test_server(wait_until='ACTIVE')
        self.delete_server(server['id'])
        self.assertRaises(lib_exc.BadRequest,
                          self._create_snapshot,
                          server['id'])

    @test.attr(type='negative')
    @test.idempotent_id('09b798cf-c3b3-46f2-bcc7-96129f30a6a6')
    def test_create_snapshot_from_invalid_server(self):
        # A snapshot should not be created with invalid server id
        # this scenario could be happend in api or cli
        self.assertRaises(lib_exc.BadRequest,
                          self._create_snapshot,
                          '!@#$%^&*()')

    @test.attr(type='negative')
    @test.idempotent_id('60ef90f8-b4d6-4a26-98fe-f53cadf28fa2')
    def test_create_snapshot_from_non_server(self):
        # A snapshot should not be created when server id is none
        # this scenario could be happend in api or cli
        self.assertRaises(lib_exc.BadRequest,
                          self._create_snapshot,
                          server_id="", name=_generate_name())

    @test.attr(type='negative')
    @test.idempotent_id('35cb3357-41a5-46f4-85b0-2f3042a22c3d')
    def test_create_snapshot_without_snapshot_name(self):
        # A snapshot should not be created when snapshot name is none
        server = self.create_test_server(wait_until='ACTIVE')
        self.assertRaises(lib_exc.BadRequest,
                          self._create_snapshot,
                          server['id'], name="")

    @test.attr(type='negative')
    @test.idempotent_id('3d961a50-211a-40f2-949e-3bad97b3c8d4')
    def test_snapshot_list_with_invaild_server_id(self):
        # A snapshot should not be list with invalid server id
        # this scenario could be happend in api or cli
        self.assertRaises(lib_exc.NotFound, self._list_snapshot,
                          instance_id='!@#$%^&*()')

    @test.attr(type='negative')
    @test.idempotent_id('0d2c12a9-d6a6-4980-8e03-df562200973c')
    def test_snapshot_list_with_non_server(self):
        # A snapshot should not be list when server id is none
        # this scenario could be happend in api or cli
        self.assertRaises(lib_exc.BadRequest,
                          self._list_snapshot,
                          instance_id="")
