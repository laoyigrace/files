# Copyright 2012 OpenStack Foundation
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
import netaddr
from tempest.api.network import base
from oslo_log import log as logging
from tempest_lib import exceptions as lib_exc

from tempest import config

CONF = config.CONF

LOG = logging.getLogger(__name__)


class SfBaseNetworkTest(base.BaseNetworkTest):

    force_tenant_isolation = False
    credentials = ['primary']

    # Default to ipv4.
    _ip_version = 4

    @classmethod
    def setup_clients(cls):
        super(SfBaseNetworkTest, cls).setup_clients()
        cls.sf_network_client = cls.os.sf_network_client

    @classmethod
    def resource_setup(cls):
        super(SfBaseNetworkTest, cls).resource_setup()
        cls.network_cfg = CONF.network
        cls.ipdomains = []
        cls.ethertype = "IPv" + str(cls._ip_version)

    @classmethod
    def resource_cleanup(cls):
        if CONF.service_available.neutron:
            # Clean up ipdomains
            for ipdomain in cls.ipdomains:
                cls._sf_try_delete_resource(
                    cls.sf_network_client.delete_ipdomain, ipdomain['id'])
        super(SfBaseNetworkTest, cls).resource_cleanup()

    @classmethod
    def _sf_try_delete_resource(self, delete_callable, *args, **kwargs):
        try:
            delete_callable(*args, **kwargs)
        # if resource is not found, this means it was deleted in the test
        except lib_exc.NotFound:
            pass

    @classmethod
    def _create_ipdomain(cls, **kwargs):
        body = cls.sf_network_client.create_ipdomain(**kwargs)
        return body

    @classmethod
    def _list_ipdomain(cls):
        body = cls.sf_network_client.list_ipdomains()
        # get the number of ipdomains
        ipdomain_num = len(body['ipdomains'])
        return body, ipdomain_num

    @classmethod
    def _show_ipdomain(cls, ipdomain_id, **kwargs):
        body = cls.sf_network_client.show_ipdomain(ipdomain_id, **kwargs)
        return body


class SfRouteAclBaseNetworkTest(base.BaseNetworkTest):

    force_tenant_isolation = False
    credentials = ['primary']

    @classmethod
    def setup_clients(cls):
        super(SfRouteAclBaseNetworkTest, cls).setup_clients()
        cls.sf_network_client = cls.os.sf_network_client

    @classmethod
    def resource_setup(cls):
        super(SfRouteAclBaseNetworkTest, cls).resource_setup()
        cls.network_cfg = CONF.network

    @classmethod
    def _create_router_aclgroup(cls, **kwargs):
        body = cls.sf_network_client.create_router_aclgroup(**kwargs)
        return body

    @classmethod
    def _create_router_acl(cls, **kwargs):
        body = cls.sf_network_client.create_router_acl(**kwargs)
        return body

    @classmethod
    def _get_private_cidr(cls):
        body = cls.client.list_networks(**{'router:external': False})
        networks = [network for network in body['networks']]
        if len(networks) > 0:
            network = networks[0]
            body = cls.client.show_subnet(network['subnets'][0])
            cidr = netaddr.IPNetwork(body['subnet']['cidr']).ip
        else:
            cidr = netaddr.IPNetwork(cls.network_cfg.tenant_network_cidr).ip
        private_cidr = str(cidr + 2) + '-' + str(cidr + 4)
        return private_cidr

    @classmethod
    def _get_public_cidr(cls):
        body = cls.client.list_networks(**{'router:external': True})
        networks = [network for network in body['networks']]
        if len(networks) > 0:
            network = networks[0]
            body = cls.client.show_subnet(network['subnets'][0])
            cidr = netaddr.IPNetwork(body['subnet']['cidr']).ip
        else:
            cidr = netaddr.IPAddress('172.0.0.0')
        public_cidr = str(cidr + 2) + '-' + str(cidr + 4)
        return public_cidr


class SfNameserverBaseNetworkTest(base.BaseNetworkTest):

    force_tenant_isolation = False
    credentials = ['primary']

    # Default to ipv4.
    _ip_version = 4

    @classmethod
    def setup_clients(cls):
        super(SfNameserverBaseNetworkTest, cls).setup_clients()
        cls.sf_network_client = cls.os.sf_network_client

    @classmethod
    def resource_setup(cls):
        super(SfNameserverBaseNetworkTest, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(SfNameserverBaseNetworkTest, cls).resource_cleanup()

    @classmethod
    def _create_nameserver(cls, **kwargs):
        body = cls.sf_network_client.create_nameserver(**kwargs)
        return body

    @classmethod
    def _list_nameservers(cls):
        body = cls.sf_network_client.list_nameservers()
        return body

    @classmethod
    def _show_nameserver(cls, nameserver_id, **kwargs):
        body = cls.sf_network_client.show_nameserver(nameserver_id, **kwargs)
        return body
