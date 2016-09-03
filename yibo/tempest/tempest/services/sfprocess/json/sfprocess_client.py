# Copyright 2014 OpenStack Foundation
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

import time

from oslo_serialization import jsonutils as json
from six.moves.urllib import parse as urllib
from tempest_lib.common.utils import misc
from tempest_lib import exceptions as lib_exc
from tempest.common import service_client
from tempest import exceptions

class SfprocessClient(service_client.ServiceClient):


    def _list_resources(self, uri, **filters):
        req_uri = uri
        if filters:
            req_uri += '?' + urllib.urlencode(filters, doseq=1)
        resp, body = self.get(req_uri)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def _delete_resource(self, uri):
        req_uri = uri
        resp, body = self.delete(req_uri)
        self.expected_success(204, resp.status)
        return service_client.ResponseBody(resp, body)

    def _show_resource(self, uri, **fields):
        # fields is a dict which key is 'fields' and value is a
        # list of field's name. An example:
        # {'fields': ['id', 'name']}
        req_uri = uri
        if fields:
            req_uri += '?' + urllib.urlencode(fields, doseq=1)
        resp, body = self.get(req_uri)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def _create_resource(self, uri, post_data):
        req_uri = uri
        req_post_data = json.dumps(post_data)
        resp, body = self.post(req_uri, req_post_data)
        body = json.loads(body)
        self.expected_success(202, resp.status)
        return service_client.ResponseBody(resp, body)

    def _update_resource(self, uri, post_data):
        req_uri = uri
        req_post_data = json.dumps(post_data)
        resp, body = self.put(req_uri, req_post_data)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def create_net_service(self, **kwargs):
        uri = '/net-service'
        post_data = {'net_service': kwargs}
        return self._create_resource(uri, post_data)

    def update_net_service(self, service_id, **kwargs):
        uri = '/net-service/%s' % service_id
        post_data = {'net_service': kwargs}
        return self._update_resource(uri, post_data)

    def show_net_service(self, service_id, **fields):
        uri = '/net-service/%s' % service_id
        return self._show_resource(uri, **fields)

    def delete_net_service(self, service_id):
        uri = '/net-service/%s' % service_id
        return self._delete_resource(uri)

    def list_net_services(self, **filters):
        uri = '/net-service/detail'
        return self._list_resources(uri, **filters)
