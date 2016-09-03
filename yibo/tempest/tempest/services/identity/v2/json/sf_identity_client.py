# coding=utf-8
# Copyright 2012 OpenStack Foundation
# Copyright 2013 Hewlett-Packard Development Company, L.P.
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

from oslo_serialization import jsonutils as json
from tempest.common import service_client

class SfIdentityClient(service_client.ServiceClient):
    api_version = "v2.0"

    def create_user(self, **kwargs):
        """Create a user."""
        post_body = {}
        if kwargs.get('tenant_id') is not None:
            post_body['tenantId'] = kwargs.get('tenant_id')
        if kwargs.get('enabled') is not None:
            post_body['enabled'] = kwargs.get('enabled')
        post_body = json.dumps({'user': dict(post_body, **kwargs)})
        resp, body = self.post('users', post_body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, self._parse_resp(body))