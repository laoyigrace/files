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
from tempest.common import waiters
from tempest import config
from tempest import test
from tempest_lib.common.utils import data_utils
import time


CONF = config.CONF


def _generate_name():
    return data_utils.rand_name("snapshot_name")


class SfSnapshotCreateTestJSON(sf_base.SfBaseV2ComputeTest):
    """testcase for sf-snapshot-create api """

    @classmethod
    def resource_setup(cls):
        super(SfSnapshotCreateTestJSON, cls).resource_setup()
        cls.server = cls.create_test_server(wait_until='ACTIVE')

    @test.attr(type='')
    @test.idempotent_id('5751f6d2-e732-487d-a263-43dd89a2b9d7')
    def test_create_snapshot_name(self):
        # create a snapshot with the positional arguments <snapshot_name>

        snapshot_name = _generate_name()
        create_resp, create_body = self._create_snapshot(self.server['id'],
                                                         name=snapshot_name)
        snapshot_id = create_body["snapshot"]["snapshot_id"]

        self.assertEqual("200", create_resp["status"])
        self.assertTrue(snapshot_id)
        self.assertEqual(snapshot_name,
                         create_body["snapshot"]["display_name"])

    @test.attr(type='')
    @test.idempotent_id('39ca8ed1-549e-4952-a76b-ac43d6892670')
    def test_create_snapshot_desc(self):
        # create a snapshot with the optional arguments <desc> parameter
        display_description = "sf snapshot display_description_%s" \
                              % data_utils.rand_name()
        create_resp, create_body = self._create_snapshot(
            self.server['id'], name=_generate_name(), desc=display_description)

        self.assertEqual(display_description,
                         create_body["snapshot"]["display_description"])

    @test.attr(type='')
    @test.idempotent_id('3e19dafe-0e2b-4b05-b74a-835c31c4a429')
    def test_create_multi_snapshot(self):
        # create two snapshot for one server
        snapshot_name_1 = _generate_name()
        self._create_snapshot(self.server['id'], name=snapshot_name_1)

        # create the second snapshot
        snapshot_name_2 = _generate_name()
        create_resp_2, create_body_2 = self._create_snapshot(
            self.server['id'], name=snapshot_name_2)

        self.assertEqual(snapshot_name_2,
                         create_body_2["snapshot"]["display_name"])

    @test.attr(type='')
    @test.idempotent_id('ba7e6561-e0c7-4309-95f3-9c92c5d51ef2')
    def test_create_snapshot_from_stoped_server(self):
        # A snapshot can be created when server is stoped
        server = self.create_test_server(wait_until='ACTIVE')
        self.stop_server(server['id'])
        snapshot_name = _generate_name()
        resp, body = self._create_snapshot(server['id'], name=snapshot_name)

        self.assertEqual(snapshot_name, body["snapshot"]["display_name"])


class SfSnapshotListTestJSON(sf_base.SfBaseV2ComputeTest):
    """testcase for sf-snapshot-list api"""

    @classmethod
    def resource_setup(cls):
        super(SfSnapshotListTestJSON, cls).resource_setup()
        cls.server = cls.create_test_server(wait_until='ACTIVE')

    @test.attr(type='')
    @test.idempotent_id('e2e7363d-5289-475a-9c67-5bd10aeb5e79')
    def test_snapshot_list(self):
        # list a snapshot from server
        resp_create, body_create = self._create_snapshot(self.server['id'],
                                                         name=_generate_name())

        snapshot_id = body_create["snapshot"]["snapshot_id"]
        list_resp, list_body, cnt = self._list_snapshot(self.server['id'])
        snapshot_id_from_list = list_body["snapshots"][cnt - 1]['snapshot_id']
        self.assertEqual('200', list_resp['status'])
        self.assertEqual(snapshot_id, snapshot_id_from_list)


