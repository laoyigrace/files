
from tempest_lib import exceptions as lib_exc
from tempest_lib import decorators
from tempest.api.network import sf_base
from tempest.common.utils import data_utils
from tempest import test


class SfRouterAclgroupsTest(sf_base.SfRouteAclBaseNetworkTest):
    """
    Tests the following operations in the Neutron API using the REST client for
    Neutron:

        create a router_aclgroup for a tenant
        list tenant's router_aclgroups
        delete a router_aclgroup
        create a router_acl for a tenant
        list tenant's router_acls
        update a router_acl
        delete a router_acl
    """

    @test.attr(type='smoke')
    @test.idempotent_id('6901af82-7e35-11e5-869d-0242ae110093')
    def test_create_router_aclgroup_and_acl(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-6901af82')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        self.assertTrue(router_aclgroup_id)
        self.assertEqual(name, create_body["router_acl_group"]["name"])
        # Create router_acl
        src_cidr = '0.0.0.0-255.255.255.255'
        dst_cidr = '0.0.0.0-255.255.255.255'
        service_ssh = 'any/any:any'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service_ssh, acl_localtion='dvr')
        self.assertEqual(router_acl['router_acl']['router_acl_group_id'],
                         router_aclgroup_id)
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service_ssh)
        self.assertEqual(router_acl['router_acl']['acl_localtion'], 'dvr')

    @test.idempotent_id('a32096fa-7ea4-11e5-a8a6-fefcfeb453f2')
    def test_list_router_aclgroups_and_acls(self):
        # List tenant's router_aclgroups and router_acls
        name = data_utils.rand_name('router-aclgroup-a32096fa')
        router_aclgroup = self._create_router_aclgroup(name=name)
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup["router_acl_group"]["id"])
        src_cidr = '192.168.0.1-192.168.0.2'
        dst_cidr = '192.168.0.1-192.168.0.2'
        service_icmp = 'a32096fa/icmp:type-18.code-3'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup["router_acl_group"]["id"],
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service_icmp, acl_localtion='dvr')
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service_icmp)
        self.assertEqual(router_acl['router_acl']['acl_localtion'], 'dvr')
        groups_list_body = self.sf_network_client.list_router_aclgroups()
        router_aclgroup = [aclgroup['id'] for aclgroup in
                           groups_list_body['router_acl_groups']
                           if aclgroup['id'] ==
                           router_aclgroup['router_acl_group']['id']]
        self.assertNotEmpty(router_aclgroup, "aclgroup not found in the list")
        # List tenant's router_acls
        acls_list_body = self.sf_network_client.list_router_acls()
        router_acl = [acl['id'] for acl in acls_list_body['router_acls']
                      if acl['id'] == router_acl['router_acl']['id']]
        self.assertNotEmpty(router_acl, "router_acl not found in the list")

    @test.attr(type='smoke')
    @test.idempotent_id('b7c2b240-846d-11e5-b462-00e0666534ba')
    def test_show_router_acl(self):
        # List tenant's router_aclgroups and router_acls
        name = data_utils.rand_name('router-aclgroup-b7c2b240')
        router_aclgroup = self._create_router_aclgroup(name=name)
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup["router_acl_group"]["id"])
        src_cidr = '192.168.0.1-192.168.0.2'
        dst_cidr = '192.168.0.1-192.168.0.2'
        service_icmp = 'b7c2b240/icmp:type-8.code-1'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup["router_acl_group"]["id"],
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service_icmp, acl_localtion='dvr')
        # show tenant's router_acl
        acl_show_body = self.sf_network_client.show_router_acl(
            router_acl['router_acl']['id'])
        self.assertEqual(acl_show_body['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(acl_show_body['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(acl_show_body['router_acl']['service'], service_icmp)
        self.assertEqual(acl_show_body['router_acl']['acl_localtion'], 'dvr')

    @test.attr(type='smoke')
    @test.idempotent_id('a2d6568f-7fa7-11e5-8593-00e0666534ba')
    def test_update_router_acl(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-a2d6568f')
        router_aclgroup = self._create_router_aclgroup(name=name)
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup["router_acl_group"]["id"])
        # Create tenant's router_acl
        dst_cidr = '1.1.1.1-1.1.2.1'
        src_cidr = '2.2.1.1-2.2.2.1'
        service_icmp = 'a2d6568f/icmp:type-9.code-0'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup["router_acl_group"]["id"],
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            description='router-aclgroup-a2d6568f',
            service=service_icmp, acl_localtion='dvr')
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service_icmp)
        self.assertEqual(router_acl['router_acl']['valid'], 'enable')
        self.assertEqual(router_acl['router_acl']['action'], 'permit')
        self.assertEqual(router_acl['router_acl']['acl_localtion'], 'dvr')
        self.assertEqual(router_acl['router_acl']['description'],
                         'router-aclgroup-a2d6568f')
        # Update router_acl
        update_body = self.sf_network_client.update_router_acl(
            router_acl["router_acl"]["id"],
            description='a2d6568f',
            valid='disable', action='deny')
        self.assertEqual(update_body['router_acl']['description'], 'a2d6568f')
        self.assertEqual(update_body['router_acl']['valid'], 'disable')
        self.assertEqual(update_body['router_acl']['action'], 'deny')

    @test.attr(type='smoke')
    @test.idempotent_id('bddeb5f0-c344-11e5-88ce-00e0666534ba')
    def test_enable_disable_router_acl(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-a2d6568f')
        router_aclgroup = self._create_router_aclgroup(name=name)
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup["router_acl_group"]["id"])
        # Create tenant's router_acl
        dst_cidr = '1.1.1.1-1.1.2.1'
        src_cidr = '2.2.1.1-2.2.2.1'
        service_icmp = 'a2d6568f/icmp:type-9.code-0'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup["router_acl_group"]["id"],
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            description='router-aclgroup-a2d6568f',
            service=service_icmp, acl_localtion='dvr', valid='enable')
        self.assertEqual(router_acl['router_acl']['valid'], 'enable')
        # disable router_acl
        update_body = self.sf_network_client.update_router_acl(
            router_acl["router_acl"]["id"], valid='disable')
        self.assertEqual(update_body['router_acl']['valid'], 'disable')

    @test.attr(type='smoke')
    @test.idempotent_id('1a987330-c340-11e5-aca2-00e0666534ba')
    def test_delete_router_acl(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-1a987330')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        self.assertTrue(router_aclgroup_id)
        # Create router_acl
        src_cidr = '192.168.0.1-192.168.0.2'
        dst_cidr = '192.168.1.1-192.168.1.2'
        service_ssh = '6901af82/tcp:56'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service_ssh, acl_localtion='dvr')
        router_acl_id = router_acl["router_acl"]["id"]
        self.assertTrue(router_acl_id)
        # delete router_acl and router_aclgroup
        self.sf_network_client.delete_router_acl(router_acl_id)
        acls_list_body = self.sf_network_client.list_router_acls()
        router_acl = [acl['id'] for acl in acls_list_body['router_acls']
                      if acl['id'] == router_acl_id]
        self.assertEmpty(router_acl, "Delete router_acl faild")

    @test.attr(type='smoke')
    @test.idempotent_id('b49e28b0-c342-11e5-8b27-00e0666534ba')
    def test_delete_multi_router_acl(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-b49e28b0')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        self.assertTrue(router_aclgroup_id)
        # Create router_acl
        src_cidr = '192.168.0.1-192.168.0.2'
        dst_cidr = '192.168.1.1-192.168.1.2'
        service_ssh = '6901af82/tcp:56'
        router_acl_args = []
        for i in range(0, 9):
            router_acl = self._create_router_acl(
                router_acl_group_id=router_aclgroup_id,
                src_cidr=src_cidr, dst_cidr=dst_cidr,
                service=service_ssh, acl_localtion='dvr')
            router_acl_id = router_acl["router_acl"]["id"]
            self.assertTrue(router_acl_id)
            router_acl_args.append(router_acl_id)

        # delete router_acls and router_aclgroup
        for router_acl_id in router_acl_args:
            self.sf_network_client.delete_router_acl(router_acl_id)
            acls_list_body = self.sf_network_client.list_router_acls()
            router_acl = [acl['id'] for acl in acls_list_body['router_acls']
                          if acl['id'] == router_acl_id]
            self.assertEmpty(router_acl, "Delete router_acl faild")

    @test.attr(type='smoke')
    @test.idempotent_id('54e4c621-8203-11e5-895f-00e0666534ba')
    def test_create_conflict_router_acls(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-54e4c621')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        # Create router_acl and enable
        src_cidr = '192.168.0.1-192.168.0.2'
        dst_cidr = '192.168.1.1-192.168.1.2'
        service_ssh = '54e4c621/tcp:5126'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service_ssh, acl_localtion='dvr')
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service_ssh)
        self.assertEqual(router_acl['router_acl']['valid'], 'enable')
        # Create same router_acl and disable
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service_ssh, valid='disable',
            acl_localtion='dvr')
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service_ssh)
        self.assertEqual(router_acl['router_acl']['valid'], 'disable')

    @decorators.skip_because(bug="29696")
    @test.idempotent_id('da735a30-8385-11e5-9d36-00e0666534ba')
    def test_create_512_router_acl(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-da735a30')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        # Create router_acl
        src_cidr = '192.168.0.1-192.168.0.2'
        dst_cidr = '192.168.1.1-192.168.1.2'
        service_ssh = '00e0666534ba/tcp:56'
        for i in range(1, 513):
            self._create_router_acl(router_acl_group_id=router_aclgroup_id,
                                    src_cidr=src_cidr, dst_cidr=dst_cidr,
                                    service=service_ssh, acl_localtion='dvr')
        list_body = self.sf_network_client.list_router_acls()
        number = len(list_body['router_acls'])
        self.assertEqual(number, 512)
        self.assertRaises(lib_exc.BadRequest, self._create_router_acl,
                          router_acl_group_id=router_aclgroup_id,
                          src_cidr=src_cidr, dst_cidr=dst_cidr,
                          service=service_ssh, acl_localtion='dvr')

    @test.idempotent_id('898b78e1-838b-11e5-9baa-00e0666534ba')
    def test_create_evr_router_acl(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-898b78e1')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        # Create router_acl
        src_cidr = self._get_public_cidr()
        dst_cidr = self._get_private_cidr()
        service = '00e0666534ba/tcp:56'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service, acl_localtion='evr')
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service)
        self.assertEqual(router_acl['router_acl']['acl_localtion'], 'evr')

    @test.idempotent_id('5c19c140-838c-11e5-a529-00e0666534ba')
    def test_create_dvr_router_acl(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-5c19c140')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        # Create router_acl
        src_cidr = self._get_private_cidr()
        dst_cidr = self._get_private_cidr()
        service = '5c19c140/tcp:5126'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service, acl_localtion='dvr')
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service)
        self.assertEqual(router_acl['router_acl']['acl_localtion'], 'dvr')

    @test.attr(type='smoke')
    @test.idempotent_id('cbcbaea1-c3d2-11e5-b7b6-00e0666534ba')
    def test_create_router_acl_tcp_all_disable(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-cbcbaea1')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        # Create router_acl
        src_cidr = '0.0.0.0-255.255.255.255'
        dst_cidr = '0.0.0.0-255.255.255.255'
        service = '00e0666534ba/tcp:1-65535'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service, acl_localtion='dvr',
            valid='disable')
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service)
        self.assertEqual(router_acl['router_acl']['acl_localtion'], 'dvr')
        self.assertEqual(router_acl['router_acl']['valid'], 'disable')

    @test.attr(type='smoke')
    @test.idempotent_id('8b65ce5e-c3da-11e5-8ca6-00e0666534ba')
    def test_create_router_acl_tcp_enable(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-8b65ce5e')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        # Create router_acl
        src_cidr = '192.168.0.1-192.168.0.2'
        dst_cidr = '192.168.1.1-192.168.1.2'
        service = '00e0666534ba1/tcp:1-10'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service, acl_localtion='dvr',
            valid='enable')
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service)
        self.assertEqual(router_acl['router_acl']['acl_localtion'], 'dvr')
        self.assertEqual(router_acl['router_acl']['valid'], 'enable')

    @test.attr(type='smoke')
    @test.idempotent_id('0cf76730-c3dc-11e5-8b94-00e0666534ba')
    def test_create_router_acl_udp_all_port_enable(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-0cf76730')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        # Create router_acl
        src_cidr = '192.168.0.1-192.168.0.2'
        dst_cidr = '192.168.1.1-192.168.1.2'
        service = '0cf76730/udp:1-65535'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service, acl_localtion='dvr')
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service)
        self.assertEqual(router_acl['router_acl']['acl_localtion'], 'dvr')

    @test.attr(type='smoke')
    @test.idempotent_id('4f0749c0-c3db-11e5-862f-00e0666534ba')
    def test_create_router_acl_udp_enable(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-4f0749c0')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        # Create router_acl
        src_cidr = '0.0.0.0-255.255.255.255'
        dst_cidr = '0.0.0.0-255.255.255.255'
        service = '4f0749c0/udp:1-16'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service, acl_localtion='dvr',
            valid='enable')
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service)
        self.assertEqual(router_acl['router_acl']['acl_localtion'], 'dvr')
        self.assertEqual(router_acl['router_acl']['valid'], 'enable')

    @test.attr(type='smoke')
    @test.idempotent_id('3e6f2acf-c3e8-11e5-b5ea-00e0666534ba')
    def test_create_router_acl_other_disable(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-3e6f2acf')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        # Create router_acl
        src_cidr = '192.168.100.0/24'
        dst_cidr = '192.168.100.0/24'
        service = '3e6f2acf/50:any'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service, acl_localtion='dvr',
            valid='disable')
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service)
        self.assertEqual(router_acl['router_acl']['acl_localtion'], 'dvr')
        self.assertEqual(router_acl['router_acl']['valid'], 'disable')

    @test.attr(type='smoke')
    @test.idempotent_id('d9780200-c3f6-11e5-b788-00e0666534ba')
    def test_create_router_acl_udp_disable(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-d9780200')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        # Create router_acl
        src_cidr = '192.168.100.1-192.168.100.255'
        dst_cidr = '0.0.0.0-255.255.255.255'
        service = 'd9780200/udp:1-1456'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service, acl_localtion='dvr',
            valid='disable')
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service)
        self.assertEqual(router_acl['router_acl']['acl_localtion'], 'dvr')
        self.assertEqual(router_acl['router_acl']['valid'], 'disable')

    @test.attr(type='smoke')
    @test.idempotent_id('624cd8d1-c3f7-11e5-a4ee-00e0666534ba')
    def test_create_router_acl_icmp_disable(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-624cd8d1')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        # Create router_acl
        src_cidr = '192.168.100.1-192.168.100.255'
        dst_cidr = '1.1.1.1-255.255.255.255'
        service = '624cd8d1/icmp:type-9.code-0'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service, acl_localtion='dvr',
            valid='disable')
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service)
        self.assertEqual(router_acl['router_acl']['acl_localtion'], 'dvr')
        self.assertEqual(router_acl['router_acl']['valid'], 'disable')

    @test.attr(type='smoke')
    @test.idempotent_id('11235770-c3f9-11e5-a781-00e0666534ba')
    def test_create_router_acl_multi_servers(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-11235770')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        # Create router_acl
        src_cidr = '0.0.0.0-255.255.255.255'
        dst_cidr = '1.1.1.1-255.255.255.255'
        service = '11235770/tcp:1701,udp:1701@00e0666534ba/icmp:type-9.code-0'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service, acl_localtion='dvr')
        self.assertEqual(router_acl['router_acl']['src_cidr'], src_cidr)
        self.assertEqual(router_acl['router_acl']['dst_cidr'], dst_cidr)
        self.assertEqual(router_acl['router_acl']['service'], service)
        self.assertEqual(router_acl['router_acl']['acl_localtion'], 'dvr')
