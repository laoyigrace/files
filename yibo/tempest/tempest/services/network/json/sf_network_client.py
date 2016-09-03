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
from six.moves.urllib import parse as urllib
from tempest.common import service_client


class SfNetworkClient(service_client.ServiceClient):

    """
    Tempest REST client for Neutron. Uses v2 of the Neutron API, since the
    V1 API has been removed from the code base.

    Implements create, delete, update, list and show for the basic Neutron
    abstractions (networks, sub-networks, routers, ports and floating IP):

    Implements add/remove interface to router using subnet ID / port ID

    It also implements list, show, update and reset for OpenStack Networking
    quotas
    """

    version = '2.0'
    uri_prefix = "v2.0"

    def _list_resources(self, uri, **filters):
        req_uri = self.uri_prefix + uri
        if filters:
            req_uri += '?' + urllib.urlencode(filters, doseq=1)
        resp, body = self.get(req_uri)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def _delete_resource(self, uri):
        req_uri = self.uri_prefix + uri
        resp, body = self.delete(req_uri)
        self.expected_success(204, resp.status)
        return service_client.ResponseBody(resp, body)

    def _show_resource(self, uri, **fields):
        # fields is a dict which key is 'fields' and value is a
        # list of field's name. An example:
        # {'fields': ['id', 'name']}
        req_uri = self.uri_prefix + uri
        if fields:
            req_uri += '?' + urllib.urlencode(fields, doseq=1)
        resp, body = self.get(req_uri)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def _create_resource(self, uri, post_data):
        req_uri = self.uri_prefix + uri
        req_post_data = json.dumps(post_data)
        resp, body = self.post(req_uri, req_post_data)
        body = json.loads(body)
        self.expected_success(201, resp.status)
        return service_client.ResponseBody(resp, body)

    def _update_resource(self, uri, post_data):
        req_uri = self.uri_prefix + uri
        req_post_data = json.dumps(post_data)
        resp, body = self.put(req_uri, req_post_data)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    # ipdomain
    def create_ipdomain(self, **kwargs):
        uri = '/ipdomains'
        post_data = {'ipdomain': kwargs}
        return self._create_resource(uri, post_data)

    def update_ipdomain(self, ipdomain_id, **kwargs):
        uri = '/ipdomains/%s' % ipdomain_id
        body = self._show_resource(uri)
        update_body = {}
        update_body['ip_address'] = kwargs.get('ip_address',
                                               body['ipdomain']['ip_address'])
        update_body['domain'] = kwargs.get('domain',
                                           body['ipdomain']['domain'])
        update_body = dict(ipdomain=update_body)
        return self._update_resource(uri, update_body)

    def show_ipdomain(self, ipdomain_id, **fields):
        uri = '/ipdomains/%s' % ipdomain_id
        return self._show_resource(uri, **fields)

    def delete_ipdomain(self, ipdomain_id):
        uri = '/ipdomains/%s' % ipdomain_id
        return self._delete_resource(uri)

    def list_ipdomains(self, **filters):
        uri = '/ipdomains'
        return self._list_resources(uri, **filters)

    # router_aclgroup
    def create_router_aclgroup(self, **kwargs):
        uri = '/router-acl-groups'
        post_data = {'router_acl_group': kwargs}
        return self._create_resource(uri, post_data)

    def delete_router_aclgroup(self, router_aclgroup_id):
        uri = '/router-acl-groups/%s' % router_aclgroup_id
        return self._delete_resource(uri)

    def list_router_aclgroups(self, **filters):
        uri = '/router-acl-groups'
        return self._list_resources(uri, **filters)

    # router_acl
    def create_router_acl(self, **kwargs):
        uri = '/router-acls'
        post_data = {'router_acl': kwargs}
        return self._create_resource(uri, post_data)

    def delete_router_acl(self, router_acl_id):
        uri = '/router-acls/%s' % router_acl_id
        return self._delete_resource(uri)

    def list_router_acls(self, **filters):
        uri = '/router-acls'
        return self._list_resources(uri, **filters)

    def show_router_acl(self, router_acl_id):
        uri = '/router-acls/%s' % router_acl_id
        return self._list_resources(uri)

    def update_router_acl(self, router_acl_id, **kwargs):
        uri = '/router-acls/%s' % router_acl_id
        update_body = {'router_acl': kwargs}
        return self._update_resource(uri, update_body)

    def create_portmap(self, router_id, **kwargs):
        uri = '/nat/port_maps'
        post_data = {
            'port_map': {
                'router_id': router_id,
                'priority': kwargs.get(
                    'priority',
                    2),
                'external_ip': kwargs.get(
                    'external_ip',
                    '2.2.2.2'),
                'external_port': kwargs.get(
                    'external_port',
                    1000),
                'interanet_ip': kwargs.get(
                    'interanet_ip',
                    '1.1.1.1'),
                'protocol': kwargs.get(
                    'protocol',
                    'udp'),
                'status': kwargs.get(
                    'status',
                    'enable'),
                'tenant_id': kwargs.get(
                    'tenant_id',
                    'test-tenant_id'),
                'rule_name': kwargs.get(
                    'rule_name',
                    'test-rule_name'),
                'rule_desc': kwargs.get(
                    'rule_desc',
                    'test-rule_desc'),
                'interanet_port': kwargs.get(
                    'interanet_port',
                    2000),
            }}
        return self._create_resource(uri, post_data)

    def update_portmap(self, portmap_id, **kwargs):
        uri = '/nat/port_maps/%s' % portmap_id
        body = self._show_resource(uri)
        update_body = {}
        update_body['router_id'] = kwargs.get('router_id',
                                              body['port_map']['router_id'])
        update_body['priority'] = kwargs.get('priority', 100)
        update_body['external_ip'] = kwargs.get('external_ip', '1.1.1.1')
        update_body['external_port'] = kwargs.get('external_port', 100)
        update_body['interanet_ip'] = kwargs.get('interanet_ip', '10.10.10.10')
        update_body['interanet_port'] = kwargs.get('domain', 200)
        update_body['protocol'] = kwargs.get('protocol', 'tcp')
        update_body['status'] = kwargs.get('status',
                                           body['port_map']['status'])
        update_body['rule_desc'] = kwargs.get('rule_desc',
                                              body['port_map']['rule_desc'])
        update_body = dict(port_map=update_body)
        return self._update_resource(uri, update_body)

    def show_portmap(self, portmap_id, **fields):
        uri = '/nat/port_maps/%s' % portmap_id
        return self._show_resource(uri, **fields)

    def delete_portmap(self, portmap_id):
        uri = '/nat/port_maps/%s' % portmap_id
        return self._delete_resource(uri)

    def list_portmaps(self, **filters):
        uri = '/nat/port_maps'
        return self._list_resources(uri, **filters)

    def create_qos(self, port_id, **kwargs):
        uri = '/qos/interface_qoss'
        post_data = {
            'interface_qos': {
                'port_id': port_id,
                'tenant_id': kwargs.get(
                    'tenant_id',
                    2),
                'qos_uplink': kwargs.get(
                    'qos_uplink',
                    500),
                'qos_downlink': kwargs.get(
                    'qos_downlink',
                    1000),
            }}
        return self._create_resource(uri, post_data)

    def update_qos(self, qos_id, **kwargs):
        uri = '/qos/interface_qoss/%s' % qos_id
        body = self._show_resource(uri)
        update_body = {}
        update_body['port_id'] = kwargs.get('port_id',
                                            body['interface_qos']['port_id'])
        update_body['qos_uplink'] = kwargs.get('qos_uplink', 100)
        update_body['qos_downlink'] = kwargs.get('qos_downlink', 200)
        update_body = dict(interface_qos=update_body)
        return self._update_resource(uri, update_body)

    def show_qos(self, qos_id, **fields):
        uri = '/qos/interface_qoss/%s' % qos_id
        return self._show_resource(uri, **fields)

    def delete_qos(self, qos_id):
        uri = '/qos/interface_qoss/%s' % qos_id
        return self._delete_resource(uri)

    def list_qoss(self, **filters):
        uri = '/qos/interface_qoss'
        return self._list_resources(uri, **filters)

    def create_floatingip_alloc(self, floating_network_id,
                                **kwargs):
        uri = '/nat/sf_fip_allocs'
        post_data = {}
        post_data['sf_fip_alloc'] = {}
        post_data['sf_fip_alloc']['external_network_id'] = floating_network_id
        post_data['sf_fip_alloc']['qos_uplink'] = kwargs.get('qos_uplink',
                                                             '1000')
        post_data['sf_fip_alloc']['qos_downlink'] = kwargs.get('qos_downlink',
                                                               '1000')
        return self._create_resource(uri, post_data)

    def delete_floatingip_alloc(self, floating_id):
        uri = '/nat/sf_fip_allocs/%s' % floating_id
        return self._delete_resource(uri)

    def show_floatingip_alloc(self, floating_id):
        uri = '/nat/sf_fip_allocs/%s' % floating_id
        return self._show_resource(uri)

    def list_floatingips_alloc(self, **filters):
        uri = '/nat/sf_fip_allocs'
        return self._list_resources(uri, **filters)

    def update_floatingip_alloc(self, floating_id, **kwargs):
        uri = '/nat/sf_fip_allocs/%s' % floating_id
        update_body = {}
        update_body['qos_uplink'] = kwargs.get('qos_uplink', '2048')
        update_body['qos_downlink'] = kwargs.get('qos_downlink', '4096')
        update_body = dict(sf_fip_alloc=update_body)
        return self._update_resource(uri, update_body)

    def create_floatingip(self, router_id, sffip_id, tenant_id, **kwargs):
        uri = '/nat/one_to_one_nats'
        post_data = {}
        post_data['one_to_one_nat'] = {}
        post_data['one_to_one_nat']['router_id'] = router_id
        post_data['one_to_one_nat']['sffip_id'] = sffip_id
        post_data['one_to_one_nat']['intranet_ip'] = kwargs.get('intranet_ip',
                                                                '10.10.122.110'
                                                                )
        post_data['one_to_one_nat']['tenant_id'] = tenant_id

        return self._create_resource(uri, post_data)

    def delete_floatingip(self, floating_id):
        uri = '/nat/one_to_one_nats/%s' % floating_id
        return self._delete_resource(uri)

    def show_floatingip(self, floating_id):
        uri = '/nat/one_to_one_nats/%s' % floating_id
        return self._show_resource(uri)

    def list_floatingips(self, **filters):
        uri = '/nat/one_to_one_nats'
        return self._list_resources(uri, **filters)

    def update_floatingip(self, floating_id, **kwargs):
        uri = '/nat/one_to_one_nats/%s' % floating_id
        update_body = {}
        update_body['one_to_one_nat'] = {}
        update_body['one_to_one_nat']['intranet_ip'] = \
            kwargs.get('intranet_ip', '192.200.200.200')
        return self._update_resource(uri, update_body)

    # nameserver
    def create_nameserver(self, **kwargs):
        uri = '/sfnameservers'
        post_data = {'sfnameserver': kwargs}
        return self._create_resource(uri, post_data)

    def delete_nameserver(self, nameserver_id):
        uri = '/sfnameservers/%s' % nameserver_id
        return self._delete_resource(uri)

    def update_nameserver(self, nameserver_id, **kwargs):
        uri = '/sfnameservers/%s' % nameserver_id
        update_body = {'sfnameserver': kwargs}
        return self._update_resource(uri, update_body)

    def show_nameserver(self, nameserver_id, **fields):
        uri = '/sfnameservers/%s' % nameserver_id
        return self._show_resource(uri, **fields)

    def list_nameservers(self, **filters):
        uri = '/sfnameservers'
        return self._list_resources(uri, **filters)

    def show_network(self, network_id, **fields):
        uri = '/networks/%s' % network_id
        return self._show_resource(uri, **fields)
   
    def create_subnet(self, kwargs):
        uri = '/subnets'
        post_data = {'subnet': kwargs}
        return self._create_resource(uri, post_data)

    def router_update(self, router_id, action, **kwargs):
        uri = '/routers/%s' % router_id
        router_info = {}
        router_info = {'routes':action}
        post_data = {'router': router_info}
        return self._update_resource(uri, post_data)

    def router_show(self, router_id, **fields):
        uri = '/routers/%s' % router_id
        return self._show_resource(uri, **fields)

    def add_router_interface(self, router_id, subnet_id):
        uri = '/routers/%s/add_router_interface' % router_id
        post_data = {'subnet_id':subnet_id}
        return self._update_resource(uri, post_data)

    def remove_router_interface(self, router_id, subnet_id):
        uri = '/routers/%s/remove_router_interface' % router_id
        post_data = {'subnet_id':subnet_id}
        return self._update_resource(uri, post_data)
