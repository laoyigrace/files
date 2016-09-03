# Copyright 2015 Sangfor Technologies Co., Ltd.
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

from tempest.api_schema.response.compute.v2_1 import sf_evacuates as schema
from tempest.services.compute.json.servers_client import ServersClient


# NOTE(15533): When using this sf extended class, you should replace
# 'ServersClientJSON' to 'SfServersClientJSON' in file '/tempest/clients.py'
class SfServersClient(ServersClient):
    def __init__(self, auth_provider, service, region,
                 enable_instance_password=True, **kwargs):
        super(SfServersClient, self).__init__(
            auth_provider, service, region,
            enable_instance_password, **kwargs)

    def sf_evacuate_server(self, server_id):
        """
        Evacuate a specific server by using sf-evacuate.
        server_id: The id of an existing server.
        """
        return self.action(server_id, "sf_evacuate", None,
                           schema=schema.sf_evacuate_common_schema)

    def sf_evacuate_server_to_specific_host(self, server_id, host):
        """
        Evacuate a specific server to a specific host by using sf-evacuate.
        server_id: The id of an existing server.
        host: The name of an existing host which not same as server's.
        """
        return self.action(server_id, "sf_evacuate", None,
                           schema=schema.sf_evacuate_common_schema,
                           host=host)

    def sf_force_stop(self, server_id, **kwargs):
        return self.action(server_id, 'os-force-stop', None, **kwargs)
