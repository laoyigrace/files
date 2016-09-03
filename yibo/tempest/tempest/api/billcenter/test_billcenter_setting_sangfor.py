from tempest_lib.common.utils import data_utils

from tempest.api.billcenter import base


class BillcenterChargeSettingTestJson(base.BaseBillcenterTest):

    def test_set_charge_setting(self):
        alarm_title = data_utils.rand_name(name='alarm-title')
        kwargs = {
            'alarm_title': alarm_title,
            'alarm_content': "tempest test",
            'alarm_count':  2,
            'alarm_time ':  "9:00",
            'invoice_threshold :':  100,
            'resource_threshold ': 100,
            'email_enabled ':  False,
            'msg_enabled': True,
            'sms_enabled': False

        }
        body = self.charge_setting(alarm_title, **kwargs)
        self.assertEqual(201, body.resp.status)



