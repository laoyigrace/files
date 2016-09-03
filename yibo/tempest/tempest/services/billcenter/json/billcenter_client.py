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

from oslo_serialization import jsonutils as json
from six.moves.urllib import parse as urllib

from tempest.common import service_client


class BillCenterClient(service_client.ServiceClient):
    version = '2'
    uri_prefix = "v2"

    def deserialize(self, body):
        return json.loads(body.replace("\n", ""))

    def serialize(self, body):
        return json.dumps(body)

    def _helper_list(self, uri, query=None, period=None):
        uri_dict = {}
        if query:
            uri_dict = {'q.field': query[0],
                        'q.op': query[1],
                        'q.value': query[2]}
        if period:
            uri_dict['period'] = period
        if uri_dict:
            uri += "?%s" % urllib.urlencode(uri_dict)
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBodyList(resp, body)

    def _helper_list_multi_query(self, uri, **kwargs):
        uri_dict = {}
        list_url_encode = []
        query = kwargs.get('query')
        if query is not None:
            for q in query:
                query_params = {'q.field': q['field'],
                                'q.op': q['op'],
                                'q.value': q['value'],
                                }

                list_url_encode.append(urllib.urlencode(query_params))
        period = kwargs.get('period')
        if period:
            uri_dict["period"] = period
        merge = kwargs.get('merge')
        if merge:
            uri_dict["merge"] = merge
            list_url_encode.append(urllib.urlencode(uri_dict))

        uri += "?%s" % '&'.join(list_url_encode)
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBodyList(resp, body)

    def create_bill_policy(self, region="guangdong", policies=[], **kwargs):
        uri = "%s/billcenter/policy" % self.uri_prefix
        policy_body = []
        for param in policies:
            body = {
                "meter": param[0],
                "price": param[1],
                "enabled": kwargs.get("enabled", True)
            }
            policy_body.append(body)

        # policy = dict()
        # policy[meter] = {'price': price}
        # policy['meter']['enabled'] = kwargs.get('enabled', True)

        post_body = {
            "region": region,
            "policy": policy_body,
            "description": kwargs.get("description", "sf")
        }

        post_body = json.dumps(post_body)
        resp, body = self.post(uri, post_body)
        self.expected_success(201, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def list_bill_policy(self):
        uri = "%s/billcenter/policy" % self.uri_prefix
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBodyList(resp, body)

    def get_bill_policy(self, region):
        uri = "%s/billcenter/policy/%s" % (self.uri_prefix, region)
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def update_bill_policy(self, region, policies, **kwargs):
        uri = "%s/billcenter/policy" % self.uri_prefix
        policy_body = []
        for param in policies:
            body = {
                "meter": param[0],
                "price": param[1],
                "enabled": kwargs.get("enabled", True)
            }
            policy_body.append(body)

        post_body = {
            "region": region,
            "policy": policy_body,
            "description": kwargs.get("desc", "sf")
        }

        post_body = json.dumps(post_body)
        resp, body = self.post(uri, post_body)
        self.expected_success(201, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBodyList(resp, body)

    def create_bill_pay(self, tenant_id, author, **kwargs):
        uri = "%s/billcenter/pay" % self.uri_prefix
        post_body = {
            'tenant_id': tenant_id,
            'author': author,
            'base_account_pay': kwargs.get('base_account_pay', 0),
            'free_account_pay': kwargs.get('free_account_pay', 0),
            'remarks': kwargs.get('remark', 'recharge')

        }

        post_body = json.dumps(post_body)
        resp, body = self.post(uri, post_body)
        self.expected_success(201, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def list_bill_pay(self, query=None):
        uri = "%s/billcenter/pay" % self.uri_prefix
        return self._helper_list(uri, query)

    def cut_bill_pay(self, tenant_id, **kwargs):
        uri = "%s/billcenter/pay/cut_pay" % self.uri_prefix
        post_body = {
            'tenant_id': tenant_id,
            'base_account_pay': kwargs.get('base_account_pay', 0),
            'free_account_pay': kwargs.get('free_account_pay', 0),
            'remarks': kwargs.get('remark', '')
        }
        post_body = json.dumps(post_body)
        resp, body = self.post(uri, post_body)
        self.expected_success(201, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def get_bill_balance(self, tenant_id):
        uri = "%s/billcenter/balance/%s" % (self.uri_prefix, tenant_id)
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def charge_bill(self, region, last_time, flows):
        uri = "%s/billcenter/charge" % self.uri_prefix
        post_body = {
            'region': region,
            'uuid': str(last_time),
            'flows': flows,
        }
        post_body = json.dumps(post_body)
        resp, body = self.post(uri, post_body)
        self.expected_success(201, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def get_cost(self, query=None):
        uri = "%s/billcenter/cost" % self.uri_prefix
        return self._helper_list(uri, query)

    def set_charge_setting(self, alarm_title, **kwargs):
        uri = "%s/billcenter/charge_setting" % self.uri_prefix
        post_body = {
            'alarm_title': alarm_title,
            'alarm_content': kwargs.get('alarm_content', "tempest test"),
            'alarm_count': kwargs.get('alarm_content', 2),
            'alarm_time ': kwargs.get('alarm_time', "9:00"),
            'invoice_threshold :': kwargs.get('invoice_threshold', 100),
            'resource_threshold ': kwargs.get('resource_threshold', 100),
            'email_enabled ': kwargs.get('email_enabled', False),
            'msg_enabled': kwargs.get('msg_enabled', True),
            'sms_enabled': kwargs.get('sms_enabled', False)

        }

        post_body = json.dumps(post_body)
        resp, body = self.post(uri, post_body)
        self.expected_success(201, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def show_alarm(self, alarm_id):
        uri = '%s/alarms/%s' % (self.uri_prefix, alarm_id)
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def delete_alarm(self, alarm_id):
        uri = "%s/alarms/%s" % (self.uri_prefix, alarm_id)
        resp, body = self.delete(uri)
        self.expected_success(204, resp.status)
        if body:
            body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def create_alarm(self, **kwargs):
        uri = "%s/alarms" % self.uri_prefix
        body = self.serialize(kwargs)
        resp, body = self.post(uri, body)
        self.expected_success(201, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def update_alarm(self, alarm_id, **kwargs):
        uri = "%s/alarms/%s" % (self.uri_prefix, alarm_id)
        body = self.serialize(kwargs)
        resp, body = self.put(uri, body)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)


