# Copyright 2015 NEC Corporation. All rights reserved.
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

from oslo_serialization import jsonutils as json

from tempest.api_schema.response.compute.v2_1 import tenant_networks as schema

from tempest.api_schema.response.compute.v2_1 import servers as server_schema
from tempest.common import service_client


class SfTenantNetworksClient(service_client.ServiceClient):

    def list_tenant_networks(self):
        resp, body = self.get("os-tenant-networks")
        body = json.loads(body)
        self.validate_response(schema.list_tenant_networks, resp, body)
        return service_client.ResponseBodyList(resp, body['networks'])

    def show_tenant_network(self, network_id):
        resp, body = self.get("os-tenant-networks/%s" % network_id)
        body = json.loads(body)
        self.validate_response(schema.get_tenant_network, resp, body)
        return service_client.ResponseBody(resp, body['network'])

    def access_networks(self, server, attach_networks=None,
                        detach_networks=None):

        request_body = {'access_networks': {}}
        attach_list = []
        detach_list = []

        if attach_networks:
            for network in attach_networks:
                attach_dict = {'interfaceAttachment': {}}
                if 'net_id' in network:
                    attach_dict['interfaceAttachment']['net_id'] = \
                        network['net_id']
                attach_list.append(attach_dict)

        if detach_networks:
            for port_id in detach_networks:
                detach_dict = dict()
                detach_dict['port_id'] = port_id
                detach_list.append(detach_dict)

        request_body['access_networks']['attach_interfaces'] = attach_list
        request_body['access_networks']['detach_interfaces'] = detach_list

        request_body = json.dumps(request_body)
        resp, body = self.post('/servers/%s/action' % server, request_body)
        return resp, body

