import operator

from oslo_log import log as logging
from testtools import matchers

from tempest.api.volume import base
from tempest.common.utils import data_utils
from tempest import test

LOG = logging.getLogger(__name__)


class VolumesV2ListTestJSON(base.BaseVolumeTest):

    """
    This test creates a number of 1G volumes. To run successfully,
    ensure that the backing file for the volume group that Nova uses
    has space for at least 3 1G volumes!
    If you are running a Devstack environment, ensure that the
    VOLUME_BACKING_FILE_SIZE is at least 4G in your localrc
    """

    VOLUME_FIELDS = ('id', 'name')

    def assertVolumesIn(self, fetched_list, expected_list, fields=None):
        if fields:
            expected_list = map(operator.itemgetter(*fields), expected_list)
            fetched_list = map(operator.itemgetter(*fields), fetched_list)

        missing_vols = [v for v in expected_list if v not in fetched_list]
        if len(missing_vols) == 0:
            return

        def str_vol(vol):
            return "%s:%s" % (vol['id'], vol[self.name])

        raw_msg = "Could not find volumes %s in expected list %s; fetched %s"
        self.fail(raw_msg % ([str_vol(v) for v in missing_vols],
                             [str_vol(v) for v in expected_list],
                             [str_vol(v) for v in fetched_list]))

    @classmethod
    def setup_clients(cls):
        super(VolumesV2ListTestJSON, cls).setup_clients()
        cls.client = cls.volumes_client

    @classmethod
    def resource_setup(cls):
        super(VolumesV2ListTestJSON, cls).resource_setup()
        cls.name = cls.VOLUME_FIELDS[1]

        # Create 3 test volumes
        cls.volume_list = []
        cls.volume_id_list = []
        cls.metadata = {'Type': 'work'}
        for i in range(3):
            volume = cls.create_volume(metadata=cls.metadata)
            volume = cls.client.show_volume(volume['id'])
            cls.volume_list.append(volume)
            cls.volume_id_list.append(volume['id'])

    @classmethod
    def resource_cleanup(cls):
        # Delete the created volumes
        for volid in cls.volume_id_list:
            cls.client.delete_volume(volid)
            cls.client.wait_for_resource_deletion(volid)
        super(VolumesV2ListTestJSON, cls).resource_cleanup()

    def _list_by_param_value_and_assert(self, params, with_detail=False):
        """
        Perform list or list_details action with given params
        and validates result.
        """
        if with_detail:
            fetched_vol_list = \
                self.client.list_volumes(detail=True, params=params)
        else:
            fetched_vol_list = self.client.list_volumes(params=params)

        # Validating params of fetched volumes
        # In v2, only list detail view includes items in params.
        # In v1, list view and list detail view are same. So the
        # following check should be run when 'with_detail' is True
        # or v1 tests.
        if with_detail or self._api_version == 1:
            for volume in fetched_vol_list:
                for key in params:
                    msg = "Failed to list volumes %s by %s" % \
                          ('details' if with_detail else '', key)
                    if key == 'metadata':
                        self.assertThat(
                            volume[key].items(),
                            matchers.ContainsAll(params[key].items()),
                            msg)
                    else:
                        self.assertEqual(params[key], volume[key], msg)

    @test.attr(type='')
    @test.idempotent_id('4e065cbe-df2c-4f6d-bb89-3a7b06efd472')
    def test_volume_list(self):
        # Get a list of Volumes
        # Fetch all volumes
        fetched_list = self.client.list_volumes()
        self.assertVolumesIn(fetched_list, self.volume_list,
                             fields=self.VOLUME_FIELDS)

    @test.attr(type='')
    @test.idempotent_id('50312bca-4287-4f8f-8784-6916677508d8')
    def test_volume_list_with_details(self):
        # Get a list of Volumes with details
        # Fetch all Volumes
        fetched_list = self.client.list_volumes(detail=True)
        self.assertVolumesIn(fetched_list, self.volume_list)

    @test.idempotent_id('c87f4db8-4865-4192-ad2b-380596280e12')
    def test_volume_list_by_name(self):
        volume = self.volume_list[data_utils.rand_int_id(0, 2)]
        params = {self.name: volume[self.name]}
        fetched_vol = self.client.list_volumes(params=params)
        self.assertEqual(1, len(fetched_vol), str(fetched_vol))
        self.assertEqual(fetched_vol[0][self.name],
                         volume[self.name])

    @test.idempotent_id('76789e0f-c96e-429a-93ea-9bf52605a478')
    def test_volume_list_details_by_name(self):
        volume = self.volume_list[data_utils.rand_int_id(0, 2)]
        params = {self.name: volume[self.name]}
        fetched_vol = self.client.list_volumes(detail=True, params=params)
        self.assertEqual(1, len(fetched_vol), str(fetched_vol))
        self.assertEqual(fetched_vol[0][self.name],
                         volume[self.name])

    @test.idempotent_id('51fec71d-f934-4649-827a-1a5527fce86b')
    def test_volumes_list_by_status(self):
        params = {'status': 'available'}
        fetched_list = self.client.list_volumes(params=params)
        self._list_by_param_value_and_assert(params)
        self.assertVolumesIn(fetched_list, self.volume_list,
                             fields=self.VOLUME_FIELDS)

    @test.idempotent_id('2d9e9e89-ed47-4891-93e3-5896a5319109')
    def test_volume_list_param_display_name_and_status(self):
        # Test to list volume when display name and status param is given
        volume = self.volume_list[data_utils.rand_int_id(0, 2)]
        params = {self.name: volume[self.name],
                  'status': 'available'}
        self._list_by_param_value_and_assert(params)


