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

import json
from tempest.common import service_client


class SfSnapshotClient(service_client.ServiceClient):
    def __init__(self, auth_provider, service, region, **kwargs):
        super(SfSnapshotClient, self).__init__(
            auth_provider, service, region, **kwargs)

    def create_snapshot(self, server_id, **kwargs):
        """
        POST    /v2/<project_id>/os-sf-snapshot
        :return: resp, body are dict
        """
        # vda is system disk，vdb is data disk,
        request_body = {
            "desc": "tempest api test",
            "instance_uuid": "",
            "name": "",
            "type": "internal"
        }
        request_body.update(kwargs)
        request_body['instance_uuid'] = server_id

        body_json = json.dumps(request_body)
        resp, body = self.post('os-sf-snapshot', body_json)
        body = json.loads(body)
        # self.validate_response(schema.list_snapshot, resp, body)
        return resp, body

    def list_snapshot(self, server_id):
        """
        POST    /v2/${project_id}/os-sf-snapshot/detail
        :return: resp, body are dict
        """
        request_body = {"instance_uuid": server_id}
        body_json = json.dumps(request_body)
        resp, body = self.post('os-sf-snapshot/detail', body_json)
        body = json.loads(body)
        # self.validate_response(schema.list_snapshot, resp, body)
        return resp, body

    def update_snapshot(self, snapshot_id, **kwargs):
        """
        PUT    /v2/${project_id}/os-sf-snapshot/${snapshot_id}
        :return: resp is dict, body is none
        """
        request_body = kwargs
        body_json = json.dumps(request_body)
        resp, body = self.put('os-sf-snapshot/%s' % snapshot_id, body_json)
        # self.validate_response(schema.list_snapshot, resp, body)
        return resp

    def delete_snapshot(self, snapshot_id):
        """
        DELETE  /v2/${project_id}/os-sf-snapshot/${snapshot_id}
        """
        resp, body = self.delete('os-sf-snapshot/%s' % snapshot_id)
        return resp

    def revert_snapshot(self, instance_id, snapshot_id):
        """
        POST /v2/${project_id}/os-sf-snapshot/revert
        """
        request_body = {}
        request_body['instance_uuid'] = instance_id
        request_body['snapshot_id'] = snapshot_id
        body_json = json.dumps(request_body)
        resp, body = self.post('os-sf-snapshot/revert', body_json)
        return resp

    def list_chain(self):
        """
        GET /v2/${project_id}/os-sf-snapshot/list_chain
        :return body is string(json format)
        """
        resp, body = self.get('os-sf-snapshot/list_chain')
        return body

    def del_chain(self, chain_id):
        """
        POST /v2/${project_id}/os-sf-snapshot/delete_chain
        """
        request_body = {"chain_id": chain_id}
        body_json = json.dumps(request_body)
        resp, body = self.post('os-sf-snapshot/delete_chain', body_json)
        return resp

    def force_stop(self, instance_id):
        """
        POST    /v2/${project_id}/servers/${instance_id}/action
        request_body = {"os-force-stop": null}
        :return:
        """
        request_body = {"os-force-stop": None}
        body_json = json.dumps(request_body)
        resp, body = self.post('servers/%s/action' % instance_id, body_json)
        return resp

    def create_image(self, **kwargs):
        """
        POST /v2/${project_id}/os-sf-snapshot/create_image
        :return: body in None
        """
        request_body = {
            "image_name": "",
            "snapshot_id": "",
            "instance_uuid": "",
            "desc": ""
        }
        request_body.update(kwargs)
        body_json = json.dumps(request_body)
        resp, body = self.post("os-sf-snapshot/create_image", body_json)
        return resp


