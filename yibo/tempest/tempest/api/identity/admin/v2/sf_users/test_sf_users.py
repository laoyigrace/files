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

from testtools import matchers

from tempest.api.identity import sf_base
from tempest.common.utils import data_utils
from tempest import test


class SfUsersTestJSON(sf_base.SfBaseIdentityV2AdminTest):
    @test.attr(type='smoke')
    @test.idempotent_id('01d5c540-9574-11e5-b330-00e0666534ba')
    def test_create_user(self):
        # Create a user
        user = self.sf_client.create_user(name=self.alt_user, password=self.alt_password,
                                          tenant_id=self.alt_tenant_id,
                                          phone=self.alt_phone, unit=self.alt_company,
                                          place=self.alt_place, add_flag=self.alt_flag)
        user_id = user['id']
        self.addCleanup(self.client.delete_user, user_id)
        self.assertEqual(self.alt_user, user['name'])
        self.assertEqual(self.alt_phone, user['phone'])
        self.assertEqual(self.alt_company, user['unit'])
        self.assertEqual(self.alt_place, user['place'])
        self.assertEqual(self.alt_flag, user['add_flag'])
        # assign tenant, user and role
        role_assigns = self.client.list_user_roles(self.alt_tenant_id, user_id)
        member = [role_assign['name'] for role_assign in role_assigns
                  if role_assign['name'] == '_member_']
        if len(member) == 0:
            self.client.assign_user_role(self.alt_tenant_id, user_id, self.alt_role_id)
        # add default config
        # create router
        router = self.network_client.create_router('default_router', external_gateway_info={
            "network_id": self.alt_network_id}, admin_state_up=True, tenant_id=self.alt_tenant_id)
        self.addCleanup(self.network_client.delete_router, router['router']['id'])
        self.assertEqual(router['router']['name'], 'default_router')
        self.assertEqual(router['router']['tenant_id'], self.alt_tenant_id)
        # add dnsproxy
        nameserver1 = self.sf_network_client.create_nameserver(major=True, address='8.8.8.8',
                                                               tenant_id=self.alt_tenant_id)
        self.addCleanup(self.sf_network_client.delete_nameserver, nameserver1['sfnameserver']['id'])
        self.assertEqual(nameserver1['sfnameserver']['tenant_id'], self.alt_tenant_id)
        self.assertTrue(nameserver1['sfnameserver']['major'])
        self.assertEqual(nameserver1['sfnameserver']['address'], '8.8.8.8')
        nameserver2 = self.sf_network_client.create_nameserver(major=False, address='8.8.8.7',
                                                               tenant_id=self.alt_tenant_id)
        self.addCleanup(self.sf_network_client.delete_nameserver, nameserver2['sfnameserver']['id'])
        self.assertEqual(nameserver2['sfnameserver']['tenant_id'], self.alt_tenant_id)
        self.assertFalse(nameserver2['sfnameserver']['major'])
        self.assertEqual(nameserver2['sfnameserver']['address'], '8.8.8.7')
        # add_network
        net = self.network_client.create_network(name='default_network', tenant_id=self.alt_tenant_id,
                                                 admin_state_up=True)
        self.addCleanup(self.network_client.delete_network, net['network']['id'])
        self.assertEqual(net['network']['name'], 'default_network')
        self.assertEqual(net['network']['tenant_id'], self.alt_tenant_id)
        subnet = self.network_client.create_subnet(
            name='default_subnet', enable_dhcp=True,
            tenant_id=self.alt_tenant_id, network_id=net['network']['id'],
            cidr='192.168.0.0/24', ip_version=4)
        self.addCleanup(self.network_client.delete_subnet, subnet['subnet']['id'])
        self.assertEqual(subnet['subnet']['name'], 'default_subnet')
        # default quota
        # nova cores 128, ram 262144
        nova_quotas = self.nova_quotas_client.show_quota_set(self.alt_tenant_id)
        self.assertEqual(nova_quotas['cores'], 128)
        self.assertEqual(nova_quotas['ram'], 262144)
        # volume gigabytes 10240
        volume_quotas = self.volume_quotas_client.show_quota_set(self.alt_tenant_id)
        self.assertEqual(volume_quotas['gigabytes'], 10240)
        # neutron network 10, subnet 10
        neutron_quotas = self.network_client.show_quotas(self.alt_tenant_id)
        self.assertEqual(neutron_quotas['quota']['network'], 10)
        self.assertEqual(neutron_quotas['quota']['subnet'], 10)

    @test.attr(type='smoke')
    @test.idempotent_id('0e02aeee-9574-11e5-97ec-00e0666534ba')
    def test_update_user_info(self):
        # Test case to check if updating of user attributes is successful.
        user = self.sf_client.create_user(name=self.alt_user, password=self.alt_password,
                                          tenant_id=self.alt_tenant_id,
                                          phone=self.alt_phone, unit=self.alt_company,
                                          place=self.alt_place, add_flag=self.alt_flag)
        # Delete the User at the end of this method
        self.addCleanup(self.client.delete_user, user['id'])
        # Updating user details with new values
        u_name2 = data_utils.rand_name('user2@sangfor.com')
        u_phone2 = '09876543212'
        u_company2 = 'Sinfor'
        u_place2 = 'ZhiYuanNanShan'
        update_user = self.client.update_user(user['id'], name=u_name2,
                                              phone=u_phone2, unit=u_company2,
                                              place=u_place2)
        self.assertEqual(u_name2, update_user['name'])
        self.assertEqual(u_phone2, update_user['phone'])
        self.assertEqual(u_company2, update_user['unit'])
        self.assertEqual(u_place2, update_user['place'])

    @test.attr(type='smoke')
    @test.idempotent_id('f901ad40-95a4-11e5-ab05-00e0666534ba')
    def test_update_user_quotas(self):
        # Test case to check if updating of user attributes is successful.
        user = self.sf_client.create_user(name=self.alt_user, password=self.alt_password,
                                          tenant_id=self.alt_tenant_id,
                                          phone=self.alt_phone, unit=self.alt_company,
                                          place=self.alt_place, add_flag=self.alt_flag)
        # Delete the User at the end of this method
        self.addCleanup(self.client.delete_user, user['id'])
        # update quotas
        cores = 10
        ram = 2621440
        gigabytes = 20480
        network = 100
        subnet = 100
        # nova cores , ram
        nova_quotas = self.nova_quotas_client.update_quota_set(self.alt_tenant_id,
                                                               ram=ram, cores=cores)
        self.assertEqual(nova_quotas['cores'], 10)
        self.assertEqual(nova_quotas['ram'], 2621440)
        # volume gigabytes
        volume_quotas = self.volume_quotas_client.update_quota_set(self.alt_tenant_id,
                                                                   gigabytes=gigabytes)
        self.assertEqual(volume_quotas['gigabytes'], 20480)
        # neutron network , subnet
        neutron_quotas = self.network_client.update_quotas(self.alt_tenant_id,
                                                           network=network, subnet=subnet)
        self.assertEqual(neutron_quotas['quota']['network'], 100)
        self.assertEqual(neutron_quotas['quota']['subnet'], 100)

    @test.attr(type='smoke')
    @test.idempotent_id('0a693e40-95a5-11e5-8959-00e0666534ba')
    def test_update_user_network(self):
        # Test case to check if updating of user attributes is successful.
        user = self.sf_client.create_user(name=self.alt_user, password=self.alt_password,
                                          tenant_id=self.alt_tenant_id,
                                          phone=self.alt_phone, unit=self.alt_company,
                                          place=self.alt_place, add_flag=self.alt_flag)
        # Delete the User at the end of this method
        self.addCleanup(self.client.delete_user, user['id'])
        # create router
        router = self.network_client.create_router('default_router', external_gateway_info={
            "network_id": self.alt_network_id}, admin_state_up=True, tenant_id=self.alt_tenant_id)
        self.addCleanup(self.network_client.delete_router, router['router']['id'])
        self.assertEqual(router['router']['external_gateway_info']['network_id'], self.alt_network_id)
        # create network
        net = self.network_client.create_network(name='test_user_network2')
        self.addCleanup(self.network_client.delete_network, net['network']['id'])
        subnet = self.network_client.create_subnet(
            network_id=net['network']['id'],
            cidr='172.182.0.0/24',
            ip_version=4)
        self.addCleanup(self.network_client.delete_subnet, subnet['subnet']['id'])
        # change router gateway
