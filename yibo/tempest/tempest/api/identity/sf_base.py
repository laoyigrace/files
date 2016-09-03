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
from tempest.api.identity import base

class SfBaseIdentityV2AdminTest(base.BaseIdentityV2AdminTest):
    @classmethod
    def setup_clients(cls):
        super(SfBaseIdentityV2AdminTest, cls).setup_clients()
        cls.sf_client = cls.os_adm.sf_identity_client
        cls.network_client = cls.os_adm.network_client
        cls.sf_network_client = cls.os_adm.sf_network_client
        cls.nova_quotas_client = cls.os_adm.quotas_client
        cls.volume_quotas_client = cls.os_adm.volume_quotas_client

    @classmethod
    def resource_setup(cls):
        super(SfBaseIdentityV2AdminTest, cls).resource_setup()
        tenant = cls.client.create_tenant('test_user@sangfor.com',
                                          description='test_user@sangfor.com')
        cls.alt_tenant_id = tenant['id']
        # update quotas
        cores = 128
        ram = 262144
        gigabytes = 10240
        network = 10
        subnet = 10
        # nova cores , ram
        cls.nova_quotas_client.update_quota_set(cls.alt_tenant_id, ram=ram, cores=cores)
        # volume gigabytes
        cls.volume_quotas_client.update_quota_set(cls.alt_tenant_id, gigabytes=gigabytes)
        # neutron network , subnet
        cls.network_client.update_quotas(cls.alt_tenant_id, network=network, subnet=subnet)
        role = cls.get_role_by_name('_member_')
        kwargs = {'router:external': True, 'name': 'test_user_network'}
        net = cls.network_client.create_network(**kwargs)
        cls.network_client.create_subnet(
            network_id=net['network']['id'],
            cidr='172.180.0.0/24',
            ip_version=4)
        cls.alt_network_id = net['network']['id']
        cls.alt_role_id = role['id']
        cls.alt_user = 'test_user@sangfor.com'
        cls.alt_password = 'password123'
        cls.alt_phone = '12345678901'
        cls.alt_company = 'Sangfor'
        cls.alt_place = 'NanShanZhiYuan'
        cls.alt_flag = '_sangfor'

    @classmethod
    def resource_cleanup(cls):
        super(SfBaseIdentityV2AdminTest, cls).resource_cleanup()
        cls.network_client.delete_network(cls.alt_network_id)
        cls.client.delete_tenant(cls.alt_tenant_id)
