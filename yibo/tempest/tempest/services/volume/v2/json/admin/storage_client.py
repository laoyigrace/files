from oslo_serialization import jsonutils as json
import six
from six.moves.urllib import parse as urllib
from tempest_lib import exceptions as lib_exc

from tempest.common import service_client


class BaseStorageClient(service_client.ServiceClient):
    """
    Base client class to send CRUD iscsi and fc API requests to Cinder endpoint
    """

    api_version = "v2"

    def _prepare_params(self, params):
        """Prepares params for use in get or _ext_get methods.

        If params is a string it will be left as it is, but if it's not it will
        be urlencoded.
        """
        if isinstance(params, six.string_types):
            return params
        return urllib.urlencode(params)

    # NOTE (fty)
    # New API, to send CRUD ISCSI and FC API requests to a Cinder endpoint
    def add_iscsi_server(self, iscsi_ip, iscsi_port):
        """add a new iscsi server"""
        post_body = {"iscsi-ip": iscsi_ip,
                     "iscsi-port": iscsi_port
                     }
        post_body = json.dumps({"iscsi": post_body})
        resp, body = self.post('iscsi', post_body)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body['iscsi'])

    def delete_iscsi_server(self, iscsi_id):
        """Deletes the Specified iscsi server."""
        resp, body = self.delete("iscsi/%s" % str(iscsi_id))
        self.expected_success(202, resp.status)
        return service_client.ResponseBody(resp, body)

    def list_iscsi_server(self, detail=True, params=None):
        """List all the iscsi server."""
        url = 'iscsi'
        if detail:
            url += '/detail'
        if params:
            url += '?%s' % self._prepare_params(params)

        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBodyList(resp, body['servers'])

    def show_iscsi_server(self, iscsi_id):
        """Returns the details of a single iscsi server."""
        url = 'iscsi/show?iscsi_id=%s' % iscsi_id
        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def list_iscsi_target(self, detail=True, params=None):
        """List all the iscsi target."""
        url = 'target'
        if detail:
            url += '/detail'
        if params:
            url += '?%s' % self._prepare_params(params)

        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBodyList(resp, body['targets'])

    def show_iscsi_target(self, target_id):
        """Returns the details of a single iscsi target."""
        url = 'target/show?target_id=%s' % target_id
        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def add_iscsi_storage(self, disk_id, node_list, **kwargs):
        """add a new iscsi storage"""
        post_body = {
            "disk_id": disk_id,
            "node_list": node_list,
            "display_name": kwargs.get("name"),
            "description": kwargs.get("description")
        }
        post_body = json.dumps({"storage": post_body})
        resp, body = self.post('storage', post_body)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body['storage'])

    def list_iscsi_storage(self, detail=True, params=None):
        """List all the iscsi storage."""
        url = 'storage'
        if detail:
            url += '/detail'
        if params:
            url += '?%s' % self._prepare_params(params)

        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBodyList(resp, body['storages'])

    def show_iscsi_storage(self, storage_id):
        """Returns the details of a single iscsi storage."""
        url = 'storage/show?storage_id=%s' % storage_id
        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def delete_iscsi_storage(self, storage_id):
        """Deletes the Specified iscsi server."""
        resp, body = self.delete("storage/%s" % str(storage_id))
        self.expected_success(202, resp.status)
        return service_client.ResponseBody(resp, body)
