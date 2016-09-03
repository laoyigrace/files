

import time

from oslo_serialization import jsonutils as json
from six.moves.urllib import parse as urllib
from tempest_lib.common.utils import misc
from tempest_lib import exceptions as lib_exc
from tempest.common import service_client
from tempest import exceptions


class SfpoolClient(service_client.ServiceClient):
    api_version = "v2"

    def pool_common(self, opr, param):
        req_uri = '/pool/%s%s' %(opr, param)
        resp, body = self.get(req_uri)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def pool_add_storage(self, poolname=None, storage=None):
        param = "?pool=%s&storage=%s" % (poolname, storage)
        return self.pool_common("addstorage", param)

    def pool_del_storage(self, poolname=None, storage=None):
        param = "?pool=%s&storage=%s" % (poolname, storage)
        return self.pool_common("delstorage", param)

    def pool_add_host(self, poolname=None, host=None):
        param = "?pool=%s&host=%s" % (poolname, host)
        return self.pool_common("addhost", param)

    def pool_del_host(self, poolname=None, host=None):
        param = "?pool=%s&host=%s" % (poolname, host)
        return self.pool_common("delhost", param)

    def pool_detail(self, poolname=None):
        req_uri = '/pool/detail'
        if poolname is not None:
            req_uri = '/pool/detail?pool=%s' % poolname
        resp, body = self.get(req_uri)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def pool_create(self, poolname=None):
        req_uri = '/pool?pool=%s' % poolname
        resp, body = self.post(req_uri, None)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def pool_delete(self, poolname=None):
        req_uri = '/pool/%s' % poolname
        resp, body = self.delete(req_uri)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

