from testtools import matchers

from tempest.api.volume import base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test

CONF = config.CONF


class VolumesV2CreateTest(base.BaseVolumeTest):

    @classmethod
    def setup_clients(cls):
        super(VolumesV2CreateTest, cls).setup_clients()
        cls.client = cls.volumes_client

    @classmethod
    def resource_setup(cls):
        super(VolumesV2CreateTest, cls).resource_setup()

        cls.name_field = cls.special_fields['name_field']
        cls.descrip_field = cls.special_fields['descrip_field']

    def _delete_volume(self, volume_id):
        self.client.delete_volume(volume_id)
        self.client.wait_for_resource_deletion(volume_id)

    def _volume_create_show_delete(self, size=None, **kwargs):
        # Create a volume
        metadata = {'Type': 'Test'}
        # Create a volume
        kwargs['metadata'] = metadata
        volume = self.client.create_volume(size, **kwargs)
        self.assertIn('id', volume)
        self.addCleanup(self._delete_volume, volume['id'])
        self.client.wait_for_volume_status(volume['id'], 'available')
        self.assertIn(self.name_field, volume)
        self.assertEqual(volume[self.name_field], kwargs[self.name_field],
                         "The created volume name is not equal "
                         "to the requested name")
        self.assertTrue(volume['id'] is not None,
                        "Field volume id is empty or not found.")

        fetched_volume = self.client.show_volume(volume['id'])

        self.assertEqual(kwargs[self.name_field],
                         fetched_volume[self.name_field],
                         'The fetched Volume name is different '
                         'from the created Volume')
        self.assertEqual(volume['id'],
                         fetched_volume['id'],
                         'The fetched Volume id is different '
                         'from the created Volume')
        self.assertThat(fetched_volume['metadata'].items(),
                        matchers.ContainsAll(metadata.items()),
                        'The fetched Volume metadata misses data '
                        'from the created Volume')

        if 'imageRef' in kwargs:
            self.assertEqual('true', fetched_volume['bootable'])
        if 'imageRef' not in kwargs:
            self.assertEqual('false', fetched_volume['bootable'])

    @test.attr(type='')
    @test.idempotent_id('17bd3e2a-5ff5-4d06-871f-3936a173b488')
    def test_volume_create_show_delete_with_1gb_capacity(self):
        v_name = data_utils.rand_name('Volume')
        v_desc = data_utils.rand_name('description')
        kwargs = {self.name_field: v_name, self.descrip_field: v_desc}
        self._volume_create_show_delete(1, **kwargs)

    @test.attr(type='')
    @test.idempotent_id('fea2913b-f42b-4b49-8d4c-cdabc4937f10')
    def test_volume_create_show_delete_with_specific_character_name(self):
        v_name = '@#$%^test'
        v_desc = data_utils.rand_name('description')
        kwargs = {self.name_field: v_name, self.descrip_field: v_desc}
        self._volume_create_show_delete(10, **kwargs)

    @test.attr(type='')
    @test.idempotent_id('fea2913b-f42b-4b49-8d4c-cdabc4937f10')
    def test_volume_create_show_delete_with_name_none(self):
        # Test volume create when display_name is none and display_description
        # contains specific characters
        v_desc = '@#$%^test'
        kwargs = {self.descrip_field: v_desc}
        self._volume_create_show_delete(20, **kwargs)

    @test.attr(type='')
    @test.idempotent_id('a2100baa-2568-46ad-aaca-5f1a34ec1618')
    def test_volume_create_show_delete_from_image(self):
        image_id = CONF.compute.image_ref
        v_name = data_utils.rand_name('Volume')
        v_desc = data_utils.rand_name('description')
        kwargs = {'imageRef': image_id,
                  self.name_field: v_name, self.descrip_field: v_desc}
        self._volume_create_show_delete(1, **kwargs)


class VolumesV2CreateMaxTest(base.BaseVolumeTest):

    @classmethod
    def setup_clients(cls):
        super(VolumesV2CreateMaxTest, cls).setup_clients()
        cls.client = cls.volumes_client

    @classmethod
    def resource_setup(cls):
        super(VolumesV2CreateMaxTest, cls).resource_setup()

        cls.name_field = cls.special_fields['name_field']
        cls.descrip_field = cls.special_fields['descrip_field']

    def _delete_volume(self, volume_id):
        self.client.delete_volume(volume_id)
        self.client.wait_for_resource_deletion(volume_id)

    def _volume_create(self, size=None, **kwargs):
        # Create a volume
        metadata = {'Type': 'Test'}
        # Create a volume
        kwargs['metadata'] = metadata
        volume = self.client.create_volume(size, **kwargs)
        self.assertIn('id', volume)
        self.addCleanup(self._delete_volume, volume['id'])
        self.client.wait_for_volume_status(volume['id'], 'available')
        self.assertIn(self.name_field, volume)
        self.assertEqual(volume[self.name_field], kwargs[self.name_field],
                         "The created volume name is not equal "
                         "to the requested name")
        self.assertTrue(volume['id'] is not None,
                        "Field volume id is empty or not found.")

    @test.attr(type='')
    @test.idempotent_id('6be3fdd5-7e48-47c6-899d-2adf6a9e8cad')
    def test_create_volume_with_8tb_capacity(self):
        # Test volume create with max capacity
        v_name = data_utils.rand_name('Volume')
        v_desc = data_utils.rand_name('description')
        kwargs = {self.name_field: v_name, self.descrip_field: v_desc}
        self._volume_create(8192, **kwargs)
