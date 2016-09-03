

from oslo_log import log as logging
from tempest.common.utils import data_utils
from tempest import config
import tempest.test


CONF = config.CONF
LOG = logging.getLogger(__name__)


class SfBaseSfpoolTest(tempest.test.BaseTestCase):
    """Base test case class for all sfpool API tests."""

    # only set credentials, test.BaseTestCase.setup_credentials
    # will active 'os'
    credentials = ['primary']

    # must keep
    @classmethod
    def setup_credentials(cls):
        super(SfBaseSfpoolTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(SfBaseSfpoolTest, cls).setup_clients()
        cls.sfpool_client = cls.os.sfpool_client

    @classmethod
    def resource_setup(cls):
        super(SfBaseSfpoolTest, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(SfBaseSfpoolTest, cls).resource_cleanup()
