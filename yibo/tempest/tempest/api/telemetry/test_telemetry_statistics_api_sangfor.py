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


from tempest.api.telemetry import sf_base
from tempest.api.compute import base as compute_base
from tempest import config
from tempest import test


CONF = config.CONF


class TelemetryStatsAPITestJSON(sf_base.SfBaseTelemetryTest,
                                compute_base.BaseV2ComputeTest):

    @classmethod
    def resource_setup(cls):
        super(TelemetryStatsAPITestJSON, cls).resource_setup()
        for i in range(2):
            body = cls.create_test_server(wait_until='ACTIVE')

    @test.attr(type='smoke')
    @test.idempotent_id('5e9dbd0f-95a0-11e5-b6dc-00e06665338b')
    def test_vms_stats_list(self):
        # list current stats of vms

        self.await_statistics()

    # def test_vm_start_end_timestamp(self):
    #     # specify time interval
    #     q = [{'field': 'type', 'op': 'eq', 'value': 'vm'},
    #          {'field': 'id', 'op': 'eq', 'value': self.server_ids[0]},
    #          {'field': 'date', 'op': 'ge', 'value': '20150811'},
    #          {'field': 'date', 'op': 'le', 'value': '20150812'}
    #          ]
    #     stats_instance = self.await_statistics(query=q)
    #     fetched_id = stats_instance[0]['id']
    #     self.assertEqual(self.server_ids[0], fetched_id,
    #                      "Failed to find the stats of specific instance")
    #
    # def test_vm_current_stats(self):
    #     # show specific vm stats
    #     q = [{'field': 'type', 'op': 'eq', 'value': 'vm'},
    #          {'field': 'id', 'op': 'eq', 'value': self.server_ids[0]}
    #          ]
    #     stats_instance = self.await_statistics(query=q)
    #     fetched_id = stats_instance[0]['id']
    #     self.assertEqual(self.server_ids[0], fetched_id,
    #                      "Failed to find the stats of specific instance")






