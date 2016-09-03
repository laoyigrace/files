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

from tempest.api.sfprocess import sf_base
from tempest.common.utils import data_utils
from tempest import test


class SfprocessTest(sf_base.SfBaseSfprocessTest):
    """testcase for sfprocess api """

    @test.attr(type='smoke')
    @test.idempotent_id('31c3d891-c4c8-11e5-ad14-00e0666534ba')
    def test_create_net_service(self):
        # create net-service with tcp protocol
        service_name = data_utils.rand_name('net-service-31c3d891')
        protocol = 'tcp:1-65535'
        net_service = self.sfprocess_client.create_net_service(service_name=service_name,
                                                               protocol=protocol)
        self.addCleanup(self.sfprocess_client.delete_net_service, net_service['net_service']['service_id'])
        self.assertEqual(net_service['net_service']["service_name"], service_name)
        self.assertEqual(net_service['net_service']["protocol"], protocol)

    @test.attr(type='smoke')
    @test.idempotent_id('1371e4cf-c4c9-11e5-b9c5-00e0666534ba')
    def test_create_udp_and_update_icmp_net_service(self):
        # create net-service with udp protocol
        service_name = data_utils.rand_name('net-service-1371e4cf')
        protocol = 'udp:1265,3333-4444'
        net_service = self.sfprocess_client.create_net_service(service_name=service_name,
                                                               protocol=protocol)
        self.addCleanup(self.sfprocess_client.delete_net_service, net_service['net_service']['service_id'])
        self.assertEqual(net_service['net_service']["service_name"], service_name)
        self.assertEqual(net_service['net_service']["protocol"], protocol)
        # update net-service with icmp protocol
        new_protocol = 'icmp:type:8,code:0;type:9,code:0'
        new_service_name = data_utils.rand_name('net-service-update-1371e4cf')
        net_service = self.sfprocess_client.update_net_service(net_service['net_service']['service_id'],
                                                               service_name=new_service_name,
                                                               protocol=new_protocol)
        self.assertEqual(net_service['net_service']["service_name"], new_service_name)
        self.assertEqual(net_service['net_service']["protocol"], new_protocol)

    @test.attr(type='smoke')
    @test.idempotent_id('8050eae1-c4cb-11e5-ae6d-00e0666534ba')
    def test_create_other_and_delete_net_service(self):
        # create net-service with other protocol
        service_name = data_utils.rand_name('net-service-8050eae1')
        protocol = 'other:45'
        net_service = self.sfprocess_client.create_net_service(service_name=service_name,
                                                               protocol=protocol)
        self.assertEqual(net_service['net_service']["service_name"], service_name)
        self.assertEqual(net_service['net_service']["protocol"], protocol)
        # delete net-service
        self.sfprocess_client.delete_net_service(net_service['net_service']['service_id'])

    @test.idempotent_id('47145e61-c4da-11e5-8e35-00e0666534ba')
    def test_list_and_show_net_service(self):
        # create net-service with other protocol
        service_name = data_utils.rand_name('net-service-47145e61')
        protocol = 'other:45'
        net_service = self.sfprocess_client.create_net_service(service_name=service_name,
                                                               protocol=protocol)
        net_service_id = net_service['net_service']['service_id']
        self.addCleanup(self.sfprocess_client.delete_net_service, net_service_id)
        self.assertEqual(net_service['net_service']["service_name"], service_name)
        self.assertEqual(net_service['net_service']["protocol"], protocol)
        # list net-service
        net_service_list_body = self.sfprocess_client.list_net_services()
        net_service = [net_service['service_id'] for net_service in net_service_list_body['net_service']
                      if net_service['service_id'] == net_service_id]
        self.assertNotEmpty(net_service, "Created net_service not found in the list")
        # show net-service
        net_service_show_body = self.sfprocess_client.show_net_service(net_service_id)
        self.assertEqual(net_service_show_body['net_service']['service_name'], service_name)
        self.assertEqual(net_service_show_body['net_service']['protocol'], protocol)