class SfSnapshotUpdateTestJSON(sf_base.SfBaseV2ComputeTest):
    """testcase for sf-snapshot-update api"""

    @classmethod
    def resource_setup(cls):
        super(SfSnapshotUpdateTestJSON, cls).resource_setup()
        cls.server = cls.create_test_server(wait_until='ACTIVE')
        cls.resp_create, cls.body_create = cls._create_snapshot(
            cls.server['id'], name=_generate_name())

    @test.attr(type='')
    @test.idempotent_id('d4915923-3717-403b-a22a-e651b20bf22d')
    def test_update_snapshot_name(self):

        snapshot_id = self.body_create["snapshot"]["snapshot_id"]
        snapshot_name_new = _generate_name()

        resp = self._update_snapshot(snapshot_id,
                                     snapshot_name=snapshot_name_new)

        self.assertEqual("202", resp["status"])

        resp_list, body_list, cnt = self._list_snapshot(self.server['id'])

        self.assertEqual(
            snapshot_name_new,
            body_list["snapshots"][cnt - 1]["display_name"])

    @test.attr(type='')
    @test.idempotent_id('16522a5a-2731-4478-8604-0573235cffab')
    def test_update_snapshot_desc(self):

        snapshot_id = self.body_create["snapshot"]["snapshot_id"]
        snapshot_desc_new = "new snapshot description-%s" \
                            % data_utils.rand_name()

        self._update_snapshot(snapshot_id, desc=snapshot_desc_new)
        resp_list, body_list, cnt = self._list_snapshot(self.server['id'])

        self.assertEqual(
            snapshot_desc_new,
            body_list["snapshots"][cnt - 1]["display_description"])


class SfSnapshotDeleteTestJSON(sf_base.SfBaseV2ComputeTest):
    """testcase for sf-snapshot-delete api"""

    @test.attr(type='')
    @test.idempotent_id('8fb47f30-45d3-4064-b509-dbb250ff5db0')
    def test_delete_snapshot(self):
        # delete snapshot by snapshot id
        server = self.create_test_server(wait_until='ACTIVE')
        self._create_snapshot(server['id'], name=_generate_name())

        resp, list_body, cnt = self._list_snapshot(server['id'])
        snapshot_id = list_body['snapshots'][cnt - 1]['snapshot_id']
        resp_delete = self.sf_snapshot_client.delete_snapshot(snapshot_id)
        self.wait_for_snapshot_delete(server['id'])

        self.assertEqual("202", resp_delete["status"])


class SfSnapshotListChainTestJSON(sf_base.SfBaseV2ComputeTest):
    """testcase for sf-snapshot-chains api"""

    @test.attr(type='')
    @test.idempotent_id('4b3a53f3-9e6a-43e4-9b96-f3dfceec4f2d')
    def test_list_chain(self):
        # get all snapshot chains
        server = self.create_test_server(wait_until='ACTIVE')
        snapshot_name = _generate_name()
        self._create_snapshot(server['id'], name=snapshot_name)
        list_chain_body = self.sf_snapshot_client.list_chain()
        self.assertIn(snapshot_name, list_chain_body)


class SfSnapshotStopForceTestJSON(sf_base.SfBaseV2ComputeTest):
    """testcase for sf-force-stop api"""

    @test.attr(type='')
    @test.idempotent_id('2d408d46-59bd-446d-8fb4-3723d1498bc6')
    def test_force_stop_instance(self):
        # stop the server
        # as setupClass create 2 servers, when execute teardown to delete
        # server, if one server is also building, it will error
        server = self.create_test_server(wait_until='ACTIVE')
        resp_force_stop = self.sf_snapshot_client.force_stop(server['id'])
        waiters.wait_for_server_status(self.servers_client,
                                       server['id'], 'SHUTOFF')

        body_servers = self.servers_client.show_server(server['id'])
        self.assertEqual("202", resp_force_stop["status"])
        self.assertEqual(u'SHUTOFF', body_servers["status"])

