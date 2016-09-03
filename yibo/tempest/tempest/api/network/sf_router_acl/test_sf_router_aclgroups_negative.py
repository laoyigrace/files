from tempest_lib import exceptions as lib_exc
from tempest.api.network import sf_base
from tempest.common.utils import data_utils
from tempest import test


class SfRouterAclgroupsNegativeTest(sf_base.SfRouteAclBaseNetworkTest):

    @test.attr(type=['negative'])
    @test.idempotent_id('57f5d15e-839d-11e5-a9b9-00e0666534ba')
    def test_update_router_acl_options(self):
        # Create tenant's router_aclgroup
        name = data_utils.rand_name('router-aclgroup-57f5d15e')
        create_body = self._create_router_aclgroup(name=name)
        router_aclgroup_id = create_body["router_acl_group"]["id"]
        self.addCleanup(self.sf_network_client.delete_router_aclgroup,
                        router_aclgroup_id)
        # Create router_acl
        src_cidr = self._get_private_cidr()
        dst_cidr = self._get_private_cidr()
        service = '57f5d15e/tcp:56'
        service2 = '57f5d15e/udp:56'
        router_acl = self._create_router_acl(
            router_acl_group_id=router_aclgroup_id,
            src_cidr=src_cidr, dst_cidr=dst_cidr,
            service=service, acl_localtion='dvr')
        self.assertNotEmpty(router_acl, "router_acl not found in the list")
        self.assertRaises(lib_exc.BadRequest, self._create_router_acl,
                          router_acl_group_id=router_aclgroup_id,
                          service=service2)
        self.assertRaises(lib_exc.BadRequest, self._create_router_acl,
                          router_acl_group_id=router_aclgroup_id,
                          src_cidr=dst_cidr)
        self.assertRaises(lib_exc.BadRequest, self._create_router_acl,
                          router_acl_group_id=router_aclgroup_id,
                          dst_cidr=src_cidr)
        self.assertRaises(lib_exc.BadRequest, self._create_router_acl,
                          router_acl_group_id=router_aclgroup_id,
                          acl_localtion='evr')
