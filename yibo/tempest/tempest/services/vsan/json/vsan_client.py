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

from oslo_serialization import jsonutils as json
import six
from six.moves.urllib import parse as urllib
from tempest_lib import exceptions as lib_exc

from tempest.common import service_client
from tempest.common import waiters
from tempest import exceptions
from tempest import config
CONF = config.CONF

class BaseVsanClient(service_client.ServiceClient):
    """
    Base client class to send CRUD Volume API requests to a Vsan endpoint
    """

    create_resp = 200
    delete_timeout = 600
    delete_interval = 10
    # hct:需要修改
   # def __init__(self, auth_provider, service, region,**kwargs):
   #     super(BaseVsanClient, self).__init__(
   #         auth_provider, service, region, **kwargs)

    #@classmethod
    def resource_setup(self):
        self.build_interval = CONF.vs.build_interval
        self.build_timeout = CONF.vs.build_timeout

    def _ext_get(self, url, key=None, status=200):
        """Extended get method.

        Retrieves requested url, checks that status is expected status and
        return a ResponseBody, ResponseBodyList or ResponseBodyData depending
        on received data's key entry.

        If key is not specified or is None we will return the whole body in a
        ResponseBody class.
        """

        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(status, resp.status)

        if not key:
            return service_client.ResponseBody(resp, body)
        elif isinstance(body[key], dict):
            return service_client.ResponseBody(resp, body[key])
        elif isinstance(body[key], list):
            return service_client.ResponseBodyList(resp, body[key])

        return service_client.ResponseBodyData(resp, body[key])

    def _prepare_params(self, params):
        """Prepares params for use in get or _ext_get methods.

        If params is a string it will be left as it is, but if it's not it will
        be urlencoded.
        """
        if isinstance(params, six.string_types):
            return params
        return urllib.urlencode(params)

    def list_vsan_clusters(self, detail=False, params=None, return_body=False):
        """List all the vsan clusters  created.

        Params can be a string (must be urlencoded) or a dictionary.
        If return_body is True then we will return the whole response body in
        a ResponseBody class, it it's False or has not been specified we will
        return only the list of volumes in a ResponseBodyList (inherits from
        list).
        """
        url = 'clusters'
        if detail:
            url += '/detail'
        if params:
            url += '?%s' % self._prepare_params(params)

        key = None if return_body else 'clusters'
        return self._ext_get(url, key)

    # Create vsan cluster
    def create_vsan_cluster(self, **kwargs):
        post_body = json.dumps({'cluster': kwargs})
        resp, body = self.post('clusters', post_body)

        body = json.loads(body)
        self.expected_success(self.create_resp, resp.status)
        return service_client.ResponseBody(resp,body['cluster'])

    # Show vsan cluster
    def show_vsan_cluster(self, cluster_id):
        """Returns the details of a single cluster."""
        url = "clusters/%s" % str(cluster_id)
        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body['cluster'])

    # Update vsan cluster
    def update_vsan_cluster(self, cluster_id, **kwargs):
        """Updates the Specified Vsan Cluster."""
        put_body = json.dumps({'cluster': kwargs})
        resp, body = self.put('clusters/%s' % cluster_id, put_body)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body['cluster'])

    # Delete vsan cluster
    def delete_vsan_cluster(self, cluster_id):
        """Deletes the Specified Cluster."""
        resp, body = self.delete("clusters/%s" % str(cluster_id))
        self.expected_success(202, resp.status)
        return service_client.ResponseBody(resp, body)

    # init vsan cluster
    def init_vsan_cluster(self, cluster_id,
                          cluster_init_cfg,
                          node_type,
                          display_name=None,
                          display_description=None):

        body = {'os-init_vs':{'init_para':cluster_init_cfg,
                                   'display_name':display_name,
                                   'display_description':display_description,
                                   'node_type':node_type}}

        post_body = json.dumps(body)
        url = 'clusters/%s/action'% cluster_id
        resp, body = self.post(url, post_body)

        #body = json.loads(body)
        self.expected_success(202, resp.status)
        return service_client.ResponseBody(resp)

    # replace_disk
    def replace_disk(self, cluster_id, host_from,
                     old_disk, host_to, new_disk):
        body = {'os-replace_disk': {'host_from' : host_from,
                                    'old_disk' : old_disk,
                                    'host_to' : host_to,
                                    'new_disk' : new_disk}}

        post_body = json.dumps(body)
        url = 'clusters/%s/action'% cluster_id
        resp, body = self.post(url, post_body)
        #body = json.loads(body)
        self.expected_success(202, resp.status)
        return service_client.ResponseBody(resp)

    # expand_vsan_cluster
    def expand_vsan_cluster_hosts(self, cluster_id, expand_host):
        body = {'os-expand_hosts': {'ehosts' : expand_host}}

        post_body = json.dumps(body)
        url = 'clusters/%s/action'% cluster_id
        resp, body = self.post(url, post_body)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    # expand_vsan_cluster
    def cancel_expand_vsan_cluster_hosts(self, cluster_id):
        body = {'os-cancel_expand_hosts': None}

        post_body = json.dumps(body)
        url = 'clusters/%s/action'% cluster_id
        resp, body = self.post(url, post_body)
        self.expected_success(202, resp.status)
        return service_client.ResponseBody(resp)

    # init vsan cluster
    def expand_vsan_cluster(self, cluster_id, expand_cfg):
        body = {'os-expand':{'expand_para':expand_cfg}}
        post_body = json.dumps(body)
        url = 'clusters/%s/action'% cluster_id
        resp, body = self.post(url, post_body)

        self.expected_success(202, resp.status)
        return service_client.ResponseBody(resp)


    # rebalance set
    def rebalance_set(self, cluster_id, date,
                     end_date, time, end_time):
        body = {'os-rebalance_set': {'date' : date,
                                     'end_date' : end_date,
                                     'time' : time,
                                     'end_time' : end_time}}

        post_body = json.dumps(body)
        url = 'clusters/%s/action'% cluster_id
        resp, body = self.post(url, post_body)
        #body = json.loads(body)
        self.expected_success(202, resp.status)
        return service_client.ResponseBody(resp)

    # rebalance get
    def rebalance_get(self, cluster_id):
        body = {'os-rebalance_get': None}

        post_body = json.dumps(body)
        url = 'clusters/%s/action'% cluster_id
        resp, body = self.post(url, post_body)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    # rebalance show
    def rebalance_show(self, cluster_id):
        body = {'os-rebalance_show': None}

        post_body = json.dumps(body)
        url = 'clusters/%s/action'% cluster_id
        resp, body = self.post(url, post_body)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    # rebalance stop
    def rebalance_stop(self, cluster_id):
        body = {'os-rebalance_stop': None}

        post_body = json.dumps(body)
        url = 'clusters/%s/action'% cluster_id
        resp, body = self.post(url, post_body)
        self.expected_success(202, resp.status)
        return service_client.ResponseBody(resp)

    # rebalance cancel
    def rebalance_cancel(self, cluster_id):
        body = {'os-rebalance_cancel': None}

        post_body = json.dumps(body)
        url = 'clusters/%s/action'% cluster_id
        resp, body = self.post(url, post_body)
        self.expected_success(202, resp.status)
        return service_client.ResponseBody(resp)

    # rebalance get
    def cluster_perform_get(self, cluster_id, time_type):
        body = {'os-cluster_perform_get': {'time_type':time_type}}

        post_body = json.dumps(body)
        url = 'clusters/%s/action'% cluster_id
        resp, body = self.post(url, post_body)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def wait_for_vsan_cluster_status(self, cluster_id, status):
        """Waits for a Volume to reach a given status."""
        waiters.wait_for_vsan_cluster_status(self, cluster_id, status)

    def wait_for_resource_deletion(self, id):
        waiters.wait_for_vsan_resource_deletion(self, id)

    def is_resource_deleted(self, id):
        try:
            cluster = self.show_vsan_cluster(id)
            if cluster['status'] == 'error_delete':
                raise exceptions.ClusterDeleteErrorException(cluster_id=id)
        except lib_exc.NotFound:
            return True
        return False

    @property
    def resource_type(self):
        """Returns the primary type of resource this client works with."""
        return 'cluster'


class VsanClient(BaseVsanClient):
    """
    Client class to send CRUD Volume V1 API requests to a Cinder endpoint
    """
