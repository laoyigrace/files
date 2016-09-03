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


import testtools

from tempest.api.telemetry import sf_base
from tempest.api.compute import base as compute_base
from tempest import config
from tempest import test

CONF = config.CONF


class TelemetrySampleTestJson(sf_base.SfBaseTelemetryTest,
                              compute_base.BaseV2ComputeTest):

    @test.idempotent_id('7c8c8430-9589-11e5-82e6-00e06665338b')
    @testtools.skipIf(not CONF.service_available.nova,
                      "Nova is not available.")
    def test_check_nova_samples(self):
        body = self.create_test_server()

        query = ('resource_id', 'eq', body['id'])

        for metric in self.vm_basic_meters:
            self.await_samples(metric, query)
