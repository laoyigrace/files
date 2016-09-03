
import time
from oslo_log import log as logging
from tempest import config
from tempest import exceptions
from tempest import test
from tempest.common import waiters
from tempest.sf_scenario import sf_manager

CONF = config.CONF
LOG = logging.getLogger(__name__)

class TestVhdCreate(sf_manager.SfScenarioTest):

    credentials = ['primary', 'admin']

    def _create_by_type(self, volume_type, capacity=10):
        kwargs = {}
        kwargs['volume_type'] = volume_type
        volume = self.volumes_client.create_volume(capacity, **kwargs)
        self.assertIn('id', volume)
        self.addCleanup(self.volumes_client.delete_volume, volume['id'])
        self.volumes_client.wait_for_volume_status(volume['id'], 'available')
        return volume

    def _expand_volume(self, volume_id, capacity=20):
        self.volumes_client.extend_volume(volume_id, capacity)
        self.volumes_client.wait_for_volume_status(volume_id, 'available')
        return

    def _get_backend_name(self, volume_id):
        show = self.os_adm.volumes_client.show_volume(volume_id)
        self.assertIn('os-vol-host-attr:host', show)
        return show['os-vol-host-attr:host']

    def _check_size(self, volume_id, capacity=10):
        show = self.os_adm.volumes_client.show_volume(volume_id)
        self.assertIn('size', show)
        self.assertEqual(show['size'], capacity)

    def _do_test_create(self, volume_type, backend_substr):
        """ test if low-speed disks are created in corresponding storage """
        print("YJZ: BEGIN")

        print("YJZ: create volume: %s" % volume_type)
        volume = self._create_by_type(volume_type)
        print("volume:", volume)
        self.assertTrue(volume)

        print("YJZ: get backend name")
        backend = self._get_backend_name(volume['id'])
        print("backend:", backend)
        self.assertTrue(backend)

        print("YJZ: verify backend name")
        result = backend.find(backend_substr)
        print("result:", result)
        self.assertTrue(result > -1)

        print("YJZ: verify volume size")
        self._check_size(volume['id'])

        print("YJZ: PASS")
        return

    def test_create_high_speed(self):
        self._do_test_create("high-speed", "high_speed")

    def test_create_low_speed(self):
        self._do_test_create("low-speed", "low_speed")

    def _do_test_expand(self, volume_type, backend_substr):
        """ test if low-speed disks are created in corresponding storage """
        print("YJZ: BEGIN")

        print("YJZ: create volume: %s" % volume_type)
        volume = self._create_by_type(volume_type, 10)
        print("volume:", volume)
        self.assertTrue(volume)

        print("YJZ: get backend name")
        backend = self._get_backend_name(volume['id'])
        print("backend:", backend)
        self.assertTrue(backend)

        print("YJZ: verify backend name")
        result = backend.find(backend_substr)
        print("result:", result)
        self.assertTrue(result > -1)

        print("YJZ: verify volume size == 10")
        self._check_size(volume['id'], 10)

        print("YJZ: expand volume")
        self._expand_volume(volume['id'], 20)

        print("YJZ: verify volume size == 20")
        self._check_size(volume['id'], 20)

        print("YJZ: PASS")
        return

    def test_expand_high_speed(self):
        self._do_test_expand("high-speed", "high_speed")

    def test_expand_low_speed(self):
        self._do_test_expand("low-speed", "low_speed")

