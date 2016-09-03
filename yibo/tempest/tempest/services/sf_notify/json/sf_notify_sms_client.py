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


class SfNotifySmsClient(service_client.ServiceClient):
    uri_prefix = "v1"

    def sms_create(self, phone, message):
        """
        create sms
        :param phone(required): The phone number to send
        :param message(required): Content of short message
        """
        uri = "%s/sms/send" % self.uri_prefix
        post_body = {'phone': phone,
                     'sms': message
                     }
        post_body = json.dumps(post_body)
        resp, body = self.post(uri, post_body)
        self.expected_success(201, resp.status)
        body = json.loads(body)
        return service_client.ResponseBody(resp, body)

    def sms_config_set(self, cfg, **kwargs):
        """
        update config ini file
        :param cfg: dict of config like this:
        {section:{option:value}}
        :param kwargs: multiple section
        """
        uri = "%s/sms/config" % self.uri_prefix

        if kwargs:
            cfg.update(kwargs)
        cfg = json.dumps(cfg)
        post_body = {
            'config': cfg
        }

        post_body = json.dumps(post_body)
        resp, body = self.post(uri, post_body)
        self.expected_success(201, resp.status)
        body = json.loads(body)
        return service_client.ResponseBody(resp, body)

    def sms_config_get(self):
        """
        get config ini file
        """
        uri = "%s/sms/config" % self.uri_prefix
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return service_client.ResponseBody(resp, body)


