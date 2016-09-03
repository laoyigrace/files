# -*- coding:utf-8 -*-
# Copyright 2015 Sangfor Technologies Co., Ltd
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

from testtools import matchers
from tempest.api.vsan import base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test
import random
import time
import datetime

CONF = config.CONF

class VsanCreateTest(base.BaseVsanTest):
    """test cases for vsan create api """
    @classmethod
    def setup_clients(cls):
        super(VsanCreateTest, cls).setup_clients()
        cls.client = cls.vsan_client
        cls.vsan_client.resource_setup()

    def _delete_vsan_cluster(self, cluster_id):
        self.vsan_client.delete_vsan_cluster(cluster_id)
        self.vsan_client.wait_for_resource_deletion(cluster_id)

    def _vsan_clsuter_create_get_update_delete(self, **kwargs):
        cluster_hosts = CONF.vs.cluster_hosts
        hosts_lists = ''
        for h in cluster_hosts:
            hosts_lists = hosts_lists + h + ','
        hosts_lists = hosts_lists.rstrip(',')

        display_description = 'test for create vsan cluster'
        display_name = 'Vs-Test'
        creating = 'creating'

        kwargs['cluster_hosts'] = hosts_lists
        kwargs['display_description'] = display_description
        kwargs['display_name'] = display_name
        kwargs['status'] = creating
        kwargs['project_id'] = None
        # Create cluster
        cluster = self.vsan_client.create_vsan_cluster(**kwargs)
        self.assertIn('id', cluster)
        # by hct:addClean will delete the cluster after case ends
        self.addCleanup(self._delete_vsan_cluster, cluster['id'])
        self.client.wait_for_vsan_cluster_status(cluster['id'], 'creating')

        self.assertIn('description', cluster)
        self.assertIn('name', cluster)
        self.assertEqual('creating', cluster['status'],
                         'Field status is not creating')
        self.assertTrue(cluster['id'] is not None,
                        "Field cluster_id is empty or not found.")
        # create vsan cluster id
        cluster_id = cluster['id']
        # Show cluster
        fetched_vsan_cluster = self.vsan_client.show_vsan_cluster(cluster['id'])
        self.assertEqual(creating, fetched_vsan_cluster['status'],
                         'The fetched Vsan cluster status is different '
                         'from the created Vsan cluster')
        self.assertEqual(display_name, fetched_vsan_cluster['name'],
                         'The fetched Vsan cluster name is different '
                         'from the created Vsan cluster')
        self.assertEqual(display_description, fetched_vsan_cluster['description'],
                         'The fetched Vsan cluster description is different '
                         'from the created Vsan cluster')
        self.assertEqual(cluster['id'], fetched_vsan_cluster['id'],
                         'The fetched Vsan cluster id is different '
                         'from the created Vsan cluster')
        self.assertEqual(len(cluster_hosts), fetched_vsan_cluster['total_servers'],
                         'The fetched Vsan cluster total_servers is different '
                         'from the created Vsan cluster')

        # Update cluster
        # Test vsan cluster update when display_name is same with original value
        # @hct: here is a bug for hht ui-level user display_name ,but backend use name
        params = {'display_name':'tempest'}
        update_cluster = self.vsan_client.update_vsan_cluster(cluster['id'], **params)
        self.client.wait_for_vsan_cluster_status(cluster['id'], 'creating')
        # assert:name description
        self.assertEqual(params['display_name'], update_cluster['name'])
        self.assertEqual(display_description, update_cluster['description'])
        # Test vsan cluster  update when name is new value
        new_v_name = data_utils.rand_name('new-Vs-Test')
        new_desc = 'new dec test for create vsan cluster'
        # @hct: here is a bug for hht ui-level user display_name ,but backend use name
        params = {'display_name': new_v_name,
                  'display_description': new_desc}
        update_cluster = self.vsan_client.update_vsan_cluster(cluster['id'], **params)
        self.client.wait_for_vsan_cluster_status(cluster['id'], 'creating')
        # Assert response body
        self.assertEqual(new_v_name, update_cluster['name'])
        self.assertEqual(new_desc, update_cluster['description'])
        # Assert response body for show_volume method
        updated_cluster = self.vsan_client.show_vsan_cluster(cluster['id'])
        self.assertEqual(cluster['id'], updated_cluster['id'])
        self.assertEqual(new_v_name, updated_cluster['name'])
        self.assertEqual(new_desc, updated_cluster['description'])

    @test.idempotent_id('9d8b9a28-a3c2-4053-8413-31d96730bf00')
    def test_vsan_cluster_create_show_update_delete(self):
        self._vsan_clsuter_create_get_update_delete()

    def _test_vsan_cluster_init_delete(self, **kwargs):
        cluster_hosts = CONF.vs.cluster_hosts
        replica_num = CONF.vs.replica_num
        hosts_lists = ''
        for h in cluster_hosts:
            hosts_lists = hosts_lists + h + ','
        hosts_lists = hosts_lists.rstrip(',')

        display_description = 'test for create vsan cluster'
        display_name = 'Vs-Test'
        creating = 'creating'

        kwargs['cluster_hosts'] = hosts_lists
        kwargs['display_description'] = display_description
        kwargs['display_name'] = display_name
        kwargs['status'] = creating
        kwargs['project_id'] = None
        # Create cluster
        cluster = self.vsan_client.create_vsan_cluster(**kwargs)
        self.assertIn('id', cluster)
        cluster_id = cluster['id']
        self.addCleanup(self._delete_vsan_cluster, cluster_id)

        disks = cluster['disks']
        servers = {}
        usable_disk_num = 0
        for disk in disks:
            sn = disk['vs_sname']
            if sn not in servers:
                servers[sn] = []
            server =  servers[sn]
            if disk['storage_type'] == 'STORAGE_NONE':
                server.append(disk)
                usable_disk_num += 1

        self.assertTrue(usable_disk_num >= replica_num,
                        "usable disk num less then replica_num, can not init.")

        max_disks_num = 0
        for sn , disks in servers.items():
            if len(disks) > max_disks_num:
                max_disks_num = len(disks)

        init_cfg = {}
        init_cfg['replica'] = replica_num
        init_cfg['hosts'] = []
        used_disk_num = 0

        def _find_idx(k, v, arr):
            for i in range(0, len(arr)):
                if arr[i][k] == v:
                    return i
            return -1

        disk_idx = 0
        while disk_idx < max_disks_num and used_disk_num < replica_num:
            for sn , disks in servers.items():
                if used_disk_num >= replica_num:
                    break
                if len(disks) <= disk_idx:
                    continue
                cfg_idx = _find_idx('host_name', sn, init_cfg['hosts'])
                if cfg_idx == -1:
                    newhost = {'host_name': sn, 'data':[{'disk': disks[disk_idx]['disk_id'],
                                                         'storage_type':'STORAGE_DATA'}]}
                    init_cfg['hosts'].append(newhost)
                else:
                    init_cfg['hosts'][cfg_idx]['data'].append({"disk":disks[disk_idx]['disk_id'],
                                                               "storage_type":"STORAGE_DATA"})
                used_disk_num += 1
            disk_idx += 1

        display_name = 'n_init_test'
        display_description = 'd_init_test'
        node_type = 'compute_xx'
        self.vsan_client.init_vsan_cluster(cluster_id, init_cfg, node_type,
                                           display_name=display_name,
                                           display_description=display_description)
        self.client.wait_for_vsan_cluster_status(cluster_id, 'available')

        clster = self.vsan_client.show_vsan_cluster(cluster_id)
        self.assertEqual('available', clster['status'],
                         'The fetched Vsan cluster status is different '
                         'from the created Vsan cluster')
        self.assertEqual(display_name, clster['name'],
                         'The fetched Vsan cluster name is different '
                         'from the created Vsan cluster')
        self.assertEqual(display_description, clster['description'],
                         'The fetched Vsan cluster description is different '
                         'from the created Vsan cluster')
        self.assertEqual(cluster_id, clster['id'],
                         'The fetched Vsan cluster id is different '
                         'from the created Vsan cluster')
        self.assertEqual(replica_num, int(clster['replication']),
                         'The fetched Vsan cluster replica_num is different '
                         'from the created Vsan cluster')
        self.assertEqual(node_type, clster['node_type'],
                         'The fetched Vsan cluster node_type is different '
                         'from the created Vsan cluster')
        capacity = clster['capacity']
        self.assertEqual(capacity['used_size'] + capacity['avail_size'], capacity['total_size'],
                         'The fetched Vsan cluster size is error '
                         'from the created Vsan cluster')
        self.assertGreater(capacity['total_size'], 0,
                         'The fetched Vsan cluster total_size is error '
                         'from the created Vsan cluster')

        servers = clster['servers']
        cluster_nodes = []
        for serv in servers:
            self.assertEqual(True, serv['is_in_cls'],
                         'The fetched Vsan cluster is_in_cls is different '
                         'from the created Vsan cluster')
            cluster_nodes.append(serv["cp_sname"])

        cluster_nodes_sort = sorted(cluster_nodes)
        cluster_hosts_sort = sorted(cluster_hosts)
        self.assertEqual(cluster_nodes_sort, cluster_hosts_sort,
                         'The fetched Vsan cluster cluster_nodes is different '
                         'from the created Vsan cluster')

        disks = clster['disks']
        vs_disks = {}
        init_disks = {}
        for disk in disks:
            if disk['storage_type'] == 'STORAGE_DATA':
                vs_disks[disk['disk_id']] = disk['vs_sname']

        for host in init_cfg['hosts']:
            for init_disk in host['data']:
                init_disks[init_disk['disk']] = host['host_name']

        self.assertEqual(init_disks, vs_disks,
                         'The fetched Vsan cluster disks is different '
                         'from the created Vsan cluster')

        self.assertEqual(len(vs_disks), replica_num,
                         'The fetched Vsan cluster data disks num is different '
                         'from the created Vsan cluster')

    # Test init
    @test.idempotent_id('3bdae13b-29f3-44c9-8c5c-72b92fcdcbc4')
    def test_vsan_cluster_init_delete(self):
        self._test_vsan_cluster_init_delete()

    def _test_vsan_cluster_replace_disk(self, **kwargs):
        cluster_hosts = CONF.vs.cluster_hosts
        replica_num = CONF.vs.replica_num
        hosts_lists = ''
        for h in cluster_hosts:
            hosts_lists = hosts_lists + h + ','
        hosts_lists = hosts_lists.rstrip(',')

        display_description = 'test for create vsan cluster'
        display_name = 'Vs-Test'
        creating = 'creating'

        kwargs['cluster_hosts'] = hosts_lists
        kwargs['display_description'] = display_description
        kwargs['display_name'] = display_name
        kwargs['status'] = creating
        kwargs['project_id'] = None
        # Create cluster
        cluster = self.vsan_client.create_vsan_cluster(**kwargs)
        self.assertIn('id', cluster)
        cluster_id = cluster['id']
        self.addCleanup(self._delete_vsan_cluster, cluster_id)

        disks = cluster['disks']
        servers = {}
        usable_disk_num = 0
        for disk in disks:
            sn = disk['vs_sname']
            if sn not in servers:
                servers[sn] = []
            server =  servers[sn]
            if disk['storage_type'] == 'STORAGE_NONE':
                server.append(disk)
                usable_disk_num += 1

        self.assertTrue(usable_disk_num >= replica_num + 1,
                        "usable disk num less then replica_num + 1, can not replace disk.")

        max_disks_num = 0
        for sn , disks in servers.items():
            if len(disks) > max_disks_num:
                max_disks_num = len(disks)

        init_cfg = {}
        init_cfg['replica'] = replica_num
        init_cfg['hosts'] = []
        used_disk_num = 0

        def _find_idx(k, v, arr):
            for i in range(0, len(arr)):
                if arr[i][k] == v:
                    return i
            return -1

        disk_idx = 0
        while disk_idx < max_disks_num and used_disk_num < replica_num:
            for sn , disks in servers.items():
                if used_disk_num >= replica_num:
                    break
                if len(disks) <= disk_idx:
                    continue
                cfg_idx = _find_idx('host_name', sn, init_cfg['hosts'])
                if cfg_idx == -1:
                    newhost = {'host_name': sn, 'data':[{'disk': disks[disk_idx]['disk_id'],
                                                         'storage_type':'STORAGE_DATA'}]}
                    init_cfg['hosts'].append(newhost)
                else:
                    init_cfg['hosts'][cfg_idx]['data'].append({"disk":disks[disk_idx]['disk_id'],
                                                               "storage_type":"STORAGE_DATA"})
                used_disk_num += 1
            disk_idx += 1

        display_name = 'n_replace_disk_test'
        display_description = 'd_replace_disk_test'
        self.vsan_client.init_vsan_cluster(cluster_id, init_cfg, 'network',
                                           display_name=display_name,
                                           display_description=display_description)
        self.client.wait_for_vsan_cluster_status(cluster_id, 'available')
        clster = self.vsan_client.show_vsan_cluster(cluster_id)
        disks = clster['disks']

        servs = {}
        for disk in disks:
            sn = disk['vs_sname']
            if sn not in servs:
                servs[sn] = []
            server =  servs[sn]
            server.append(disk)

        replace_serv = None
        oldDisk = None
        newDisk = None
        for sn, disks in servs.items():
            for disk in disks:
                if oldDisk == None and disk['storage_type'] == 'STORAGE_DATA':
                    oldDisk = disk['disk_id']
                if newDisk == None and disk['storage_type'] == 'STORAGE_NONE':
                    newDisk = disk['disk_id']
            if oldDisk != None and newDisk != None:
                replace_serv = sn
                break

            oldDisk = None
            newDisk = None

        self.assertNotEqual(replace_serv , None,
                        "do not hava None disk to replace, can not replace disk.")

        self.vsan_client.replace_disk(cluster_id, replace_serv, oldDisk, replace_serv, newDisk)
        time.sleep(3)
        self.client.wait_for_vsan_cluster_status(cluster_id, 'available')
        clster = self.vsan_client.show_vsan_cluster(cluster_id)
        disks = clster['disks']
        for disk in disks:
            if disk['disk_id'] == oldDisk:
                self.assertEqual('STORAGE_NONE' , disk['storage_type'],
                        "old disk 's storage_type is not STORAGE_NONE, replace disk failed.")
            if disk['disk_id'] == newDisk:
                self.assertEqual('STORAGE_DATA' , disk['storage_type'],
                        "new disk 's storage_type is not STORAGE_DATA, replace disk failed.")

    # Test replace disk
    @test.idempotent_id('41b64b9d-c449-4bbe-81a7-6915c9c6bbf9')
    def test_vsan_cluster_replace_disk(self):
        self._test_vsan_cluster_replace_disk()

    def _test_vsan_cluster_expand(self, **kwargs):
        cluster_hosts = CONF.vs.cluster_hosts
        replica_num = CONF.vs.replica_num
        hosts_lists = ''
        for h in cluster_hosts:
            hosts_lists = hosts_lists + h + ','
        hosts_lists = hosts_lists.rstrip(',')

        display_description = 'test for create vsan cluster'
        display_name = 'Vs-Test'
        creating = 'creating'

        kwargs['cluster_hosts'] = hosts_lists
        kwargs['display_description'] = display_description
        kwargs['display_name'] = display_name
        kwargs['status'] = creating
        kwargs['project_id'] = None
        # Create cluster
        cluster = self.vsan_client.create_vsan_cluster(**kwargs)
        self.assertIn('id', cluster)
        cluster_id = cluster['id']
        self.addCleanup(self._delete_vsan_cluster, cluster_id)

        disks = cluster['disks']
        servers = {}
        usable_disk_num = 0
        for disk in disks:
            sn = disk['vs_sname']
            if sn not in servers:
                servers[sn] = []
            server =  servers[sn]
            if disk['storage_type'] == 'STORAGE_NONE':
                server.append(disk)
                usable_disk_num += 1

        max_disks_num = 0
        for sn , disks in servers.items():
            if len(disks) > max_disks_num:
                max_disks_num = len(disks)

        init_cfg = {}
        init_cfg['replica'] = replica_num
        init_cfg['hosts'] = []
        used_disk_num = 0

        def _find_idx(k, v, arr):
            for i in range(0, len(arr)):
                if arr[i][k] == v:
                    return i
            return -1

        disk_idx = 0
        while disk_idx < max_disks_num and used_disk_num < replica_num:
            for sn , disks in servers.items():
                if used_disk_num >= replica_num:
                    break
                if len(disks) <= disk_idx:
                    continue
                cfg_idx = _find_idx('host_name', sn, init_cfg['hosts'])
                if cfg_idx == -1:
                    newhost = {'host_name': sn, 'data':[{'disk': disks[disk_idx]['disk_id'],
                                                         'storage_type':'STORAGE_DATA'}]}
                    init_cfg['hosts'].append(newhost)
                else:
                    init_cfg['hosts'][cfg_idx]['data'].append({"disk":disks[disk_idx]['disk_id'],
                                                               "storage_type":"STORAGE_DATA"})
                used_disk_num += 1
            disk_idx += 1

        display_name = 'n_expand_test'
        display_description = 'd_expand_test'
        self.vsan_client.init_vsan_cluster(cluster_id, init_cfg, 'compute',
                                           display_name=display_name,
                                           display_description=display_description)

        self.client.wait_for_vsan_cluster_status(cluster_id, 'available')
        cluster_init = self.vsan_client.show_vsan_cluster(cluster_id)
        capacity = cluster_init['capacity']
        old_total_size = capacity['total_size']

        expand_host = CONF.vs.expand_hosts[0]
        cluster_ehst = self.vsan_client.expand_vsan_cluster_hosts(cluster_id, expand_host)
        cluster_ehst = cluster_ehst['cluster']
        servs = cluster_ehst['servers']
        cp_snames = []
        for serv in servs:
            cp_snames.append(serv['cp_sname'])
            if serv['cp_sname'] == expand_host:
                self.assertEqual(False, serv['is_in_cls'],
                         'The fetched Vsan cluster is_in_cls is different True')

        init_exp_hosts = []
        init_exp_hosts.append(expand_host)
        init_exp_hosts = init_exp_hosts + cluster_hosts

        self.assertEqual(sorted(init_exp_hosts), sorted(cp_snames),
                      'The init and expand hosts not eaual Vsan cluster servers, expand hosts failed')

        disks = cluster_ehst['disks']
        servers = {}
        usable_disk_num = 0
        for disk in disks:
            sn = disk['vs_sname']
            if sn not in servers:
                servers[sn] = []
            server =  servers[sn]
            if disk['storage_type'] == 'STORAGE_NONE':
                server.append(disk)
                usable_disk_num += 1

        self.assertTrue(usable_disk_num >= replica_num,
                        "usable disk num less then replica_num, can not replace disk.")

        max_disks_num = 0
        for sn , disks in servers.items():
            if len(disks) > max_disks_num:
                max_disks_num = len(disks)

        expand_cfg = {}
        expand_cfg['hosts'] = []
        used_disk_num = 0

        def _find_idx(k, v, arr):
            for i in range(0, len(arr)):
                if arr[i][k] == v:
                    return i
            return -1

        snarr = []
        for sn , disks in servers.items():
            snarr.append(sn)
        #random sort
        random.shuffle(snarr)

        disk_idx = 0
        while disk_idx < max_disks_num and used_disk_num < replica_num:
            for sn in snarr:
                disks = servers[sn]
                if used_disk_num >= replica_num:
                    break
                if len(disks) <= disk_idx:
                    continue
                cfg_idx = _find_idx('host_name', sn, expand_cfg['hosts'])
                if cfg_idx == -1:
                    newhost = {'host_name': sn, 'data':[{'disk': disks[disk_idx]['disk_id'],
                                                         'storage_type':'STORAGE_DATA'}]}
                    expand_cfg['hosts'].append(newhost)
                else:
                    expand_cfg['hosts'][cfg_idx]['data'].append({"disk":disks[disk_idx]['disk_id'],
                                                                 "storage_type":"STORAGE_DATA"})
                used_disk_num += 1
            disk_idx += 1

        self.vsan_client.expand_vsan_cluster(cluster_id, expand_cfg)
        time.sleep(3)
        self.client.wait_for_vsan_cluster_status(cluster_id, 'available')
        cluster_expand = self.vsan_client.show_vsan_cluster(cluster_id)
        disks = cluster_expand['disks']

        vs_disks = {}
        init_disks = {}
        expand_diks = {}

        for disk in disks:
            if disk['storage_type'] == 'STORAGE_DATA':
                vs_disks[disk['disk_id']] = disk['vs_sname']

        for host in init_cfg['hosts']:
            for init_disk in host['data']:
                init_disks[init_disk['disk']] = host['host_name']

        for host in expand_cfg['hosts']:
            for expand_disk in host['data']:
                expand_diks[expand_disk['disk']] = host['host_name']

        self.assertEqual(dict(init_disks.items() + expand_diks.items()), vs_disks,
                         'The fetched Vsan cluster disks is different '
                         'from init and expand Vsan cluster')

        self.assertEqual(len(vs_disks) - len(init_disks), replica_num,
                         'The fetched Vsan cluster expand data disks num is different '
                         'from replica number')

        servers = cluster_expand['servers']
        for serv in servers:
            self.assertEqual(True, serv['is_in_cls'],
                         'The fetched Vsan cluster is_in_cls is different True')

        capacity = cluster_expand['capacity']
        new_total_size = capacity['total_size']
        self.assertGreater(new_total_size, old_total_size,
                           'after expand , total_size no change')

    # Test cluster expand
    @test.idempotent_id('6564f114-dc6c-4d0b-adda-ff621f5d5212')
    def test_vsan_cluster_expand(self):
        self._test_vsan_cluster_expand()

    def _test_vsan_cluster_cancel_expand_hosts(self, **kwargs):
        cluster_hosts = CONF.vs.cluster_hosts
        replica_num = CONF.vs.replica_num
        hosts_lists = ''
        for h in cluster_hosts:
            hosts_lists = hosts_lists + h + ','
        hosts_lists = hosts_lists.rstrip(',')

        display_description = 'test for create vsan cluster'
        display_name = 'Vs-Test'
        creating = 'creating'

        kwargs['cluster_hosts'] = hosts_lists
        kwargs['display_description'] = display_description
        kwargs['display_name'] = display_name
        kwargs['status'] = creating
        kwargs['project_id'] = None
        # Create cluster
        cluster = self.vsan_client.create_vsan_cluster(**kwargs)
        self.assertIn('id', cluster)
        cluster_id = cluster['id']
        self.addCleanup(self._delete_vsan_cluster, cluster_id)

        disks = cluster['disks']
        servers = {}
        usable_disk_num = 0
        for disk in disks:
            sn = disk['vs_sname']
            if sn not in servers:
                servers[sn] = []
            server =  servers[sn]
            if disk['storage_type'] == 'STORAGE_NONE':
                server.append(disk)
                usable_disk_num += 1

        max_disks_num = 0
        for sn , disks in servers.items():
            if len(disks) > max_disks_num:
                max_disks_num = len(disks)

        init_cfg = {}
        init_cfg['replica'] = replica_num
        init_cfg['hosts'] = []
        used_disk_num = 0

        def _find_idx(k, v, arr):
            for i in range(0, len(arr)):
                if arr[i][k] == v:
                    return i
            return -1

        disk_idx = 0
        while disk_idx < max_disks_num and used_disk_num < replica_num:
            for sn , disks in servers.items():
                if used_disk_num >= replica_num:
                    break
                if len(disks) <= disk_idx:
                    continue
                cfg_idx = _find_idx('host_name', sn, init_cfg['hosts'])
                if cfg_idx == -1:
                    newhost = {'host_name': sn, 'data':[{'disk': disks[disk_idx]['disk_id'],
                                                         'storage_type':'STORAGE_DATA'}]}
                    init_cfg['hosts'].append(newhost)
                else:
                    init_cfg['hosts'][cfg_idx]['data'].append({"disk":disks[disk_idx]['disk_id'],
                                                               "storage_type":"STORAGE_DATA"})
                used_disk_num += 1
            disk_idx += 1

        display_name = 'n_cancel_expand_test'
        display_description = 'd_cancel_expand_test'
        self.vsan_client.init_vsan_cluster(cluster_id, init_cfg, 'compute',
                                           display_name=display_name,
                                           display_description=display_description)

        self.client.wait_for_vsan_cluster_status(cluster_id, 'available')
        cluster_init = self.vsan_client.show_vsan_cluster(cluster_id)

        disks = cluster_init['disks']
        bf_exp_disks = {}
        for disk in disks:
                bf_exp_disks[disk['disk_id']] = disk['vs_sname']

        expand_host = CONF.vs.expand_hosts[0]
        cluster_ehst = self.vsan_client.expand_vsan_cluster_hosts(cluster_id, expand_host)
        cluster_ehst = cluster_ehst['cluster']
        servs = cluster_ehst['servers']
        cp_snames = []
        for serv in servs:
            cp_snames.append(serv['cp_sname'])
            if serv['cp_sname'] == expand_host:
                self.assertEqual(False, serv['is_in_cls'],
                         'The fetched Vsan cluster is_in_cls is different True')

        init_exp_hosts = []
        init_exp_hosts.append(expand_host)
        init_exp_hosts = init_exp_hosts + cluster_hosts

        self.assertEqual(sorted(init_exp_hosts), sorted(cp_snames),
                      'The init and expand hosts not eaual Vsan cluster servers, expand hosts failed')

        self.vsan_client.cancel_expand_vsan_cluster_hosts(cluster_id)
        cluster_cancel_ehst = self.vsan_client.show_vsan_cluster(cluster_id)
        servs = cluster_cancel_ehst['servers']
        cp_snames = []
        for serv in servs:
            cp_snames.append(serv['cp_sname'])
            self.assertEqual(True, serv['is_in_cls'],
                             'The fetched Vsan cluster is_in_cls is different True')

        self.assertEqual(sorted(cluster_hosts), sorted(cp_snames),
                      'The init and expand hosts not eaual Vsan cluster servers, expand hosts failed')

        disks = cluster_cancel_ehst['disks']
        aft_cancel_exp_disks = {}
        for disk in disks:
                aft_cancel_exp_disks[disk['disk_id']] = disk['vs_sname']

        self.assertEqual(bf_exp_disks, aft_cancel_exp_disks, 'The disks before expand hosts not eaual '
                        'disks after cancel expand hosts,cancel-expand-hosts failed')

    # Test Vsan Cluster Cancel Expand Hosts
    @test.idempotent_id('27bfa5d6-e753-41a2-9d6e-3785cfb108f9')
    def test_vsan_cluster_cancel_expand_hosts(self):
        self._test_vsan_cluster_cancel_expand_hosts()

    def _test_vsan_cluster_rebalance(self, **kwargs):
        cluster_hosts = CONF.vs.cluster_hosts
        replica_num = CONF.vs.replica_num
        hosts_lists = ''
        for h in cluster_hosts:
            hosts_lists = hosts_lists + h + ','
        hosts_lists = hosts_lists.rstrip(',')

        display_description = 'test for create vsan cluster'
        display_name = 'Vs-Test'
        creating = 'creating'

        kwargs['cluster_hosts'] = hosts_lists
        kwargs['display_description'] = display_description
        kwargs['display_name'] = display_name
        kwargs['status'] = creating
        kwargs['project_id'] = None
        # Create cluster
        cluster = self.vsan_client.create_vsan_cluster(**kwargs)
        self.assertIn('id', cluster)
        cluster_id = cluster['id']
        self.addCleanup(self._delete_vsan_cluster, cluster_id)

        disks = cluster['disks']
        servers = {}
        usable_disk_num = 0
        for disk in disks:
            sn = disk['vs_sname']
            if sn not in servers:
                servers[sn] = []
            server =  servers[sn]
            if disk['storage_type'] == 'STORAGE_NONE':
                server.append(disk)
                usable_disk_num += 1

        self.assertTrue(usable_disk_num >= replica_num * 2,
                        "usable disk num less then replica_num * 2, can not test rebalance.")

        max_disks_num = 0
        for sn , disks in servers.items():
            if len(disks) > max_disks_num:
                max_disks_num = len(disks)

        init_cfg = {}
        init_cfg['replica'] = replica_num
        init_cfg['hosts'] = []
        used_disk_num = 0

        def _find_idx(k, v, arr):
            for i in range(0, len(arr)):
                if arr[i][k] == v:
                    return i
            return -1

        total_disk_num = replica_num * 2
        disk_idx = 0
        while disk_idx < max_disks_num and used_disk_num < total_disk_num:
            for sn , disks in servers.items():
                if used_disk_num >= total_disk_num:
                    break
                if len(disks) <= disk_idx:
                    continue
                cfg_idx = _find_idx('host_name', sn, init_cfg['hosts'])
                if cfg_idx == -1:
                    newhost = {'host_name': sn, 'data':[{'disk': disks[disk_idx]['disk_id'],
                                                         'storage_type':'STORAGE_DATA'}]}
                    init_cfg['hosts'].append(newhost)
                else:
                    init_cfg['hosts'][cfg_idx]['data'].append({"disk":disks[disk_idx]['disk_id'],
                                                               "storage_type":"STORAGE_DATA"})
                used_disk_num += 1
            disk_idx += 1

        display_name = 'n_rebalance_test'
        display_description = 'd_rebalance_test'
        self.vsan_client.init_vsan_cluster(cluster_id, init_cfg, 'compute',
                                           display_name=display_name,
                                           display_description=display_description)

        self.client.wait_for_vsan_cluster_status(cluster_id, 'available')
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        start_date = tomorrow.strftime("%Y-%m-%d")
        end_date = start_date
        start_time = "08:00"
        end_time = "09:00"
        self.vsan_client.rebalance_set(cluster_id, start_date, end_date, start_time, end_time)
        rebalance_plan = self.vsan_client.rebalance_get(cluster_id)
        rebalance_plan = rebalance_plan['rebalance']
        set_time = rebalance_plan.pop('set_time')
        rebalance_plan_expect = {
            "start_date" : start_date,
            "end_date" : end_date,
            "start_time" : start_time,
            "end_time" : end_time,
            "stop" : "0"}

        self.assertEqual(rebalance_plan, rebalance_plan_expect,
                         'The fetched Vsan cluster rebalance plan is different '
                         'from expect')
        set_time_arr = set_time.split(' ')
        set_time_date = set_time_arr[0]
        self.assertEqual(today.strftime("%Y-%m-%d"), set_time_date,
                         'The fetched Vsan cluster rebalance plan set_time_date is different '
                         'from expect')

        rebalance_status = self.vsan_client.rebalance_show(cluster_id)
        rebalance_status = rebalance_status['rebalance']
        rebalance_status_expect = {
            "msg" : start_date + " " + start_time,
            "state" : "ready"}

        self.assertEqual(rebalance_status, rebalance_status_expect,
                         'The fetched Vsan cluster rebalance plan status is different '
                         'from expect')

        self.vsan_client.rebalance_cancel(cluster_id)
        rebalance_plan = self.vsan_client.rebalance_get(cluster_id)
        rebalance_plan = rebalance_plan['rebalance']
        self.assertEqual({}, rebalance_plan,
                         'The fetched Vsan cluster rebalance plan is not empty')

        #stop
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        start_date = today.strftime("%Y-%m-%d")
        end_date = tomorrow.strftime("%Y-%m-%d")
        start_time = "00:00"
        end_time = "23:59"

        self.vsan_client.rebalance_set(cluster_id, start_date, end_date, start_time, end_time)
        #time.sleep(300)
        self.vsan_client.rebalance_stop(cluster_id)
        rebalance_plan = self.vsan_client.rebalance_get(cluster_id)
        rebalance_plan = rebalance_plan['rebalance']
        rebalance_plan.pop('set_time')
        rebalance_plan_expect = {
            "start_date" : start_date,
            "end_date" : end_date,
            "start_time" : start_time,
            "end_time" : end_time,
            "stop" : "1"}

        self.assertEqual(rebalance_plan, rebalance_plan_expect,
                         'The fetched Vsan cluster rebalance plan is different '
                         'from expect')

        rebalance_status = self.vsan_client.rebalance_show(cluster_id)
        rebalance_status = rebalance_status['rebalance']
        rebalance_status_expect = {
            "msg" : "",
            "state" : "stopped"}

        self.assertEqual(rebalance_status, rebalance_status_expect,
                         'The fetched Vsan cluster rebalance plan status is different '
                         'from expect')

    # Test cluster rebalance
    @test.idempotent_id('fdc9f2c8-32b2-49f2-90a7-8d2bef631ecb')
    def test_vsan_cluster_rebalance(self):
        self._test_vsan_cluster_rebalance()

    def _test_cluster_perform_get(self, **kwargs):
        cluster_hosts = CONF.vs.cluster_hosts
        replica_num = CONF.vs.replica_num
        hosts_lists = ''
        for h in cluster_hosts:
            hosts_lists = hosts_lists + h + ','
        hosts_lists = hosts_lists.rstrip(',')

        display_description = 'test for create vsan cluster'
        display_name = 'Vs-Test'
        creating = 'creating'

        kwargs['cluster_hosts'] = hosts_lists
        kwargs['display_description'] = display_description
        kwargs['display_name'] = display_name
        kwargs['status'] = creating
        kwargs['project_id'] = None
        # Create cluster
        cluster = self.vsan_client.create_vsan_cluster(**kwargs)
        self.assertIn('id', cluster)
        cluster_id = cluster['id']
        self.addCleanup(self._delete_vsan_cluster, cluster_id)

        disks = cluster['disks']
        servers = {}
        usable_disk_num = 0
        for disk in disks:
            sn = disk['vs_sname']
            if sn not in servers:
                servers[sn] = []
            server =  servers[sn]
            if disk['storage_type'] == 'STORAGE_NONE':
                server.append(disk)
                usable_disk_num += 1

        max_disks_num = 0
        for sn , disks in servers.items():
            if len(disks) > max_disks_num:
                max_disks_num = len(disks)

        init_cfg = {}
        init_cfg['replica'] = replica_num
        init_cfg['hosts'] = []
        used_disk_num = 0

        def _find_idx(k, v, arr):
            for i in range(0, len(arr)):
                if arr[i][k] == v:
                    return i
            return -1

        total_disk_num = replica_num * 2
        disk_idx = 0
        while disk_idx < max_disks_num and used_disk_num < total_disk_num:
            for sn , disks in servers.items():
                if used_disk_num >= total_disk_num:
                    break
                if len(disks) <= disk_idx:
                    continue
                cfg_idx = _find_idx('host_name', sn, init_cfg['hosts'])
                if cfg_idx == -1:
                    newhost = {'host_name': sn, 'data':[{'disk': disks[disk_idx]['disk_id'],
                                                         'storage_type':'STORAGE_DATA'}]}
                    init_cfg['hosts'].append(newhost)
                else:
                    init_cfg['hosts'][cfg_idx]['data'].append({"disk":disks[disk_idx]['disk_id'],
                                                               "storage_type":"STORAGE_DATA"})
                used_disk_num += 1
            disk_idx += 1

        display_name = 'n_test_cluster_perform_get'
        display_description = 'd_test_cluster_perform_get'
        self.vsan_client.init_vsan_cluster(cluster_id, init_cfg, 'compute',
                                           display_name=display_name,
                                           display_description=display_description)

        self.client.wait_for_vsan_cluster_status(cluster_id, 'available')
        time.sleep(90)

        def _test_one_type(cluster_id, time_type):
            perform = self.vsan_client.cluster_perform_get(cluster_id, time_type)
            perform = perform['perform']

            #check hitrate
            self.assertIn('hitrate', perform, "hitrate is not in perform")
            hitrate = perform['hitrate']

            self.assertIn('cluster_hitrate', hitrate, "cluster_hitrate is not in hitrate")
            cluster_hitrate = hitrate['cluster_hitrate']
            self.assertEqual(168, len(cluster_hitrate),
                            'The fetched Vsan cluster cluster_hitrate has not include 7 day')
            one_cls_hit = cluster_hitrate[0]
            self.assertIn('hitrate', one_cls_hit, "hitrate is not in one_cls_hit")
            self.assertIn('time', one_cls_hit, "time is not in one_cls_hit")


            self.assertIn('host_hitrate', hitrate, "host_hitrate is not in hitrate")
            host_hitrate = hitrate['host_hitrate']
            self.assertEqual(len(cluster_hosts), len(host_hitrate),
                            'The fetched Vsan cluster host_hitrate has not include all node')

            one_host_hit = host_hitrate[0]
            self.assertIn('hitrate', one_host_hit, "hitrate is not in one_host_hit")
            self.assertIn('ip', one_host_hit, "ip is not in one_host_hit")

            #check storage
            self.assertIn('storage', perform, "storage is not in perform")
            storage = perform['storage']

            self.assertEqual(60, len(storage),
                            'The fetched Vsan cluster storage has not include 60 day')
            one_stor = storage[0]
            self.assertIn('use_storage', one_stor, "hitrate is not in one_cls_hit")
            self.assertIn('free_storage', one_stor, "hitrate is not in one_cls_hit")
            self.assertIn('time', one_stor, "time is not in one_cls_hit")

            #check io
            if time_type == "day":
                data_len = 74
                err_log = "The fetched Vsan cluster storage has not include 1 day"
            elif time_type == "hour":
                data_len = 70
                err_log = "The fetched Vsan cluster storage has not include 1 hour"
            elif time_type == "min":
                data_len = 70
                err_log = "The fetched Vsan cluster storage has not include 1 min"
            elif time_type == "ten_min":
                data_len = 70
                err_log = "The fetched Vsan cluster storage has not include ten min"

            self.assertIn('io', perform, "io is not in perform")
            io = perform['io']
            self.assertEqual(data_len, len(io), err_log)
            one_io = io[0]

            self.assertIn('latency_write', one_io, "hitrate is not in one_day_io__hit")
            self.assertIn('latency_read', one_io, "hitrate is not in one_day_io__hit")
            self.assertIn('throughoutput_write', one_io, "time is not in one_day_io__hit")
            self.assertIn('throughoutput_read', one_io, "time is not in one_day_io__hit")
            self.assertIn('iops_write', one_io, "hitrate is not in one_day_io__hit")
            self.assertIn('iops_read', one_io, "time is not in one_day_io__hit")
            self.assertIn('time', one_io, "hitrate is not in one_day_io__hit")

        _test_one_type(cluster_id, "day")
        _test_one_type(cluster_id, "hour")
        _test_one_type(cluster_id, "min")
        _test_one_type(cluster_id, "ten_min")

    # Test cluster rebalance
    @test.idempotent_id('fdc9f2c8-32b2-49f2-90a7-8d2bef631ecb')
    def test_cluster_perform_get(self):
        self._test_cluster_perform_get()

    def _test_vsan_cluster_init_cache_backup(self, **kwargs):
        cluster_hosts = CONF.vs.cluster_hosts
        replica_num = CONF.vs.replica_num
        #self.assertGreater(replica_num, 1, "replica_num is not gt 1, can not init.")
        hosts_lists = ''
        for h in cluster_hosts:
            hosts_lists = hosts_lists + h + ','
        hosts_lists = hosts_lists.rstrip(',')

        display_description = 'test for create vsan cluster'
        display_name = 'Vs-Test'
        creating = 'creating'

        kwargs['cluster_hosts'] = hosts_lists
        kwargs['display_description'] = display_description
        kwargs['display_name'] = display_name
        kwargs['status'] = creating
        kwargs['project_id'] = None
        # Create cluster
        cluster = self.vsan_client.create_vsan_cluster(**kwargs)
        self.assertIn('id', cluster)
        cluster_id = cluster['id']
        self.addCleanup(self._delete_vsan_cluster, cluster_id)

        disks = cluster['disks']
        servers = {}
        for disk in disks:
            sn = disk['vs_sname']
            if sn not in servers:
                servers[sn] = []
            server =  servers[sn]
            if disk['storage_type'] == 'STORAGE_NONE':
                server.append(disk)

        self.assertGreaterEqual(len(servers) , replica_num ,
                        "usable servers num less then replica_num, can not init.")

        cac_serv = None
        idx_cac = 0
        for sn , disks in servers.items():
            has_cac = False
            idx_cac_tmp = 0
            for disk in disks:
                if disk['disk_type'] == 'DISK_SSD':
                    has_cac = True
                    idx_cac = idx_cac_tmp

                if has_cac == True:
                    break

                idx_cac_tmp += 1

            if has_cac == True and len(disks) >= 2:
                cac_serv = sn
                break

        self.assertNotEqual(None, cac_serv , "it has not SSD disk, can not init.")

        bak_serv = None
        for sn , disks in servers.items():
            if len(disks) >= 2 and sn != cac_serv:
                bak_serv = sn
                break

        self.assertNotEqual(None, bak_serv , "it has not enough disks to bak, can not init.")

        init_cfg = {}
        init_cfg['replica'] = replica_num
        init_cfg['hosts'] = []

        if idx_cac == 0:
            idx_dat = 1
        else:
            idx_dat = 0

        used_disk = []
        init_cfg['hosts'].append(
            {
                "host_name" : cac_serv,
                "data" : [{"disk":servers[cac_serv][idx_dat]['disk_id'],"storage_type":"STORAGE_DATA"},
                 {"disk":servers[cac_serv][idx_cac]['disk_id'],"storage_type":"STORAGE_CACHE"}
                 ]
            }
        )
        used_disk.append(servers[cac_serv][idx_dat]['disk_id'])
        used_disk.append(servers[cac_serv][idx_cac]['disk_id'])

        init_cfg['hosts'].append(
            {
                "host_name" : bak_serv,
                "data" : [{"disk":servers[bak_serv][0]['disk_id'],"storage_type":"STORAGE_DATA"},
                 {"disk":servers[bak_serv][1]['disk_id'],"storage_type":"STORAGE_BACKUP"}
                 ]
            }
        )

        used_disk.append(servers[bak_serv][0]['disk_id'])
        used_disk.append(servers[bak_serv][1]['disk_id'])

        def _find_idx(k, v, arr):
            for i in range(0, len(arr)):
                if arr[i][k] == v:
                    return i
            return -1

        data_disk_num = 2
        for sn , disks in servers.items():

            if data_disk_num >= replica_num:
                break

            cfg_idx = _find_idx('host_name', sn, init_cfg['hosts'])

            for disk in disks:
                if data_disk_num >= replica_num:
                    break

                if disk['disk_id'] in used_disk:
                    continue

                if cfg_idx == -1:
                    newhost = {'host_name': sn, 'data':[{'disk': disk['disk_id'],
                                                         'storage_type':'STORAGE_DATA'}]}
                    init_cfg['hosts'].append(newhost)
                else:
                    init_cfg['hosts'][cfg_idx]['data'].append({"disk":disk['disk_id'],
                                                               "storage_type":"STORAGE_DATA"})
                data_disk_num += 1

        self.assertEqual(replica_num, data_disk_num , "useable data disk lt replica_num, can not init.")

        display_name = 'n_init_cac_bak_test'
        display_description = 'd_init_cac_bak_test'
        node_type = 'controller'
        self.vsan_client.init_vsan_cluster(cluster_id, init_cfg, node_type,
                                           display_name=display_name,
                                           display_description=display_description)
        self.client.wait_for_vsan_cluster_status(cluster_id, 'available')

        clster = self.vsan_client.show_vsan_cluster(cluster_id)
        self.assertEqual('available', clster['status'],
                         'The fetched Vsan cluster status is different '
                         'from the created Vsan cluster')
        self.assertEqual(display_name, clster['name'],
                         'The fetched Vsan cluster name is different '
                         'from the created Vsan cluster')
        self.assertEqual(display_description, clster['description'],
                         'The fetched Vsan cluster description is different '
                         'from the created Vsan cluster')
        self.assertEqual(cluster_id, clster['id'],
                         'The fetched Vsan cluster id is different '
                         'from the created Vsan cluster')
        self.assertEqual(replica_num, int(clster['replication']),
                         'The fetched Vsan cluster replica_num is different '
                         'from the created Vsan cluster')
        self.assertEqual(node_type, clster['node_type'],
                         'The fetched Vsan cluster node_type is different '
                         'from the created Vsan cluster')
        capacity = clster['capacity']
        self.assertEqual(capacity['used_size'] + capacity['avail_size'], capacity['total_size'],
                         'The fetched Vsan cluster size is error '
                         'from the created Vsan cluster')
        self.assertGreater(capacity['total_size'], 0,
                         'The fetched Vsan cluster total_size is error '
                         'from the created Vsan cluster')

        servers = clster['servers']
        cluster_nodes = []
        for serv in servers:
            self.assertEqual(True, serv['is_in_cls'],
                         'The fetched Vsan cluster is_in_cls is different '
                         'from the created Vsan cluster')
            cluster_nodes.append(serv["cp_sname"])

        cluster_nodes_sort = sorted(cluster_nodes)
        cluster_hosts_sort = sorted(cluster_hosts)
        self.assertEqual(cluster_nodes_sort, cluster_hosts_sort,
                         'The fetched Vsan cluster cluster_nodes is different '
                         'from the created Vsan cluster')

        disks = clster['disks']
        vs_disks = {}
        init_disks = {}

        for disk in disks:
            if disk['storage_type'] in ['STORAGE_DATA', 'STORAGE_CACHE' ,'STORAGE_BACKUP']:
                vs_disks[disk['disk_id']] = {"hostname": disk['vs_sname'],
                                             "storage_type": disk['storage_type']}

        for host in init_cfg['hosts']:
            for init_disk in host['data']:
                init_disks[init_disk['disk']] = {"hostname": host['host_name'],
                                                 "storage_type": init_disk['storage_type']}


        self.assertEqual(init_disks, vs_disks,
                         'The fetched Vsan cluster disks is different '
                         'from the created Vsan cluster')

        self.assertEqual(len(vs_disks), replica_num + 2,
                         'The fetched Vsan cluster data disks num is different '
                         'from the created Vsan cluster')

    # Test init
    @test.idempotent_id('3bdae13b-29f3-44c9-8c5c-72b92fcdcbc4')
    def test_vsan_cluster_init_cache_backup(self):
        self._test_vsan_cluster_init_cache_backup()


    def _test_vsan_cluster_expand_cache_backup(self, **kwargs):
        cluster_hosts = CONF.vs.cluster_hosts
        replica_num = CONF.vs.replica_num
        #self.assertGreater(replica_num, 1, "replica_num is not gt 1, can not init.")
        hosts_lists = ''
        for h in cluster_hosts:
            hosts_lists = hosts_lists + h + ','
        hosts_lists = hosts_lists.rstrip(',')

        display_description = 'test for create vsan cluster'
        display_name = 'Vs-Test'
        creating = 'creating'

        kwargs['cluster_hosts'] = hosts_lists
        kwargs['display_description'] = display_description
        kwargs['display_name'] = display_name
        kwargs['status'] = creating
        kwargs['project_id'] = None
        # Create cluster
        cluster = self.vsan_client.create_vsan_cluster(**kwargs)
        self.assertIn('id', cluster)
        cluster_id = cluster['id']
        self.addCleanup(self._delete_vsan_cluster, cluster_id)

        disks = cluster['disks']
        servers = {}
        for disk in disks:
            sn = disk['vs_sname']
            if sn not in servers:
                servers[sn] = []
            server =  servers[sn]
            if disk['storage_type'] == 'STORAGE_NONE':
                server.append(disk)

        self.assertGreaterEqual(len(servers) , replica_num ,
                        "usable servers num less then replica_num, can not init.")

        cac_serv = None
        idx_cac = 0
        for sn , disks in servers.items():
            has_cac = False
            idx_cac_tmp = 0
            for disk in disks:
                if disk['disk_type'] == 'DISK_SSD':
                    has_cac = True
                    idx_cac = idx_cac_tmp

                if has_cac == True:
                    break

                idx_cac_tmp += 1

            if has_cac == True and len(disks) >= 2:
                cac_serv = sn
                break

        self.assertNotEqual(None, cac_serv , "it has not SSD disk, can not init.")

        bak_serv = None
        for sn , disks in servers.items():
            if len(disks) >= 2 and sn != cac_serv:
                bak_serv = sn
                break

        self.assertNotEqual(None, bak_serv , "it has not enough disks to bak, can not init.")

        init_cfg = {}
        init_cfg['replica'] = replica_num
        init_cfg['hosts'] = []

        expand_cfg = {}
        expand_cfg['hosts'] = []

        if idx_cac == 0:
            idx_dat = 1
        else:
            idx_dat = 0

        used_disk = []
        init_cfg['hosts'].append(
            {
                "host_name" : cac_serv,
                "data" : [{"disk":servers[cac_serv][idx_dat]['disk_id'],"storage_type":"STORAGE_DATA"}
                 ]
            }
        )

        expand_cfg['hosts'].append(
            {
                "host_name" : cac_serv,
                "data" : [{"disk":servers[cac_serv][idx_cac]['disk_id'],"storage_type":"STORAGE_CACHE"}
                 ]
            }
        )

        used_disk.append(servers[cac_serv][idx_dat]['disk_id'])
        used_disk.append(servers[cac_serv][idx_cac]['disk_id'])

        init_cfg['hosts'].append(
            {
                "host_name" : bak_serv,
                "data" : [{"disk":servers[bak_serv][0]['disk_id'],"storage_type":"STORAGE_DATA"}
                 ]
            }
        )

        expand_cfg['hosts'].append(
            {
                "host_name" : bak_serv,
                "data" : [{"disk":servers[bak_serv][1]['disk_id'],"storage_type":"STORAGE_BACKUP"}
                 ]
            }
        )

        used_disk.append(servers[bak_serv][0]['disk_id'])
        used_disk.append(servers[bak_serv][1]['disk_id'])

        def _find_idx(k, v, arr):
            for i in range(0, len(arr)):
                if arr[i][k] == v:
                    return i
            return -1

        data_disk_num = 2
        for sn , disks in servers.items():

            if data_disk_num >= replica_num:
                break

            cfg_idx = _find_idx('host_name', sn, init_cfg['hosts'])

            for disk in disks:
                if data_disk_num >= replica_num:
                    break

                if disk['disk_id'] in used_disk:
                    continue

                if cfg_idx == -1:
                    newhost = {'host_name': sn, 'data':[{'disk': disk['disk_id'],
                                                         'storage_type':'STORAGE_DATA'}]}
                    init_cfg['hosts'].append(newhost)
                else:
                    init_cfg['hosts'][cfg_idx]['data'].append({"disk":disk['disk_id'],
                                                               "storage_type":"STORAGE_DATA"})
                data_disk_num += 1

        self.assertEqual(replica_num, data_disk_num , "useable data disk lt replica_num, can not init.")

        display_name = 'n_expand_cac_bak_test'
        display_description = 'd_expand_cac_bak_test'
        node_type = 'compute'
        self.vsan_client.init_vsan_cluster(cluster_id, init_cfg, node_type,
                                           display_name=display_name,
                                           display_description=display_description)
        self.client.wait_for_vsan_cluster_status(cluster_id, 'available')

        clster = self.vsan_client.show_vsan_cluster(cluster_id)
        self.assertEqual('available', clster['status'],
                         'The fetched Vsan cluster status is different '
                         'from the created Vsan cluster')
        self.assertEqual(display_name, clster['name'],
                         'The fetched Vsan cluster name is different '
                         'from the created Vsan cluster')
        self.assertEqual(display_description, clster['description'],
                         'The fetched Vsan cluster description is different '
                         'from the created Vsan cluster')
        self.assertEqual(cluster_id, clster['id'],
                         'The fetched Vsan cluster id is different '
                         'from the created Vsan cluster')
        self.assertEqual(replica_num, int(clster['replication']),
                         'The fetched Vsan cluster replica_num is different '
                         'from the created Vsan cluster')
        self.assertEqual(node_type, clster['node_type'],
                         'The fetched Vsan cluster node_type is different '
                         'from the created Vsan cluster')

        capacity = clster['capacity']

        self.assertEqual(capacity['used_size'] + capacity['avail_size'], capacity['total_size'],
                         'The fetched Vsan cluster size is error '
                         'from the created Vsan cluster')
        self.assertGreater(capacity['total_size'], 0,
                         'The fetched Vsan cluster total_size is error '
                         'from the created Vsan cluster')

        servers = clster['servers']
        cluster_nodes = []
        for serv in servers:
            self.assertEqual(True, serv['is_in_cls'],
                         'The fetched Vsan cluster is_in_cls is different '
                         'from the created Vsan cluster')
            cluster_nodes.append(serv["cp_sname"])

        cluster_nodes_sort = sorted(cluster_nodes)
        cluster_hosts_sort = sorted(cluster_hosts)
        self.assertEqual(cluster_nodes_sort, cluster_hosts_sort,
                         'The fetched Vsan cluster cluster_nodes is different '
                         'from the created Vsan cluster')

        disks = clster['disks']
        vs_disks = {}
        init_disks = {}

        for disk in disks:
            if disk['storage_type'] in ['STORAGE_DATA', 'STORAGE_CACHE' ,'STORAGE_BACKUP']:
                vs_disks[disk['disk_id']] = {"hostname": disk['vs_sname'],
                                             "storage_type": disk['storage_type']}

        for host in init_cfg['hosts']:
            for init_disk in host['data']:
                init_disks[init_disk['disk']] = {"hostname": host['host_name'],
                                                 "storage_type": init_disk['storage_type']}

        self.assertEqual(init_disks, vs_disks,
                         'The fetched Vsan cluster disks is different '
                         'from the created Vsan cluster')

        self.assertEqual(len(vs_disks), replica_num,
                         'The fetched Vsan cluster data disks num is different '
                         'from the created Vsan cluster')

        self.vsan_client.expand_vsan_cluster(cluster_id, expand_cfg)
        time.sleep(3)
        self.client.wait_for_vsan_cluster_status(cluster_id, 'available')
        cluster_expand = self.vsan_client.show_vsan_cluster(cluster_id)
        disks = cluster_expand['disks']

        vs_disks = {}
        init_disks = {}
        expand_diks = {}

        for disk in disks:
            if disk['storage_type'] in ['STORAGE_DATA', 'STORAGE_CACHE' ,'STORAGE_BACKUP']:
                vs_disks[disk['disk_id']] = {"hostname": disk['vs_sname'],
                                             "storage_type": disk['storage_type']}


        for host in init_cfg['hosts']:
            for init_disk in host['data']:
                init_disks[init_disk['disk']] = {"hostname": host['host_name'],
                                                 "storage_type": init_disk['storage_type']}

        for host in expand_cfg['hosts']:
            for expand_disk in host['data']:
                expand_diks[expand_disk['disk']] = {"hostname": host['host_name'],
                                                    "storage_type": expand_disk['storage_type']}

        self.assertEqual(dict(init_disks.items() + expand_diks.items()), vs_disks,
                         'The fetched Vsan cluster disks is different '
                         'from init and expand Vsan cluster')

        self.assertEqual(len(vs_disks) - len(init_disks), 2,
                         'The fetched Vsan cluster expand data disks num is different from 2')

        servers = cluster_expand['servers']
        for serv in servers:
            self.assertEqual(True, serv['is_in_cls'],
                             'The fetched Vsan cluster is_in_cls is different True')


    # Test init
    @test.idempotent_id('3bdae13b-29f3-44c9-8c5c-72b92fcdcbc4')
    def test_vsan_cluster_expand_cache_backup(self):
        self._test_vsan_cluster_expand_cache_backup()
