import base64
import logging

from tempest.api.compute import sf_base
from tempest.common.utils import data_utils
# from tempest.common.utils.linux import remote_client
from tempest.common.utils.linux import sf_remote_client
from tempest.common import waiters
from tempest import config
from tempest import test

CONF = config.CONF

LOG = logging.getLogger(__name__)


class SfServerActionsTestJSON(sf_base.SfBaseV2ComputeTest):
    run_ssh = CONF.validation.run_validation

    @classmethod
    def setup_clients(cls):
        super(SfServerActionsTestJSON, cls).setup_clients()
        cls.client = cls.servers_client

    @classmethod
    def resource_setup(cls):
        # cls.set_validation_resources()

        super(SfServerActionsTestJSON, cls).resource_setup()

    def _test_reboot_server(self, reboot_type, server):
        # Get the time the server was last rebooted,
        if CONF.compute.ssh_run:
            self.ssh_validation()

            linux_client = sf_remote_client.SfRemoteClient(
                self.floating_ip,
                self.ssh_user,
                self.ssh_password,
                )

            boot_time = linux_client.get_boot_time()

        self.client.reboot(server['id'], reboot_type)
        waiters.wait_for_server_status(self.client, server['id'], 'ACTIVE')

        if CONF.compute.ssh_run:
            # Log in and verify the boot time has changed
            linux_client = sf_remote_client.SfRemoteClient(
                self.floating_ip,
                self.ssh_user,
                self.ssh_password,
                )

            new_boot_time = linux_client.get_boot_time()

            self.assertTrue(new_boot_time > boot_time,
                            '%s > %s' % (new_boot_time, boot_time))

    @test.attr(type='smoke')
    @test.idempotent_id('ac8330b4-d476-44c6-b164-3e17ee94a6b3')
    def test_reboot_server_hard(self):
        server = self.create_sf_server()
        # The server should be power cycled
        self._test_reboot_server('HARD', server)

    @test.attr(type='smoke')
    @test.idempotent_id('87e415eb-80c1-4a65-82d4-856d88d80b20')
    def test_force_stop_server(self):
        server = self.create_sf_server()

        self.client.sf_force_stop(server['id'])
        waiters.wait_for_server_status(self.client, server['id'], 'SHUTOFF')
