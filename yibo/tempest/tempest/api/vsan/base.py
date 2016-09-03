# -*- coding:utf-8 -*-
# Copyright 2015 Sangfor Technologies Co., Ltd
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

# from oslo_log import log as logging
# from tempest_lib import exceptions as lib_exc
# from tempest.common import fixed_network
# from tempest.common.utils import data_utils
from tempest import config
from tempest import exceptions
import tempest.test

CONF = config.CONF

# LOG = logging.getLogger(__name__)

class BaseVsanTest(tempest.test.BaseTestCase):

    #credentials = ['primary']
    credentials = ['primary', 'admin']
    @classmethod
    def setup_credentials(cls):
        #cls.set_network_resources()
        super(BaseVsanTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseVsanTest, cls).setup_clients()
        cls.servers_client = cls.os.servers_client
        cls.networks_client = cls.os.networks_client
        #os_adm
        cls.vsan_client = cls.os_adm.vsan_client

    @classmethod
    def resource_setup(cls):
        super(BaseVsanTest, cls).resource_setup()
        cls.build_interval = CONF.vs.build_interval
        cls.build_timeout = CONF.vs.build_timeout

    @staticmethod
    def cleanup_resources(method, list_of_ids):
        for resource_id in list_of_ids:
            try:
                method(resource_id)
            except lib_exc.NotFound:
                pass

    @classmethod
    def resource_cleanup(cls):
        super(BaseVsanTest, cls).resource_cleanup()

    @classmethod
    def create_vsan_cluster(cls,**kwargs):
        vsan_cluster = cls.vsan_client.create_vsan_cluster(**kwargs)
        # 检查状态
        return vsan_cluster

    @classmethod
    def init_vsan_cluster(cls, cluster_id, node_type,
                          cluster_init_cfg,
                          display_name=None,
                          display_description=None):
        respBody = cls.vsan_client.init_vsan_cluster(cluster_id, cluster_init_cfg,
                                                         display_name=display_name,
                                                         display_description=display_description,
                                                         node_type=node_type)
        # 检查状态
        return respBody







