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

from tempest.api.network import sf_base
from tempest_lib import exceptions as lib_exc
from tempest import test


class SfNameserverNegativeTestJSON(sf_base.SfNameserverBaseNetworkTest):

    @test.attr(type=['negative'])
    @test.idempotent_id('fcb2f0e1-9cb4-11e5-af0a-00e0666534ba')
    def test_create_nameserver_with_major_minor_same_address(self):
        major_nameserver = self._create_nameserver(major=True,
                                                   address='1.8.8.8')
        self.addCleanup(self.sf_network_client.delete_nameserver,
                        major_nameserver['sfnameserver']['id'])
        self.assertTrue(major_nameserver['sfnameserver']['major'])
        self.assertEqual(major_nameserver['sfnameserver']['address'],
                         '1.8.8.8')
        self.assertRaises(lib_exc.Conflict, self._create_nameserver,
                          major=False, address='1.8.8.8')

    @test.attr(type=['negative'])
    @test.idempotent_id('47281bde-9cb6-11e5-8f01-00e0666534ba')
    def test_create_nameserver_with_same_address(self):
        nameserver = self._create_nameserver(major=True, address='1.8.8.8')
        self.addCleanup(self.sf_network_client.delete_nameserver,
                        nameserver['sfnameserver']['id'])
        self.assertTrue(nameserver['sfnameserver']['major'])
        self.assertEqual(nameserver['sfnameserver']['address'], '1.8.8.8')
        self.assertRaises(lib_exc.Conflict, self._create_nameserver,
                          major=True, address='1.8.8.8')
        nameserver2 = self._create_nameserver(major=False, address='1.8.8.7')
        self.addCleanup(self.sf_network_client.delete_nameserver,
                        nameserver2['sfnameserver']['id'])
        self.assertFalse(nameserver2['sfnameserver']['major'])
        self.assertEqual(nameserver2['sfnameserver']['address'], '1.8.8.7')
        self.assertRaises(lib_exc.Conflict, self._create_nameserver,
                          major=False, address='1.8.8.7')
