# -*- coding:utf-8 -*-
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

from tempest.api.sf_notify import sf_base
from tempest import test


class SfNotifySmsTest(sf_base.SfBaseSfNotifyTest):
    """ sf-notify sms API test"""

    @test.attr(type="smoke")
    @test.idempotent_id("2da2008f-8367-11e5-8ea3-00e06665338b")
    def test_sms_create(self):
        phone_number = '15120073460'
        message = "test short message service"

        section = "SP_CONFIG"
        option = "ENABLE"
        value = 1
        cfg = {section: {option: value}}
        self.sf_notify_sms_client.sms_config_set(cfg)

        body = self.sf_notify_sms_client.sms_create(phone_number, message)
        self.assertEqual(201, body.response.status)
        self.assertEqual(phone_number, body['phone'])
        self.assertEqual(message, body['sms'])

    @test.attr(type="smoke")
    @test.idempotent_id("3a72a44f-8367-11e5-a09c-00e06665338b")
    def test_sms_config_get(self):
        section = "SP_CONFIG"
        option = "SMG_TYPE"
        value = "MODEM"
        cfg = {section: {option: value, 'SMG_URL': 'http://www.ex.com'}}
        self.sf_notify_sms_client.sms_config_set(cfg)
        body = self.sf_notify_sms_client.sms_config_get()
        self.assertDictContainsSubset(cfg[section],
                                      eval(body['config'])["SP_CONFIG"])
        self.assertEqual(value, eval(body["config"])["SP_CONFIG"]["SMG_TYPE"])

    @test.attr(type="smoke")
    @test.idempotent_id("44e88f30-8367-11e5-9832-00e06665338b")
    def test_sms_config_set(self):
        section = "MODEM"
        option = "MODEM_TYPE"
        value = "SERIAL"
        cfg = {section: {option: value}}
        body = self.sf_notify_sms_client.sms_config_set(cfg)
        self.assertEqual(201, body.response.status)
        self.assertDictContainsSubset(cfg[section],
                                      eval(body["config"])["MODEM"])
