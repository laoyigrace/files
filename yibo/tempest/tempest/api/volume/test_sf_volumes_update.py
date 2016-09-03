from testtools import matchers

from tempest.api.volume import base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test


class VolumesV2UpdateTest(base.BaseVolumeTest):

    @classmethod
    def setup_clients(cls):
        super(VolumesV2UpdateTest, cls).setup_clients()
        cls.client = cls.volumes_client

    @classmethod
    def resource_setup(cls):
        super(VolumesV2UpdateTest, cls).resource_setup()

        cls.name_field = cls.special_fields['name_field']
        cls.descrip_field = cls.special_fields['descrip_field']

    def _delete_volume(self, volume_id):
        self.client.delete_volume(volume_id)
        self.client.wait_for_resource_deletion(volume_id)

    def _volume_create(self, **kwargs):
        # Create a volume, Get it's details and Delete the volume
        volume = {}
        self.v_name = data_utils.rand_name('Volume')
        self.desc = 'description of volume'
        metadata = {'Type': 'Test'}
        # Create a volume
        kwargs[self.name_field] = self.v_name
        kwargs[self.descrip_field] = self.desc
        kwargs['metadata'] = metadata
        volume = self.client.create_volume(**kwargs)
        self.addCleanup(self._delete_volume, volume['id'])
        self.client.wait_for_volume_status(volume['id'], 'available')
        return volume

    @test.attr(type='smoke')
    @test.idempotent_id('1d3e1bdb-3825-477a-b651-a99d725e413e')
    def test_volume_update(self):
        volume = self._volume_create()

        # Test volume update
        new_v_name = data_utils.rand_name('new-Volume')
        new_desc = 'This is the new description of volume'
        params = {self.name_field: new_v_name,
                  self.descrip_field: new_desc}
        update_volume = self.client.update_volume(volume['id'], **params)
        # Assert response body for update_volume method
        self.assertNotEqual(new_v_name, volume[self.name_field])
        self.assertNotEqual(new_desc, volume[self.descrip_field])
        self.assertEqual(new_v_name, update_volume[self.name_field])
        self.assertEqual(new_desc, update_volume[self.descrip_field])

    @test.attr(type='smoke')
    @test.idempotent_id('020d3e4e-88b5-4489-917e-856cbc032139')
    def test_volume_update_with_specific_character_name(self):
        volume = self._volume_create()

        # Test volume name update specific characters
        new_v_name = data_utils.rand_name('@#$%^')
        params = {self.name_field: new_v_name}
        update_volume = self.client.update_volume(volume['id'], **params)
        # Assert response body for update_volume method
        self.assertNotEqual(new_v_name, volume[self.name_field])
        self.assertEqual(new_v_name, update_volume[self.name_field])

    @test.attr(type='smoke')
    @test.idempotent_id('e6fe35d9-c183-44b0-b8c3-35aeff89190f')
    def test_volume_update_with_none_desc(self):
        volume = self._volume_create()

        # Test volume description none
        new_desc = None
        params = {self.descrip_field: new_desc}
        update_volume = self.client.update_volume(volume['id'], **params)
        # Assert response body for update_volume method
        self.assertEqual(volume[self.name_field],
                         update_volume[self.name_field])
        self.assertIsNone(update_volume[self.descrip_field])






