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

from tempest.api.network import sf_base
from tempest import config
from tempest.common.utils import data_utils
from tempest import test
from tempest_lib import exceptions as lib_exc

CONF = config.CONF


class SfIpdomainNegativeTestJSON(sf_base.SfBaseNetworkTest):
    """the nagative testcases for sf-ipdomain api"""

    @test.attr(type='negative')
    @test.idempotent_id('5a344e0f-72e6-11e5-99dc-00e0666de3ce')
    def test_create_ipdomain_invalid_ipaddress(self):
        # A ipdomain should not be created if the ipaddress is invalid
        self.assertRaises(lib_exc.BadRequest,
                          self._create_ipdomain,
                          ip_address='2.2.2.256', domain='www.test.com')

    @test.attr(type=['negative'])
    @test.idempotent_id('268d8000-72db-11e5-85f8-00e0666de3ce')
    def test_show_non_existent_ipdomain(self):
        non_exist_id = data_utils.rand_uuid()
        self.assertRaises(lib_exc.NotFound,
                          self.sf_network_client.show_ipdomain,
                          non_exist_id)

    @test.attr(type=['negative'])
    @test.idempotent_id('364923d1-72dd-11e5-8e94-00e0666de3ce')
    def test_delete_non_existent_ipdomain(self):
        non_exist_id = data_utils.rand_uuid()
        self.assertRaises(lib_exc.NotFound,
                          self.sf_network_client.delete_ipdomain,
                          non_exist_id)

    @test.attr(type=['negative'])
    @test.idempotent_id('67d54ea1-733d-11e5-98f1-00e0666de3ce')
    def test_list_without_ipdomain(self):
        # Without ipdomain,list ipdomain
        # Without ipdomain, list_body is {u'ipdomains': []}
        list_body, cnt = self._list_ipdomain()
        self.assertFalse(list_body["ipdomains"])

    @test.attr(type=['negative'])
    @test.idempotent_id('1e41f930-8113-11e5-b2e2-00e0666534ba')
    def test_create_conflict_ipdomain(self):
        # A ipdomain should not be created if it already exist
        ip_address = '1.1.1.1'
        domain = 'sftest.com'
        create_body = self._create_ipdomain(ip_address=ip_address,
                                            domain=domain)
        self.assertNotEmpty(create_body["ipdomain"]["id"],
                            "Created ipdomain not found in the list")
        self.addCleanup(self.sf_network_client.delete_ipdomain,
                        create_body["ipdomain"]["id"])
        self.assertRaises(lib_exc.Conflict,
                          self._create_ipdomain,
                          ip_address=ip_address, domain=domain)

    @test.attr(type=['negative'])
    @test.idempotent_id('2a1cc4b0-7240-11e5-b8ae-00e0666de3ce')
    def test_create_dup_domain_ipdomain(self):
        # Create tenant's ipdomain
        # With the duplicate domain,different ip_address
        domain_name = "test.com"
        inter_ip1 = "6.6.6.6"
        inter_ip2 = "172.21.0.0"
        create_body1 = self._create_ipdomain(ip_address=inter_ip1,
                                             domain=domain_name)
        ipdomain_id1 = create_body1["ipdomain"]["id"]
        self.addCleanup(self.sf_network_client.delete_ipdomain, ipdomain_id1)
        self.assertNotEmpty(ipdomain_id1,
                            "Created ipdomain not found in the list")
        self.assertRaises(lib_exc.Conflict,
                          self._create_ipdomain,
                          ip_address=inter_ip2, domain=domain_name)

    @test.attr(type=['negative'])
    @test.idempotent_id('14ca23b0-8450-11e5-9cb6-00e0666534ba')
    def test_create_101_ipdomains(self):
        # Create tenant's ipdomain
        # With the positional arguments <ip_address> <domain>
        name = "test.com"
        inter_ip = "6.6.6.6"
        for i in range(0, 100):
            domain_name = str(i) + name
            create_body = self._create_ipdomain(ip_address=inter_ip,
                                                domain=domain_name)
            ipdomain_id = create_body["ipdomain"]["id"]
            self.addCleanup(self.sf_network_client.delete_ipdomain,
                            ipdomain_id)
        list, num = self._list_ipdomain()
        self.assertEqual(num, 100)
        self.assertRaises(lib_exc.Conflict, self._create_ipdomain,
                          ip_address=inter_ip, domain=name)
