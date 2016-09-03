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
from tempest.common.utils import data_utils
from tempest import test


class SfNotifyEmailCreateTest(sf_base.SfBaseSfNotifyTest):
    """testcase for sf-notify email-create api """

    @test.attr(type='smoke')
    @test.idempotent_id('8b1542cd-9221-4bd7-b3b9-23ec219725b0')
    def test_email_create_with_positional_args(self):
        email_addr = "43569@sangfor.com"
        email_host = "200.200.0.11"
        resp, body = self.create_email(email_addr=email_addr,
                                       email_host=email_host)

        self.assertEqual(resp["status"], "201")
        self.assertEqual(body["email_addr"], email_addr)
        self.assertEqual(body["email_host"], email_host)

    @test.attr(type='')
    @test.idempotent_id('7ecdcd54-4e46-465a-9330-be205eabe36e')
    def test_email_create_with_optionals_args(self):
        email_addr = data_utils.rand_name() + "@sangfor.com"
        email_host = data_utils.rand_name("host")
        email_user = data_utils.rand_name("user")
        email_password = data_utils.rand_name("password")

        self.create_email(email_addr=email_addr,
                          email_host=email_host,
                          email_user=email_user,
                          email_password=email_password)

        resp_get, body_get = self.sf_notify_email_client.email_get()
        
        output_data_1 = self.sf_encrypt(email_user)
        output_data_2 = self.sf_encrypt(email_password)
        self.assertEqual(body_get["email_user"], output_data_1)
        self.assertEqual(body_get["email_password"], output_data_2)


class SfNotifyEmailDeleteTest(sf_base.SfBaseSfNotifyTest):
    """testcase for sf-notify email-delete api """

    @test.attr(type='smoke')
    @test.idempotent_id('de64dd4b-2e5a-4a1b-b51a-d477621059d9')
    def test_email_delete(self):
        self.create_email()
        resp_delete = self.sf_notify_email_client.email_delete()
        resp_get, body_get = self.sf_notify_email_client.email_get()

        self.assertEqual(resp_delete[0]["status"], "204")
        self.assertIsNone(body_get)


class SfNotifyEmailGetTest(sf_base.SfBaseSfNotifyTest):
    """testcase for sf-notify email-get api """

    @test.attr(type='smoke')
    @test.idempotent_id('f13d5559-03cb-404b-8723-5cd8e2cfbb55')
    def test_email_get(self):
        resp_create, body_create = self.create_email()
        resp_get, body_get = self.sf_notify_email_client.email_get()

        self.assertEqual(resp_get["status"], "200")
        self.assertEqual(body_create["email_addr"], body_get["email_addr"])
        self.assertEqual(body_create["email_host"], body_get["email_host"])

    @test.attr(type='')
    @test.idempotent_id('8a24bca0-5848-4506-844f-175565efde7a')
    def test_email_get_none(self):
        # the email config doesn't exist
        self.sf_notify_email_client.email_delete()
        resp_get, body_get = self.sf_notify_email_client.email_get()
        self.assertIsNone(body_get)


class SfNotifyEmailUpdateTest(sf_base.SfBaseSfNotifyTest):
    """testcase for sf-notify email-update api """

    @test.attr(type='smoke')
    @test.idempotent_id('aa606b0c-5cc8-4078-a9be-414524d0e76e')
    def test_email_addr_update(self):
        resp_create, body_create = self.create_email()
        email_addr = 'test@sangfor.com'
        resp_update, body_update = self.update_email(email_addr=email_addr)

        self.assertIsNot(body_create["email_addr"], body_update["email_addr"])
        self.assertEqual(email_addr, body_update["email_addr"])

    @test.attr(type='')
    @test.idempotent_id('865902a0-cfb3-417f-895e-34813ecfe919')
    def test_email_username_update(self):
        resp_create, body_create = self.create_email()
        email_user = "%s" % data_utils.rand_name("user")
        resp_update, body_update = self.update_email(email_user=email_user)

        email_user_encrypt = self.sf_encrypt(email_user)
        self.assertIsNot(body_create["email_user"], body_update["email_user"])
        self.assertEqual(email_user_encrypt, body_update["email_user"])


class SfNotifyEmailSendTest(sf_base.SfBaseSfNotifyTest):
    """testcase for sf-notify email-send api """

    @test.attr(type='')
    @test.idempotent_id('dba58402-9879-41d4-a2b5-b10145f64bf8')
    def test_email_send(self):
        self.enable_email()
        self.create_email()

        tomail_list = '43569@sangfor.com'
        sub = "sangfor"
        msg = "from cpt"

        resp = self.send_email(tomail_list=tomail_list, sub=sub, msg=msg)
        self.assertEqual(resp["status"], "204")
