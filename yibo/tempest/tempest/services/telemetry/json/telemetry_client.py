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


class TelemetryClient(service_client.ServiceClient):

    version = '2'
    uri_prefix = "v2"

    def deserialize(self, body):
        return json.loads(body.replace("\n", ""))

    def serialize(self, body):
        return json.dumps(body)

    def add_sample(self, sample_list, meter_name, meter_unit, volume,
                   sample_type, resource_id, **kwargs):
        sample = {"counter_name": meter_name, "counter_unit": meter_unit,
                  "counter_volume": volume, "counter_type": sample_type,
                  "resource_id": resource_id}
        for key in kwargs:
            sample[key] = kwargs[key]

        sample_list.append(self.serialize(sample))
        return sample_list

    def create_sample(self, meter_name, sample_list):
        uri = "%s/meters/%s" % (self.uri_prefix, meter_name)
        body = self.serialize(sample_list)
        resp, body = self.post(uri, body)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

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

    def list_resources(self, query=None):
        uri = '%s/resources' % self.uri_prefix
        return self._helper_list(uri, query)

    def list_meters(self, query=None):
        uri = '%s/meters' % self.uri_prefix
        return self._helper_list(uri, query)

    def list_alarms(self, query=None):
        uri = '%s/alarms' % self.uri_prefix
        return self._helper_list(uri, query)

    def list_statistics(self, meter, period=None, query=None):
        uri = "%s/meters/%s/statistics" % (self.uri_prefix, meter)
        return self._helper_list(uri, query, period)

    def list_samples(self, meter_id, query=None):
        uri = '%s/meters/%s' % (self.uri_prefix, meter_id)
        return self._helper_list(uri, query)

    def show_resource(self, resource_id):
        uri = '%s/resources/%s' % (self.uri_prefix, resource_id)
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
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

    def show_alarm_state(self, alarm_id):
        uri = "%s/alarms/%s/state" % (self.uri_prefix, alarm_id)
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBodyData(resp, body)

    def alarm_set_state(self, alarm_id, state):
        uri = "%s/alarms/%s/state" % (self.uri_prefix, alarm_id)
        body = self.serialize(state)
        resp, body = self.put(uri, body)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBodyData(resp, body)

    # [sangfor]
    def _helper_list_stats(self, uri, **kwargs):
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

    def list_stats(self, **kwargs):
        uri = '%s/stats' % self.uri_prefix
        return self._helper_list_stats(uri, **kwargs)

    def update_alarm_group(self, alarm_id, alarms):
        uri = "%s/alarm_group/%s" % (self.uri_prefix, alarm_id)
        body = self.serialize(alarms)
        resp, body = self.put(uri, body)
        self.expected_success(200, resp.status)

    def get_alarm(self, alarm_id):
        uri = '%s/alarm_group/%s' % (self.uri_prefix, alarm_id)
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def get_alarm_group(self):
        uri = '%s/alarm_group' % self.uri_prefix
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBodyList(resp, body)

    def get_spec_alarm_policy(self, alarm_obj):
        uri = '%s/alarm_group/%s' % (self.uri_prefix, alarm_obj)
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def create_bill_policy(self, meter, price, **kwargs):
        uri = "%s/bill/policy" % self.uri_prefix
        post_body = {
            "meter": meter,
            "price": price,
            "description": kwargs.get('description', "")
        }
        if kwargs.get('enabled') is not None:
            post_body['enabled'] = kwargs.get('enabled')
        post_body = json.dumps([post_body])
        resp, body = self.post(uri, post_body)
        self.expected_success(201, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBodyList(resp, body)

    def create_batch_policy(self, array, **kwargs):
        uri = "%s/bill/policy" % self.uri_prefix
        post_body = []
        for param in array:
            body = {
                "meter": param[0],
                "price": param[1],
                "description": param[2],
                "enabled": kwargs.get("enabled", True)
            }
            post_body.append(body)
        post_body = json.dumps(post_body)
        resp, body = self.post(uri, post_body)
        self.expected_success(201, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBodyList(resp, body)

    def list_bill_policy(self):
        uri = "%s/bill/policy" % self.uri_prefix
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBodyList(resp, body)

    def delete_bill_policy(self, meter):
        uri = "%s/bill/policy/%s" % (self.uri_prefix, meter)
        resp, body = self.delete(uri)
        self.expected_success(204, resp.status)
        if body:
            body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def update_bill_policy(self, meter, price=None,
                           description=None, enabled=True):
        uri = "%s/bill/policy" % self.uri_prefix
        post_body = {'meter': meter}

        if price is not None:
            post_body['price'] = price

        if description is not None:
            post_body['description'] = description

        if enabled is not None:
            post_body['enabled'] = enabled

        post_body = json.dumps([post_body])
        resp, body = self.post(uri, post_body)
        self.expected_success(201, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBodyList(resp, body)

    def create_bill_pay(self, tenant_id, pay):
        uri = "%s/bill/pay" % self.uri_prefix
        post_body = {
            'tenant_id': tenant_id,
            'payment': pay
        }

        post_body = json.dumps(post_body)
        resp, body = self.post(uri, post_body)
        self.expected_success(201, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def list_bill_pay(self, query=None):
        uri = "%s/bill/pay" % self.uri_prefix
        return self._helper_list(uri, query)

    # deprecate since the interface has changed
    # def list_pay_history(self, tenant_id):
    #     uri = "%s/bill/pay/%s" % (self.uri_prefix, tenant_id)
    #     resp, body = self.get(uri)
    #     self.expected_success(200, resp.status)
    #     body = self.deserialize(body)
    #     return service_client.ResponseBodyList(resp, body)

    def get_bill_balance(self, tenant_id):
        uri = "%s/bill/balance/%s" % (self.uri_prefix, tenant_id)
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBody(resp, body)

    def get_balance_alarm(self, threshold):
        uri = "%s/bill/balance?%s" % (
            self.uri_prefix, urllib.urlencode(threshold))
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = self.deserialize(body)
        return service_client.ResponseBodyList(resp, body)