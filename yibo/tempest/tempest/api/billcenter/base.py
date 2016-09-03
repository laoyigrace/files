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

from tempest_lib import exceptions as lib_exc

from tempest.common.sf_utils import billcenter_sqlachemy
from tempest.common.sf_utils import region_sqlachemy
from tempest.common.utils.linux import sf_remote_client
from tempest import config
import tempest.test

CONF = config.CONF

METER_BALANCE = 'bill/tenant/project_id/balance'

# 4 hours
ALARM_DURATION = 14400


class BaseBillcenterTest(tempest.test.BaseTestCase):
    """Base test case class for all Telemetry API tests."""

    credentials = ['primary']

    @classmethod
    def skip_checks(cls):
        super(BaseBillcenterTest, cls).skip_checks()
        if not CONF.service_available.billcenter:
            raise cls.skipException("billcenter support is required")

    @classmethod
    def setup_credentials(cls):
        cls.set_network_resources()
        super(BaseBillcenterTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseBillcenterTest, cls).setup_clients()
        cls.billcenter_client = cls.os.billcenter_client

    @classmethod
    def resource_setup(cls):
        super(BaseBillcenterTest, cls).resource_setup()
        cls.tenant_ids = []

    # @classmethod
    # def create_alarm(cls, **kwargs):
    #     body = cls.billcenter_client.create_alarm(
    #         name=data_utils.rand_name('telemetry_alarm'),
    #         type='threshold', **kwargs)
    #     cls.alarm_ids.append(body['alarm_id'])
    #     return body

    @staticmethod
    def cleanup_resources(method, list_of_ids):
        for resource_id in list_of_ids:
            try:
                method(resource_id)
            except lib_exc.NotFound:
                pass

    @classmethod
    def resource_cleanup(cls):
        super(BaseBillcenterTest, cls).resource_cleanup()

    @classmethod
    def get_billcenter_client(cls):
        billcenter = sf_remote_client.SfRemoteClient(
            server=CONF.sf_common_info.billcenter_host,
            username=CONF.sf_common_info.ctl_ssh_username,
            password=CONF.sf_common_info.ctl_ssh_password)
        return billcenter

    @classmethod
    def get_region_client(cls):
        region = sf_remote_client.SfRemoteClient(
            server=CONF.sf_common_info.ctl_host,
            username=CONF.sf_common_info.ctl_ssh_username,
            password=CONF.sf_common_info.ctl_ssh_password)
        return region

    @classmethod
    def get_center_conn(cls):
        remote = cls.get_billcenter_client()
        cmd = "cat /etc/billcenter/billcenter.conf | grep billcenter_connection " \
              "| cut -d '=' -f 2 | awk '{print $1}'"

        billcenter_connection = remote.exec_command(cmd)
        cls.center_conn = billcenter_sqlachemy.CenterConnection(
            billcenter_connection)

    @classmethod
    def get_region_conn(cls):
        remote = cls.get_region_client()
        region_cmd = "cat /etc/ceilometer/ceilometer.conf | " \
                     "grep bill_connection |cut -d '=' -f 2 | awk '{print $1}'"

        # get host like mysql.cloud.vt
        region_host_cmd = "cat /etc/ceilometer/ceilometer.conf | " \
                          "grep bill_connection |cut -d '=' -f 2 | " \
                          "awk '{print $1}'|cut -d '@' -f2 | cut -d '/' -f 1"

        # get host ip on /etc/hosts
        region_ip_cmd = "cat /etc/hosts |grep `cat /etc/ceilometer/ceilometer.conf | " \
                        "grep bill_connection |cut -d '=' -f 2 | " \
                        "awk '{print $1}'|cut -d '@' -f2 | cut -d '/' -f 1`|" \
                        "awk '{print $1}'"

        # remove the '\n'
        region_host = remote.exec_command(region_host_cmd)[:-1]
        region_ip = remote.exec_command(region_ip_cmd)[:-1]

        out = remote.exec_command(region_cmd)
        # replace host domain to ip like
        # 'mysql://ceilometer:CRHHfTA0@100.1.1.2/ceilometer'
        bill_connection = out.replace(region_host, region_ip)
        cls.region_conn = region_sqlachemy.RegionConnection(bill_connection)

    def charge_setting(self, alarm_title, **kwargs):
        body = self.billcenter_client.set_charge_setting(alarm_title, **kwargs)

        alarm_time = kwargs['alarm_time']
        hour = alarm_time.split(':')[0]
        minute = alarm_time.split(':')[1]
        cron_time = "%s %s * * *" % (minute, hour)
        time_constraints = [
            {
                'name': 'default',
                'start': cron_time,
                "duration": ALARM_DURATION,
            }
        ]

        alarm_id = 'bill-balance-alarm'

        alarm_exist = False
        # alarm_get = {}
        try:
            alarm_get = self.billcenter_client.show_alarm(alarm_id)
            alarm_exist = True
        except lib_exc.NotFound:
            pass

        if alarm_exist:
            try:
                alarm_get['time_constraints'] = time_constraints

                self.billcenter_client.update_alarm(alarm_id, **alarm_get)
            except Exception:
                raise Exception('update %s failed' % alarm_id)
        else:
            try:
                alarm = {
                    'type': 'threshold',
                    'alarm_id': alarm_id,
                    'name': alarm_id,
                    'enabled': True,
                    'description': '',
                    'evaluation-periods': 2,
                    'repeat_actions': True,
                    'alarm_actions': [],
                    'threshold_rule': {
                        'meter_name': METER_BALANCE,
                        'threshold': 60,
                        'statistic': 'avg',
                        'comparison_operator': 'lt',

                    },
                    'time_constraints': time_constraints
                }
                self.billcenter_client.create(**alarm)
            except Exception:
                raise Exception('create %s failed' % alarm_id)
        return body
