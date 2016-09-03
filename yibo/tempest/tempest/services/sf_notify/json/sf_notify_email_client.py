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

import json
from tempest.common import service_client


class SfNotifyEmailClient(service_client.ServiceClient):
    # def __init__(self, auth_provider, service, region, **kwargs):
    #     super(SfNotifyEmailClient, self).__init__(
    #         auth_provider, service, region, **kwargs)

    def email_create(self, request_body):
        """POST http://ctrl-pub.cloud.vt:8877/v1/comm/email"""
        body_json = json.dumps(request_body)
        resp, body = self.post("/v1/comm/email", body_json)
        body = json.loads(body)
        return resp, body

    def email_delete(self):
        """DELETE http://ctrl-pub.cloud.vt:8877/v1/comm/email/email"""
        resp = self.delete("/v1/comm/email/email")
        return resp

    def email_get(self):
        """GET http://ctrl-pub.cloud.vt:8877/v1/comm/email"""
        resp, body = self.get("/v1/comm/email")
        body = json.loads(body)
        return resp, body

    def email_update(self, request_body):
        """POST http://ctrl-pub.cloud.vt:8877/v1/comm/email"""
        body_json = json.dumps(request_body)
        resp, body = self.post("/v1/comm/email", body_json)
        body = json.loads(body)
        return resp, body

    def email_send(self, request_body):
        """POST http://ctrl-pub.cloud.vt:8877/v1/comm/email/send_email"""
        body_json = json.dumps(request_body)
        resp, body = self.post("/v1/comm/email/send_email", body_json)
        # body = json.loads(body)
        return resp

    def email_enable(self):
        """POST http://ctrl-pub.cloud.vt:8877/v1/comm/email/enable_email"""
        resp, body = self.post("/v1/comm/email/enable_email", body=None)
        # body = json.loads(body)
        return resp

    def email_disable(self):
        """POST http://ctrl-pub.cloud.vt:8877/v1/comm/email/disable_email"""
        resp, body = self.post("/v1/comm/email/disable_email", None)
        # body = json.loads(body)
        return resp
