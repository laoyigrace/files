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

from oslo_log import log as logging
from tempest import config
from tempest import sf_config
from tempest.services.sf_notify.json.sf_notify_email_client import \
    SfNotifyEmailClient
from tempest.services.compute.json.sf_snapshot_client import SfSnapshotClient
from tempest.services.sf_notify.json.sf_notify_sms_client import \
    SfNotifySmsClient
from tempest.services.compute.json.sf_tenant_networks_client import \
    SfTenantNetworksClient
from tempest.services.sfprocess.json.sfprocess_client import \
    SfprocessClient
from tempest.services.sfpool.json.sfpool_client import \
    SfpoolClient

from tempest.services.volume.v2.json.admin.storage_client import \
    BaseStorageClient

from tempest.services.billcenter.json.billcenter_client import BillCenterClient

import clients

CONF = config.CONF
LOG = logging.getLogger(__name__)


class SfManager(clients.Manager):
    """
    Extend manager for OpenStack tempest clients
    """

    def __init__(self, credentials=None, service=None):
        super(SfManager, self).__init__(credentials=credentials,
                                        service=service)
        self._set_sf_notify_client()
        self._set_compute_clients()
        self._set_sfprocess_client()
        self._set_billcenter_client()
        self._set_sfpool_client()

    def _set_sf_notify_client(self):
        params = {
            'service': CONF.sf_notify.catalog_type,
            'region': CONF.sf_notify.region or CONF.identity.region,
            'endpoint_type': CONF.sf_notify.endpoint_type
        }
        params.update(self.default_params)
        self.sf_notify_email_client = SfNotifyEmailClient(self.auth_provider,
                                                          **params)
        self.sf_notify_sms_client = SfNotifySmsClient(self.auth_provider,
                                                      **params)

    def _set_compute_clients(self):
        super(SfManager, self)._set_compute_clients()
        params = {
            'service': CONF.compute.catalog_type,
            'region': CONF.compute.region or CONF.identity.region,
            'endpoint_type': CONF.compute.endpoint_type,
            'build_interval': CONF.compute.build_interval,
            'build_timeout': CONF.compute.build_timeout
        }
        params.update(self.default_params)
        self.sf_snapshot_client = SfSnapshotClient(self.auth_provider,
                                                   **params)
        self.sf_tenant_networks_client = SfTenantNetworksClient(
            self.auth_provider, **params)

    def _set_sfprocess_client(self):
        params = {
            'service': CONF.sfprocess.catalog_type,
            'region': CONF.sfprocess.region or CONF.identity.region,
            'endpoint_type': CONF.sfprocess.endpoint_type
        }
        params.update(self.default_params)
        self.sfprocess_client = SfprocessClient(self.auth_provider,
                                                **params)

    def _set_sfpool_client(self):
        params = {
            'service': CONF.sfpool.catalog_type,
            'region': CONF.sfpool.region or CONF.identity.region,
            'endpoint_type': CONF.sfpool.endpoint_type,
        }
        params.update(self.default_params)
        self.sfpool_client = SfpoolClient(self.auth_provider, **params)

    def _set_volume_clients(self):
        super(SfManager, self)._set_volume_clients()
        params = {
            'service': CONF.volume.catalog_type,
            'region': CONF.volume.region or CONF.identity.region,
            'endpoint_type': CONF.volume.endpoint_type,
            'build_interval': CONF.volume.build_interval,
            'build_timeout': CONF.volume.build_timeout
        }
        self.storage_client = BaseStorageClient(
            self.auth_provider, **params)

    def _set_billcenter_client(self):
        params = {
            'service': CONF.billcenter.catalog_type,
            'region': CONF.billcenter.region,
            'endpoint_type': CONF.billcenter.endpoint_type
        }
        params.update(self.default_params)
        self.billcenter_client = BillCenterClient(self.auth_provider,
                                                  **params)
