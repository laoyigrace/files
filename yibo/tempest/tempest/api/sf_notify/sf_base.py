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

from tempest import config
from oslo_log import log as logging
from tempest_lib import exceptions as lib_exc
from tempest.common.utils import data_utils
from tempest.common.utils.linux import sf_remote_client

import tempest.test


CONF = config.CONF
LOG = logging.getLogger(__name__)
_PATH = '/sf/sbin:/sf/bin:/sf/sdn/bin:/usr/sbin:/usr/bin:/sbin:' \
        '/bin:/sf/bin/busybox:/root/bin'
_set_path_cmd = 'export PATH=%s;' % _PATH


class SfBaseSfNotifyTest(tempest.test.BaseTestCase):
    """Base test case class for all sf-notify API tests."""

    # only set credentials, test.BaseTestCase.setup_credentials
    # will active 'os'
    credentials = ['primary']

    # must keep
    @classmethod
    def setup_credentials(cls):
        cls.set_network_resources()
        super(SfBaseSfNotifyTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(SfBaseSfNotifyTest, cls).setup_clients()
        cls.sf_notify_email_client = cls.os.sf_notify_email_client
        cls.sf_notify_sms_client = cls.os.sf_notify_sms_client

    @classmethod
    def resource_setup(cls):
        super(SfBaseSfNotifyTest, cls).resource_setup()

    @staticmethod
    def cleanup_resources(method, list_of_ids):
        for resource_id in list_of_ids:
            try:
                method(resource_id)
            except lib_exc.NotFound:
                pass

    @classmethod
    def resource_cleanup(cls):
        cls.sf_notify_email_client.email_delete()
        super(SfBaseSfNotifyTest, cls).resource_cleanup()

    @classmethod
    def enable_email(cls):
        resp, body = cls.sf_notify_email_client.email_enable()
        return body

    @classmethod
    def disable_email(cls):
        resp, body = cls.sf_notify_email_client.email_disable()
        return body

    def create_email(cls, **kwargs):
        request_body = {
            "email_addr": "%s" % data_utils.rand_name() + "@sangfor.com",
            "email_host": "%s" % data_utils.rand_name("host"),
            # delete email_password, email_user
            "email_password": "%s" % data_utils.rand_name("password"),
            "email_user": "%s" % data_utils.rand_name("user"),
            "email_port": 25,
        }
        request_body.update(kwargs)
        resp, body = cls.sf_notify_email_client.email_create(request_body)
        return resp, body

    @classmethod
    def update_email(cls, **kwargs):
        request_body = {}
        request_body.update(kwargs)
        resp, body = cls.sf_notify_email_client.email_update(request_body)
        return resp, body

    @classmethod
    def send_email(cls, **kwargs):
        request_body = {
            "tomail_list": "%s" % data_utils.rand_name() + "@sangfor.com"
        }
        request_body.update(kwargs)
        resp = cls.sf_notify_email_client.email_send(request_body)
        return resp

    @staticmethod
    def _exec_command(cmd):
        linux_client = sf_remote_client.SfRemoteClient(
            server=CONF.sf_common_info.ctl_host,
            username=CONF.sf_common_info.ctl_ssh_username,
            password=CONF.sf_common_info.ctl_ssh_password)
        return linux_client.exec_command(cmd)

    @classmethod
    def sf_encrypt(cls, str_encrypt):
        # if not set $PATH, would can't find pwdenc command
        cmd = _set_path_cmd + 'pwdenc %s' % str_encrypt
        output_data = cls._exec_command(cmd)
        return output_data

    @classmethod
    def sf_decrypt(cls, str_decrypt):
        cmd = _set_path_cmd + 'pwddec %s' % str_decrypt
        output_data = cls._exec_command(cmd)
        return output_data
