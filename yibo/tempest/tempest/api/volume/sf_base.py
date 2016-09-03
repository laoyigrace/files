import base
import time

from oslo_utils import timeutils

from tempest import config
from tempest import exceptions
from tempest.common.utils.linux import sf_remote_client

CONF = config.CONF


class BaseShareStorageTest(base.BaseVolumeTest):
    """Base test case class for iscsi and FC API tests."""
    credentials = ['primary', 'admin']
    _iscsi_ip = "200.200.114.42"
    _iscsi_port = "3260"
    _status = {"status": "creating"}
    _error_status = {"status": "error: server exist"}

    @classmethod
    def setup_clients(cls):
        super(BaseShareStorageTest, cls).setup_clients()
        cls.storage_client = cls.os_adm.storage_client

    @classmethod
    def resource_setup(cls):
        super(BaseShareStorageTest, cls).resource_setup()

        cls.iscsi_ips = []
        cls.storage = []

    @classmethod
    def resource_cleanup(cls):
        cls.clear_iscsi()
        super(BaseShareStorageTest, cls).resource_cleanup()

    @classmethod
    def clear_iscsi(cls):
        iscsi_ids = []
        for iscsi_ip in cls.iscsi_ips:
            iscsi_id = cls.get_iscsi_id(iscsi_ip)
            iscsi_ids.append(iscsi_id)

        for iscsi_id in iscsi_ids:
            try:
                cls.client.delete_iscsi_server(iscsi_id)
            except Exception:
                pass

        servers = cls.client.list_iscsi_server(detail=True)
        if not (len(servers) == 0):
            for server in servers:
                try:
                    # if server['iscsi_ip'] in cls.iscsi_ips:
                    cls.client.delete_iscsi_server(server['id'])
                    time.sleep(4)
                except Exception:
                    pass

    @classmethod
    def create_iscsi(cls, ip=None, port=3260):
        """Wrapper utility that returns a test iscsi."""

        cls.storage_client.add_iscsi_server(ip, port)

        # cls.iscsi_servers.append(iscsi_server)

    @classmethod
    def get_iscsi_id(cls, iscsi_ip=None):
        """get the specified iscsi server id."""
        iscsi_id = ""

        fetched_list = cls.storage_client.list_iscsi_server()

        # get the specified iscsi id
        for server in fetched_list:
            if server['iscsi_ip'] == iscsi_ip:
                iscsi_id = server['id']
                break
        return iscsi_id

    @classmethod
    def get_remote_client(cls):
        remote = sf_remote_client.SfRemoteClient(
            server=CONF.sf_common_info.ctl_host,
            username=CONF.sf_common_info.ctl_ssh_username,
            password=CONF.sf_common_info.ctl_ssh_password)
        return remote

    @classmethod
    def iscsi_target_discover(cls, iscsi_ip, iscsi_port="3260"):
        """
            iscsiadm --mode discoverydb -t sendtargets
                     -p 200.200.114.42:3260 --discover
        """

        # need to login in remote client to execute iscsi discovery command
        remote = cls.get_remote_client()
        cmd = 'iscsiadm --mode discoverydb --type sendtargets ' \
              '--portal %s:%s --discover' % (iscsi_ip, iscsi_port)

        out = remote.exec_command(cmd)
        out_list = out.split('\n')
        # pop the last blank element
        out_list.pop()

        return out_list

    @classmethod
    def find_hostname(cls):
        """
            cat /etc/hostname to find the host to mount
        """
        remote = cls.get_remote_client()
        cmd = 'cat /etc/hostname'

        out = remote.exec_command(cmd)
        return out

    @classmethod
    def get_disk_total_size(cls, disk_name):
        dev = '/dev/%s' % disk_name

        remote = cls.get_remote_client()
        disk_size = remote.exec_command('blockdev --getsize64 %s' % dev)
        disk_size = disk_size.split('\n')
        # pop the last blank element
        if disk_size[-1] == "":
            disk_size.pop()

        size = long(disk_size[0].strip())
        return size

    @classmethod
    def get_storage_id_by_holders(cls, holder):
        mapper_path = '/dev/mapper'
        remote = cls.get_remote_client()
        dm = remote.exec_command('ls -l %s' % mapper_path)
        dm_list = dm.split('\n')
        if dm_list[-1] == "":
            dm_list.pop()
        find_flag = 0
        storage_id = ""
        for index in range(len(dm_list)):
            if holder in dm_list[index]:
                disk_name = dm_list[index].split('/')[1]
                # to avoid find dm-N* when holders is dm-N
                if 0 == cmp(disk_name, holder):
                    find_flag = 1
                    storage_id = \
                        ' '.join(dm_list[index].split()).split(' ')[8]
                else:
                    continue
        return storage_id

    @classmethod
    def get_storage_ids(cls):
        """
        1.get target name by iscsiadm -m discovery
        2.get sdx through /dev/disk/by-path
        3.get holders on /sys/block/sdx/holders
        4.get wwid through /dev/mapper
        :return:disk wwid
        """

        targets = []
        disk_sdx = []
        storage_ids = []
        ret = cls.iscsi_target_discover(cls._iscsi_ip, cls._iscsi_port)
        for index in range(len(ret)):
            target_name = ret[index].split(' ')[1]
            targets.append(target_name)

        # sleep several seconds to ensure targets appear in by-path
        time.sleep(4)

        remote = cls.get_remote_client()
        scan_dir = "/dev/disk/by-path"
        out_disk = remote.exec_command('ls -l %s' % scan_dir)
        out_disk = out_disk.split('\n')
        # pop the last blank element
        if out_disk[-1] == "":
            out_disk.pop()

        # disk_sdx = [sde,sdf,sdg...]
        for disk in range(len(out_disk)):
            for target in targets:
                if target in out_disk[disk]:
                    disk_dir = '/dev/disk/by-path/%s' % \
                               out_disk[disk].split()[8]
                    out = remote.exec_command('ls -l %s' % disk_dir)
                    disk_name = out.split('\n')[0].split('/')[-1]
                    disk_sdx.append(disk_name)

        for sdx in disk_sdx:
            # disk size need minium 4GB
            total_size = cls.get_disk_total_size(sdx)
            if total_size > 4297064448:
                holders_dir = "/sys/block/%s/holders" % sdx
                holders = remote.exec_command('ls -l %s' % holders_dir)
                holder = holders.split('\n')
                if holder[-1] == "":
                    holder.pop()
                holder = holder[1].split()[8]
                storage_id = cls.get_storage_id_by_holders(holder)
                storage_ids.append(storage_id)
            else:
                continue
        return storage_ids

    @classmethod
    def await_target_storage(cls, targets, storage_flag=False):

        # number of targets and storage must be equal
        timeout = CONF.volume.list_iscsi_timeout
        start = timeutils.utcnow()
        while timeutils.delta_seconds(start, timeutils.utcnow()) < timeout:

            if storage_flag:
                storage_list = cls.client.list_iscsi_storage()
                if len(storage_list) == len(targets):
                    return storage_list
                time.sleep(CONF.volume.build_interval)
            else:
                target_list = cls.client.list_iscsi_target()

                if len(target_list) == len(targets):
                    return target_list
                time.sleep(CONF.volume.build_interval)

        raise exceptions.TimeoutException(
            'iscsi target has not been added to the '
            'database within %d seconds' % CONF.volume.list_iscsi_timeout)
