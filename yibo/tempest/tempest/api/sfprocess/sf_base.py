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
from tempest_lib import exceptions as lib_exc

from tempest.common.utils import data_utils
from tempest import config
import tempest.test

CONF = config.CONF

LOG = logging.getLogger(__name__)


class SfBaseSfprocessTest(tempest.test.BaseTestCase):
    """Base test case class for all sfprocess API tests."""

    # only set credentials, test.BaseTestCase.setup_credentials
    # will active 'os'
    credentials = ['primary']

    # must keep
    @classmethod
    def setup_credentials(cls):
        super(SfBaseSfprocessTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(SfBaseSfprocessTest, cls).setup_clients()
        cls.sfprocess_client = cls.os.sfprocess_client

    @classmethod
    def resource_setup(cls):
        super(SfBaseSfprocessTest, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(SfBaseSfprocessTest, cls).resource_cleanup()
