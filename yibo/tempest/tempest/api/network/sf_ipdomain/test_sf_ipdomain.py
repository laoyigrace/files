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
from tempest import config
from tempest import test

CONF = config.CONF


class SfIpdomainsTestJSON(sf_base.SfBaseNetworkTest):
    """
    Tests the following operations in the Neutron API using the REST client for
    Neutron:

        create a ipdomain for a tenant
        list tenant's ipdomains
        show a tenant ipdomain details
        ipdomain update
        delete tenant's ipdomain

        All ipdomain tests are run with ipv4.
    """
    # Delete ipdomains package method
    def _bulk_delete_ipdomain(self, ipdomain_id):
        self.sf_network_client.delete_ipdomain(ipdomain_id)
        # Asserting that the ipdomain is not found in the list
        # after deletion
        list_body = self.sf_network_client.list_ipdomains()
        ipdomain_list = list()
        for ipdomain in list_body['ipdomains']:
            ipdomain_list.append(ipdomain['id'])
        self.assertNotIn(ipdomain_id, ipdomain_list)

    @test.attr(type='smoke')
    @test.idempotent_id('191f561e-714e-11e5-a41d-00e0666de3ce')
    def test_create_ipdomain(self):
        # Create tenant's ipdomain
        # With the positional arguments <ip_address> <domain>
        domain_name = "test.com"
        inter_ip = "6.6.6.6"
        create_body = self._create_ipdomain(ip_address=inter_ip,
                                            domain=domain_name)
        ipdomain_id = create_body["ipdomain"]["id"]
        self.addCleanup(self.sf_network_client.delete_ipdomain, ipdomain_id)

        self.assertTrue(ipdomain_id)
        self.assertEqual(domain_name,
                         create_body["ipdomain"]["domain"])
        self.assertEqual(inter_ip,
                         create_body["ipdomain"]["ip_address"])

    @test.idempotent_id('138b4de1-7243-11e5-b480-00e0666de3ce')
    def test_create_dup_ipaddress_ipdomain(self):
        # Create tenant's ipdomain
        # With the duplicate ip_address,different domain
        domain_name1 = "sftest.com"
        domain_name2 = "sftest1.com"
        inter_ip = "10.1.1.1"
        create_body1 = self._create_ipdomain(ip_address=inter_ip,
                                             domain=domain_name1)
        ipdomain_id1 = create_body1["ipdomain"]["id"]
        self.addCleanup(self.sf_network_client.delete_ipdomain, ipdomain_id1)
        create_body2 = self._create_ipdomain(ip_address=inter_ip,
                                             domain=domain_name2)
        ipdomain_id2 = create_body2["ipdomain"]["id"]
        self.addCleanup(self.sf_network_client.delete_ipdomain, ipdomain_id2)

        self.assertEqual(inter_ip, create_body1["ipdomain"]["ip_address"])
        self.assertEqual(inter_ip, create_body2["ipdomain"]["ip_address"])
        self.assertNotEmpty(ipdomain_id1,
                            "Created ipdomain not found in the list")
        self.assertNotEmpty(ipdomain_id2,
                            "Created ipdomain not found in the list")

    @test.idempotent_id('e9a65aee-724d-11e5-af11-00e0666de3ce')
    def test_create_multi_ipdomain(self):
        # Create two ipdomain for one route
        ip_address1 = '192.168.1.1'
        domain2 = 'sftest2.com'
        create_body1 = self._create_ipdomain(ip_address=ip_address1,
                                             domain='sftest1.com')
        ipdomain_id1 = create_body1["ipdomain"]["id"]
        self.addCleanup(self.sf_network_client.delete_ipdomain, ipdomain_id1)
        self.assertEqual(ip_address1, create_body1["ipdomain"]["ip_address"])
        # Create the second ipdomain
        create_body2 = self._create_ipdomain(ip_address='192.168.2.2',
                                             domain=domain2)
        ipdomain_id2 = create_body2["ipdomain"]["id"]
        self.addCleanup(self.sf_network_client.delete_ipdomain, ipdomain_id2)
        self.assertEqual(domain2, create_body2["ipdomain"]["domain"])

    @test.idempotent_id('7b93f0c0-7155-11e5-9094-00e0666de3ce')
    def test_list_ipdomain(self):
        # List tenant's ipdomains
        create_body = self._create_ipdomain(ip_address="4.4.4.4",
                                            domain="test.com")
        self.addCleanup(self.sf_network_client.delete_ipdomain,
                        create_body["ipdomain"]["id"])

        ipdomain_id = create_body["ipdomain"]["id"]
        list_body, num = self._list_ipdomain()
        ipdomain_from_list = list_body["ipdomains"][num - 1]['id']
        self.assertEqual(ipdomain_id, ipdomain_from_list)
        # Verify the ipdomain exists in the list of all ipdomains
        if create_body["ipdomain"]["id"] == \
                list_body["ipdomains"][num - 1]['id']:
            self.assertNotEmpty(ipdomain_id,
                                "Created ipdomain not found in the list")

    @test.idempotent_id('ede7f28f-7158-11e5-8b2b-00e0666de3ce')
    def test_show_ipdomain(self):
        # Verify the details of a ipdomain
        create_body = self._create_ipdomain(ip_address="4.4.4.5",
                                            domain="test12.com")
        self.addCleanup(self.sf_network_client.delete_ipdomain,
                        create_body["ipdomain"]["id"])

        ipdomain_id = create_body["ipdomain"]["id"]
        body = self._show_ipdomain(ipdomain_id)
        ipdomain = body['ipdomain']
        for key in ['id', 'ip_address', 'domain', 'tenant_id']:
            self.assertEqual(ipdomain[key], create_body["ipdomain"][key])

    @test.attr(type='smoke')
    @test.idempotent_id('01e927ee-73cf-11e5-9a77-00e0666de3ce')
    def test_update_ipdomain_ip_and_domain(self):
        # Due to bug29569, ipdomain_update's api isn's available
        # Update ipaddress and doamin
        create_body = self._create_ipdomain(ip_address="172.1.1.1",
                                            domain="sf.com")
        self.addCleanup(self.sf_network_client.delete_ipdomain,
                        create_body["ipdomain"]["id"])
        ipdomain_id = create_body['ipdomain']['id']
        show_body = self._show_ipdomain(ipdomain_id)
        self.assertEqual('172.1.1.1', show_body['ipdomain']['ip_address'])
        self.assertEqual('sf.com', show_body['ipdomain']['domain'])
        # Update the ipaddress and domain
        new_ip = '162.2.2.2'
        new_domain = 'www.sf.com'
        self.sf_network_client.update_ipdomain(ipdomain_id, ip_address=new_ip,
                                               domain=new_domain)
        # Get the ipdomain
        fetched_ipdomain = self._show_ipdomain(ipdomain_id)
        self.assertEqual(new_ip, fetched_ipdomain['ipdomain']['ip_address'])
        self.assertEqual(new_domain, fetched_ipdomain['ipdomain']['domain'])

    @test.idempotent_id('9c1100e1-73d0-11e5-adeb-00e0666de3ce')
    def test_update_ipdomain_ipaddress(self):
        # Update ipaddress
        # Create a ipdomain
        create_body = self._create_ipdomain(ip_address="10.1.1.0",
                                            domain="www.sf.com")
        self.addCleanup(self.sf_network_client.delete_ipdomain,
                        create_body["ipdomain"]["id"])
        ipdomain_id = create_body['ipdomain']['id']
        show_body = self._show_ipdomain(ipdomain_id)
        self.assertEqual('10.1.1.0', show_body['ipdomain']['ip_address'])
        self.assertEqual('www.sf.com', show_body['ipdomain']['domain'])
        # Update the ipaddress
        new_ip = '10.2.2.0'
        self.sf_network_client.update_ipdomain(ipdomain_id, ip_address=new_ip)
        # Get the ipdomain
        fetched_ipdomain = self._show_ipdomain(ipdomain_id)
        self.assertEqual(new_ip, fetched_ipdomain['ipdomain']['ip_address'])

    @test.attr(type='smoke')
    @test.idempotent_id('dcf479ee-7175-11e5-9e8a-00e0666de3ce')
    def test_delete_ipdomain(self):
        # Creates a ipdomain
        create_body = self._create_ipdomain(ip_address="192.168.3.3",
                                            domain="test.com")
        ipdomain_id = create_body["ipdomain"]["id"]
        # Delete ipdomain
        self.sf_network_client.delete_ipdomain(ipdomain_id)
        # Verify that the ipdomain deleted.
        self.assertRaises(lib_exc.NotFound,
                          self._show_ipdomain,
                          ipdomain_id)

    @test.idempotent_id('640a40cf-73d5-11e5-8423-00e0666de3ce')
    def test_delete_bulk_ipdomains(self):
        # Ipdomains default value: ipdomains = []
        ipdomains = []
        ipdomains.append(self._create_ipdomain(ip_address='10.0.0.1',
                                               domain='test1.com'))
        ipdomains.append(self._create_ipdomain(ip_address='10.0.0.2',
                                               domain='test2.com'))
        for key in ['ip_address', 'domain']:
            self.assertNotEqual(ipdomains[0]['ipdomain'][key],
                                ipdomains[1]['ipdomain'][key])
        self.assertNotEqual(ipdomains[0]['ipdomain']['id'],
                            ipdomains[1]['ipdomain']['id'])

        for i in range(0, 2):
            self._bulk_delete_ipdomain(ipdomains[i]['ipdomain']['id'])
