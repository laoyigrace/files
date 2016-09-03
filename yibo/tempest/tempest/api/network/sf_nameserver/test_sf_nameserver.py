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
from tempest import test


class SfNameserverTestJSON(sf_base.SfNameserverBaseNetworkTest):

    @test.attr(type='smoke')
    @test.idempotent_id('af4669c0-9cb1-11e5-a8da-00e0666534ba')
    def test_create_major_and_minor_nameservers(self):
        major_nameserver = self._create_nameserver(major=True,
                                                   address='1.8.8.8')
        self.addCleanup(self.sf_network_client.delete_nameserver,
                        major_nameserver['sfnameserver']['id'])
        self.assertTrue(major_nameserver['sfnameserver']['major'])
        self.assertEqual(major_nameserver['sfnameserver']['address'],
                         '1.8.8.8')
        minor_nameserver = self._create_nameserver(major=False,
                                                   address='1.8.8.7')
        self.addCleanup(self.sf_network_client.delete_nameserver,
                        minor_nameserver['sfnameserver']['id'])
        self.assertFalse(minor_nameserver['sfnameserver']['major'])
        self.assertEqual(minor_nameserver['sfnameserver']['address'],
                         '1.8.8.7')

    @test.attr(type='smoke')
    @test.idempotent_id('63180b1e-9cb2-11e5-9425-00e0666534ba')
    def test_update_nameserver(self):
        nameserver = self._create_nameserver(major=True, address='1.8.8.8')
        self.addCleanup(self.sf_network_client.delete_nameserver,
                        nameserver['sfnameserver']['id'])
        self.assertEqual(nameserver['sfnameserver']['address'], '1.8.8.8')
        update_nameserver = self.sf_network_client.update_nameserver(
            nameserver['sfnameserver']['id'], address='1.8.8.7')
        self.assertEqual(update_nameserver['sfnameserver']['address'],
                         '1.8.8.7')

    @test.idempotent_id('99d41400-9cb3-11e5-9268-00e0666534ba')
    def test_list_nameservers(self):
        nameserver = self._create_nameserver(major=True, address='1.8.8.8')
        self.addCleanup(self.sf_network_client.delete_nameserver,
                        nameserver['sfnameserver']['id'])
        self.assertTrue(nameserver['sfnameserver']['major'])
        self.assertEqual(nameserver['sfnameserver']['address'],
                         '1.8.8.8')
        list_body = self._list_nameservers()
        nameserver = [list['id'] for list in list_body['sfnameservers']
                      if list['id'] == nameserver['sfnameserver']['id']]
        self.assertNotEmpty(nameserver, "nameserver not found in the list")

    @test.idempotent_id('7e31d6f0-9cb4-11e5-99c1-00e0666534ba')
    def test_show_nameserver(self):
        nameserver = self._create_nameserver(major=True, address='1.8.8.8')
        self.addCleanup(self.sf_network_client.delete_nameserver,
                        nameserver['sfnameserver']['id'])
        self.assertTrue(nameserver['sfnameserver']['major'])
        self.assertEqual(nameserver['sfnameserver']['address'], '1.8.8.8')
        show = self._show_nameserver(nameserver['sfnameserver']['id'])
        self.assertEqual(show['sfnameserver']['major'], 1)
        self.assertEqual(show['sfnameserver']['address'], '1.8.8.8')

    @test.idempotent_id('a751aeb0-9cb5-11e5-bdc4-00e0666534ba')
    def test_create_dup_major_nameservers(self):
        major_nameserver1 = self._create_nameserver(major=True,
                                                    address='1.8.8.8')
        self.addCleanup(self.sf_network_client.delete_nameserver,
                        major_nameserver1['sfnameserver']['id'])
        self.assertTrue(major_nameserver1['sfnameserver']['major'])
        self.assertEqual(major_nameserver1['sfnameserver']['address'],
                         '1.8.8.8')
        major_nameserver2 = self._create_nameserver(major=True,
                                                    address='1.8.8.7')
        self.addCleanup(self.sf_network_client.delete_nameserver,
                        major_nameserver2['sfnameserver']['id'])
        self.assertTrue(major_nameserver2['sfnameserver']['major'])
        self.assertEqual(major_nameserver2['sfnameserver']['address'],
                         '1.8.8.7')

    @test.idempotent_id('0c03452e-9cb6-11e5-8c0b-00e0666534ba')
    def test_create_dup_minor_nameservers(self):
        minor_nameserver1 = self._create_nameserver(major=False,
                                                    address='1.8.8.8')
        self.addCleanup(self.sf_network_client.delete_nameserver,
                        minor_nameserver1['sfnameserver']['id'])
        self.assertFalse(minor_nameserver1['sfnameserver']['major'])
        self.assertEqual(minor_nameserver1['sfnameserver']['address'],
                         '1.8.8.8')
        minor_nameserver2 = self._create_nameserver(major=False,
                                                    address='1.8.8.7')
        self.addCleanup(self.sf_network_client.delete_nameserver,
                        minor_nameserver2['sfnameserver']['id'])
        self.assertFalse(minor_nameserver2['sfnameserver']['major'])
        self.assertEqual(minor_nameserver2['sfnameserver']['address'],
                         '1.8.8.7')
