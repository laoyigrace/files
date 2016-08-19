# Copyright 2011 OpenStack Foundation
# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2011 Grid Dynamics
# Copyright 2011 Eldar Nugaev, Kirill Shileev, Ilya Alekseyev
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

from oslo_log import log as logging
import webob
import traceback

from nova.api.openstack import common
from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova import compute
from nova import exception
from nova.i18n import _
from nova.i18n import _LE
from webob import exc
from nova.compute import sf_api
from nova.api.openstack.compute.contrib.attach_interfaces import InterfaceAttachmentController
from nova.api.openstack.compute.contrib.volumes import VolumeAttachmentController

LOG = logging.getLogger(__name__)

#authorize = extensions.extension_authorizer('compute', 'snapshot')


class SFActionController(wsgi.Controller):
    def __init__(self, ext_mgr=None, *args, **kwargs):
        super(SFActionController, self).__init__(*args, **kwargs)
        self.compute_api = compute.API()
        self.sf_compute_api = sf_api.SF_API()
        self.ext_mgr = ext_mgr
        self.inter_attach_control = InterfaceAttachmentController()
        self.volume_attach_control = VolumeAttachmentController()

    @wsgi.action('os-force-stop')
    def force_stop_server(self, req, id, body):
        """force stop an instance."""
        context = req.environ['nova.context']
        instance = common.get_instance(self.compute_api, context, id)
        extensions.check_compute_policy(context, 'stop', instance)

        LOG.debug("context = %s", context)

        try:
            self.compute_api.stop(context, instance, clean_shutdown=False)
        except exception.InstanceInvalidState as state_error:
            common.raise_http_conflict_for_instance_invalid_state(
                state_error, 'force_stop', id)
        except (exception.InstanceNotReady, exception.InstanceIsLocked) as e:
            raise webob.exc.HTTPConflict(explanation=e.format_message())
        return webob.Response(status_int=202)

    @wsgi.action('access_networks')
    def access_networks(self, req, id, body):
        """
        access network
        :param req   request
        :param id   server id
        :param body       body {"access_networks":{
        "attach_interfaces":[{interfaceAttachment:{"port_id":"xxx-yy-xx"}},{interfaceAttachment:{"port_id":"xxx-yy-xx"}},...],
        "detach_interfaces":[{"port_id":port_id1},{"port_id":port_id2},...]
        }}
        """

        update_interfaces = body.get("access_networks")

        detach_interfaces = update_interfaces['detach_interfaces']
        attach_interfaces = update_interfaces['attach_interfaces']

        for interface in detach_interfaces:
            if 'port_id' not in interface:
                continue

            port_id = interface['port_id']
            try:
                self.inter_attach_control.delete(req, id, port_id)
            except Exception as ex:
                LOG.debug(
                    "server = %s, interface = %s, detach failed! err = %s", id,
                    interface, ex)

        for interface in attach_interfaces:

            try:
                self.inter_attach_control.create(req, id, interface)
            except Exception as ex:
                LOG.debug(
                    "server = %s, interface = %s, attach failed! err = %s", id,
                    interface, ex)

        return webob.Response(status_int=202)

    @wsgi.action('attach_detach_volumes')
    def attach_detach_volumes(self, req, id, body):
        """
        attach and detach volume
        :param req   request
        :param server_id   server id
        :param body       body {"attach_detach_volumes":{
        "detach_volumes":[{"volumeId":"volumeId1"},{"volumeId":"volumeId1"},,...],
        "attach_volumes":[{volumeAttachment:{"volumeId":"--"}},,...]
        }}
        """
        LOG.debug("begin to attach_detach_volumes server = %s", id)
        attach_detach_dict = body.get("attach_detach_volumes")

        detach_volumes = attach_detach_dict['detach_volumes']
        attach_volumes = attach_detach_dict['attach_volumes']

        for volume in detach_volumes:
            if 'volumeid' not in volume:
                continue

            volume_id = volume['volumeid']
            try:
                self.volume_attach_control.delete(req, id, volume_id)
            except Exception as ex:
                LOG.debug("server = %s, volume = %s, detach failed! err = %s",
                          id, volume, ex)

        for volume in attach_volumes:

            try:
                self.volume_attach_control.create(req, id, volume)
            except Exception as ex:
                LOG.debug("server = %s, volume = %s, attach failed! err = %s",
                          id, volume, ex)

        return webob.Response(status_int=202)


#name must be same to filename
class Sf_action(extensions.ExtensionDescriptor):
    """"""

    name = "sf_action"
    alias = "os-sf-action"
    namespace = "http://docs.openstack.org/compute/ext/sf_action/api/v1.1"
    updated = "2015-08-03T00:00:00Z"

    def get_controller_extensions(self):
        controller = SFActionController()
        extension = extensions.ControllerExtension(self, 'servers', controller)
        return [extension]
