from tempest import config as t_config
from tempest import sf_config
import openstack as ostack
import os
import re

import values as values_module

from keystoneclient.auth.identity import v2
from keystoneclient import session
from keystoneclient.v2_0 import client as keystone_c
from neutronclient.v2_0 import client as neutron_c
from novaclient import client as nova_c


_RUNTIME = "RETRIEVE_RUNTIME"


class Utils(object):

    @staticmethod
    def get_dict_keys(c, name=None):
        """get the keys of all dicts in a list which looks like [{"":""},{"":""}]

        :return:dict of keys
        """
        keys = []
        if c is None or c == []:
            return keys
        if name is not None:
            if name in c.keys():
                c = c[name]
            else:
                raise ValueError, "%s is not in %s" % (name, c)
        else:
            c = c
        if c is None or c == []:
            return keys
        for kv in c:
            for key in kv:
                keys.append(key)

        return keys

    @staticmethod
    def check_dup(src, dst):
        """Check the same key

        True if two dicts have the same key in the same group.
        The dicts is just like [{},{}]

        :param src: the first dict
        :param dst: the other dict

        :return:True and the same keys if they have the same.
        """
        dup_keys = []
        ret_b = False

        if (src is None) or (src == []) or (dst is None) or (dst == []):
            return ret_b, dup_keys

        src_keys = Utils.get_dict_keys(src)
        dst_keys = Utils.get_dict_keys(dst)
        for src_key in src_keys:
            if src_key in dst_keys:
                dup_keys.append(src_key)
                ret_b = True

        return ret_b, dup_keys


class DefaultRuntimeDupError(ValueError):
    def __init__(self, **kwargs):
        super(DefaultRuntimeDupError, self).__init__()
        self.group_name = kwargs["group_name"]
        self.keys = kwargs["keys"]

    def __str__(self):
        return "%s group has duplicate keys in default and runtime: %s" % \
               (self.group_name, self.keys)


class NoSuchKeyFunctionDefined(ValueError):
    def __init__(self, **kwargs):
        """

        :param kwargs:  gropu_name: the name of the group. key_function:the
            name of the key.
        :return:
        """
        super(NoSuchKeyFunctionDefined, self).__init__(self)
        self.group_name = kwargs["group_name"]
        self.key_function = kwargs["key_function"]

    def __str__(self):
        return "%s group has no key %s, " \
               "or The %s group don't defined the function %s" % \
               (self.group_name, self.key_function,
                self.group_name, self.key_function)


class OpenstackInitError(EnvironmentError):
    def __init__(self, **kwargs):
        super(OpenstackInitError, self).__init__()
        self.msg = kwargs["msg"]

    def __str__(self):
        return "Error occur when Init the openstack env, please check." \
               "The error message is as follows : %s" % self.msg


class NoOriginalTempestFileError(ValueError):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return "There is no file in the system:%s." % self.path


class TempestFileExistError(ValueError):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return "The file to generate has already existed in %s." % self.path


class BaseGroup(object):
    def __init__(self):
        self._group = None
        self.defaults = None
        self.name = "base_group"
        self.runtime = None
        self.openstack = None

    def retrieve(self, key_name, openstack):
        """
        Call the function `key_name`, to get the `keyname` info from openstack
        :param key_name:
        :param openstack:
        :return:
        """
        self.openstack = openstack
        func_name = "retrieve_%s" % key_name
        func = getattr(self, func_name)
        if func is None:
            raise NoSuchKeyFunctionDefined(
                group_name=self.name, key_fuction=func_name)
        value = func()

        return value

    def check_dup(self):
        ret, same_keys = Utils.check_dup(
            self.defaults, self.runtime)
        if ret:
            raise DefaultRuntimeDupError(group_name=self.name, keys=same_keys)

    def get_defaults_runtime(self):
        temp = []
        if self.defaults is None or self.defaults is []:
            pass
        else:
            temp.extend(self.defaults)

        if self.runtime is None or self.runtime is []:
            pass
        else:
            temp.extend(self.runtime)

        return temp


class DefaultGroup(BaseGroup):
    def __init__(self):
        super(DefaultGroup, self).__init__()
        self.name = "DEFAULT"
        self.defaults = [
            {
                "debug": self._retrieve_debug(),
                "log_file": self._retrieve_log_file(),
                "use_stderr": self._retrieve_use_stderr(),
                "use_syslog": self._retrieve_use_syslog()
            }
        ]
        self.runtime = []
        self._group = t_config.DefaultGroup

        self.check_dup()

    @staticmethod
    def _retrieve_debug():
        """
        :return: True| false
        """

        debug = True
        return debug

    @staticmethod
    def _retrieve_log_file():
        """
        :return: should be customerd
        """

        log_file = "/tmp/tempest.log"
        return log_file

    @staticmethod
    def _retrieve_use_stderr():
        """
        :return: True| false
        """

        use_stderr = False
        return use_stderr

    @staticmethod
    def _retrieve_use_syslog():
        """
        :return: True| false
        """

        use_syslog = False
        return use_syslog


class AuthGroup(BaseGroup):

    def __init__(self):
        super(AuthGroup, self).__init__()
        self.name = "auth"
        self.defaults = [
            {"allow_tenant_isolation": self._retrieve_allow_tenant_isolation()}
        ]
        self.runtime = []
        self._group = t_config.AuthGroup
        self.check_dup()

    @staticmethod
    def _retrieve_allow_tenant_isolation():
        """
        :return: True| false
        """

        allow_tenant_isolation = True
        return allow_tenant_isolation


class TelemetryGroup(BaseGroup):
    def __init__(self):
        super(TelemetryGroup, self).__init__()
        self.name = "telemetry"
        self.defaults = [
            {"too_slow_to_test": self._retrieve_too_slow_to_test()}
        ]
        self.runtime = []
        self._group = t_config.TelemetryGroup
        self.check_dup()

    @staticmethod
    def _retrieve_too_slow_to_test():
        too_slow_to_test = False
        return too_slow_to_test


class ComputeGroup(BaseGroup):

    def __init__(self):
        super(ComputeGroup, self).__init__()
        self.name = "compute"
        self.defaults = [
            {
                "fixed_network_name": self._retrieve_fixed_network_name(),
                "ssh_connect_method": self._retrieve_ssh_connect_method(),
                "image_alt_ssh_user":
                    self._retrieve_image_alt_ssh_user(),
                "image_ssh_user": self._retrieve_image_ssh_user(),
                # NOTE(add by sf laoyi)
                "image_ssh_password": self._retrieve_image_ssh_password(),
                "ssh_auth_method": self._retrieve_ssh_auth_method(),
                "ssh_timeout": self._retrieve_ssh_timeout(),
                "ip_version_for_ssh":
                    self._retrieve_ip_version_for_ssh(),
                "network_for_ssh": self._retrieve_network_for_ssh(),
                "ssh_user": self._retrieve_ssh_user(),
                "build_timeout": self._retrieve_build_timeout()
            }
        ]
        self.runtime = [
            {
                "flavor_ref_alt": self._retrieve_flavor_ref_alt(),
                "flavor_ref": self._retrieve_flavor_ref(),
                "image_ref_alt": self._retrieve_image_ref_alt(),
                "image_ref": self._retrieve_image_ref(),
            }
        ]
        self._group = t_config.ComputeGroup
        self.check_dup()
        self.nova_client = None

    def _get_nova_client(self):
        user_name = self.openstack.user_name
        user_password = self.openstack.user_password
        tenant_name = self.openstack.tenant_name
        host = self.openstack.host
        auth_url = "http://%s:5000/v2.0" % host
        auth = v2.Password(
            auth_url=auth_url,
            username=user_name,
            password=user_password,
            tenant_name = tenant_name
        )
        sess = session.Session(auth=auth)
        version = 2
        self.nova_client = nova_c.Client(version, session=sess)
        return self.nova_client

    def _get_flavors(self):
        if self.nova_client is None:
            self._get_nova_client()
        flavors = self.nova_client.flavors.list()
        return flavors

    def _get_flavor_id(self, flavor_name):
        flavors = self._get_flavors()
        for flavor in flavors:
            if flavor.name == flavor_name:
                return flavor.id
        return None

    def _get_images(self):
        if self.nova_client is None:
            self._get_nova_client()
        images = self.nova_client.images.list()
        return images

    def _get_image_id(self, image_name):
        images = self._get_images()
        for image in images:
            if image.name == image_name:
                return image.id
        return None

    @staticmethod
    def _retrieve_fixed_network_name():
        """should be customized"""

        fixed_network_name = "private"
        return fixed_network_name

    @staticmethod
    def _retrieve_ssh_connect_method():
        """
        :return: fixed|floating
        """

        ssh_connect_method = "floating"
        return ssh_connect_method

    @staticmethod
    def _retrieve_flavor_ref_alt():
        return _RUNTIME

    def retrieve_flavor_ref_alt(self):
        flavor_name = "m1.medium"
        flavor_id = self._get_flavor_id(flavor_name)
        if flavor_id is None:
            raise ValueError, "There is no flavor named '%s'" % flavor_name
        return flavor_id

    @staticmethod
    def _retrieve_flavor_ref():
        return _RUNTIME

    def retrieve_flavor_ref(self):
        flavor_name = "m1.tiny"
        flavor_id = self._get_flavor_id(flavor_name)
        if flavor_id is None:
            raise ValueError, "There is no flavor named '%s'" % flavor_name
        return flavor_id

    @staticmethod
    def _retrieve_image_alt_ssh_user():
        """should be customized"""

        image_alt_ssh_user = "cirros"
        return image_alt_ssh_user

    @staticmethod
    def _retrieve_image_ref_alt():
        return _RUNTIME

    def retrieve_image_ref_alt(self):
        # TODO:
        # image_name should not be the same as image_name in image_ref func
        image_name = "cirros"
        image_id = self._get_image_id(image_name)
        if image_id is None:
            raise ValueError, "There is no image named '%s'" % image_name
        return image_id

    @staticmethod
    def _retrieve_image_ssh_user():
        """should be customized"""

        image_ssh_user = "cirros"
        return image_ssh_user

    @staticmethod
    def _retrieve_image_ssh_password():
        """should be customized"""

        image_ssh_password = "cubswin:)"
        return image_ssh_password

    @staticmethod
    def _retrieve_ssh_auth_method():
        """should be customized"""

        ssh_auth_method = "password"
        return ssh_auth_method

    @staticmethod
    def _retrieve_image_ref():
        return _RUNTIME

    def retrieve_image_ref(self):
        image_name = "cirros"
        image_id = self._get_image_id(image_name)
        if image_id is None:
            raise ValueError, "There is no image named '%s'" % image_name
        return image_id

    @staticmethod
    def _retrieve_ssh_timeout():
        """should be customized"""

        ssh_timeout = 196
        return ssh_timeout

    @staticmethod
    def _retrieve_ip_version_for_ssh():
        ip_version_for_ssh = 4
        return ip_version_for_ssh

    @staticmethod
    def _retrieve_network_for_ssh():
        """should be customized"""

        network_for_ssh = "private"
        return network_for_ssh

    @staticmethod
    def _retrieve_ssh_user():
        """should be customized"""

        ssh_user = "cirros"
        return ssh_user

    @staticmethod
    def _retrieve_build_timeout():
        """should be customized"""

        build_timeout = 196
        return build_timeout


class ComputerFeatureEnabledGroup(BaseGroup):
    def __init__(self):
        super(ComputerFeatureEnabledGroup, self).__init__()
        self.name = "compute-feature-enabled"
        self.defaults = [
            {
                "live_migrate_paused_instances":
                    self._retrieve_live_migrate_paused_instances(),
                "preserve_ports": self._retrieve_preserve_ports(),
                "api_extensions": self._retrieve_api_extensions(),
                "block_migration_for_live_migration":
                    self._retrieve_block_migration_for_live_migration(),
                "change_password": self._retrieve_change_password(),
                "live_migration": self._retrieve_live_migration(),
                "vnc_console": self._retrieve_vnc_console()
            }
        ]
        self.runtime = []
        self._group = t_config.ComputeFeaturesGroup

        self.check_dup()

    @staticmethod
    def _retrieve_live_migrate_paused_instances():
        """
        :return: True|False
        """

        live_migrate_paused_instances = True
        return live_migrate_paused_instances

    @staticmethod
    def _retrieve_preserve_ports():
        """
        :return: True|False
        """

        preserve_ports = True
        return preserve_ports

    @staticmethod
    def _retrieve_api_extensions():
        """should be customized"""

        api_extensions = "all"
        return api_extensions

    @staticmethod
    def _retrieve_block_migration_for_live_migration():
        """
        :return: True|False
        """

        block_migration_for_live_migration = False
        return block_migration_for_live_migration

    @staticmethod
    def _retrieve_change_password():
        """
        :return: True|False
        """

        change_password = False
        return change_password

    @staticmethod
    def _retrieve_live_migration():
        """
        :return: True|False
        """

        live_migration = False
        return live_migration

    @staticmethod
    def _retrieve_vnc_console():
        vnc_console = True
        return vnc_console


class DashboardGroup(BaseGroup):
    def __init__(self):
        super(DashboardGroup, self).__init__()
        self.name = "dashboard"
        self.defaults = []
        self.runtime = [
            {
                "login_url": self._retrieve_login_url(),
                "dashboard_url": self._retrieve_dashboard_url()
            }
        ]
        self._group = t_config.DashboardGroup

        self.check_dup()

    @staticmethod
    def _retrieve_login_url():
        login_url = _RUNTIME
        return login_url

    def retrieve_login_url(self):
        login_url = "http://%s/auth/login" % self.openstack.host
        return login_url

    @staticmethod
    def _retrieve_dashboard_url():
        dashboard_url = _RUNTIME
        return dashboard_url

    def retrieve_dashboard_url(self):
        dashboard_url = "http://%s/" % self.openstack.host
        return dashboard_url


class IdentityGroup(BaseGroup):
    def __init__(self):
        super(IdentityGroup, self).__init__()
        self.name = "identity"
        self.defaults = [
            {
                "auth_version": self._retrieve_auth_version(),
                "admin_domain_name": self._retrieve_admin_domain_name()
            }
        ]
        self.runtime = [
            {
                "admin_tenant_id": self._retrieve_admin_tenant_id(),
                "admin_tenant_name": self._retrieve_admin_tenant_name(),
                "admin_username": self._retrieve_admin_username(),
                "admin_password": self._retrieve_admin_password(),
                "tenant_name": self._retrieve_tenant_name(),
                "alt_tenant_name": self._retrieve_alt_tenant_name(),
                "username": self._retrieve_username(),
                "alt_username": self._retrieve_alt_username(),
                "password": self._retrieve_password(),
                "alt_password": self._retrieve_alt_password(),
                "uri_v3": self._retrieve_uri_v3(),
                "uri": self._retrieve_uri()
            }
        ]
        self._group = t_config.IdentityGroup
        self.keystone_client = None
        self.check_dup()
        self.keystone_port = "5000"

    def _default_password(self):
        default_passowrd = "Admin12345"
        return default_passowrd

    def _get_keystone_client(self):
        user_name = self.openstack.user_name
        user_password = self.openstack.user_password
        tenant_name = self.openstack.tenant_name
        host = self.openstack.host
        auth_url = "http://%s:5000/v2.0" % host
        keystone = keystone_c.Client(
            username=user_name,
            password=user_password,
            tenant_name=tenant_name,
            auth_url=auth_url
        )
        self.keystone_client = keystone

        return keystone

    def _get_tenants_list(self):
        """
        :return: a list of the keystoneclient.v2_0.tenants.Tenants object
        """
        if self.keystone_client is None:
            self._get_keystone_client()

        tenants_list = self.keystone_client.tenants.list()
        return tenants_list

    def _get_tenants_list_dict(self):
        """
        :return: a list of a tenant dict which contains the tenant info.
        example: [{u'id':u'xxxxx', u'name':u'yyyy', ........},{}]
        """
        tenants = []
        tenants_list = self._get_tenants_list()
        for tenant in tenants_list:
            t = tenant.to_dict()
            tenants.append(t)
        return tenants

    def _tenant_exist(self, name):
        """check if the tenant exists in the openstack

        :param name: the tenant name to check
        :return:
        """
        tenants = self._get_tenants_list_dict()
        for tenant in tenants:
            if name == tenant["name"]:
                return name
        return None

    def _tenant_create(self, name, enabled=True):
        if self._tenant_exist(name):
            return name

        if name is None or name is "":
            raise ValueError, "when creating tenant ,tenant name is wrong." \
                              "The tenant name is '%s'" % name

        if self.keystone_client is None:
            self._get_keystone_client()

        tenant = self.keystone_client.tenants.create(
            tenant_name=name, enabled=enabled)
        return name

    def _get_users_list(self):
        # like _get_tenants_list
        if self.keystone_client is None:
            self._get_keystone_client()

        users_list = self.keystone_client.users.list()
        return users_list

    def _get_users_list_dict(self):
        # like _get_tenants_list_dict
        users = []
        users_list = self._get_users_list()

        for user in users_list:
            t = user.to_dict()
            users.append(t)

        return users

    def _user_exist(self, name):
        """check if the user exists in the openstack

        :param name: the user name to check
        :return:
        """
        users = self._get_users_list_dict()
        for user in users:
            if user["name"] == name:
                return name
        return None

    def _user_create(self, username, password=None, tenant_id=None):
        if self._user_exist(username):
            return username

        if username is None or username is "":
            raise ValueError, "when creating user ,username is wrong." \
                              "The username is '%s'" % username

        if self.keystone_client is None:
            self._get_keystone_client()

        if password is None:
            password = self.retrieve_password()
        tenant_id = self.retrieve_admin_tenant_id()

        user = self.keystone_client.users.create(name=username,
                                                 password=password,
                                                 tenant_id=tenant_id)
        return username

    def _retrieve_tenant_id(self, name):
        tenants = self._get_tenants_list_dict()
        for tenant in tenants:
            if name == tenant["name"]:
                return tenant["id"]
        return None

    @staticmethod
    def _retrieve_auth_version():
        auth_version = "v2"
        return auth_version

    @staticmethod
    def _retrieve_admin_domain_name():
        admin_domain_name = "Default"
        return admin_domain_name

    @staticmethod
    def _retrieve_admin_tenant_id():
        admin_tenant_id = _RUNTIME
        return admin_tenant_id

    def retrieve_admin_tenant_id(self, admin_tenant_name = "admin"):
        tenant_id = self._retrieve_tenant_id(admin_tenant_name)
        if tenant_id is not None:
            return tenant_id

        self._tenant_create(admin_tenant_name)
        tenant_id = self._retrieve_tenant_id(admin_tenant_name)
        if tenant_id is not None:
            return tenant_id

        raise ValueError, "Though the tenant(%s) is created, it's id is " \
                          "retrieved unsuccessfully"

    @staticmethod
    def _retrieve_admin_tenant_name():
        admin_tenant_name = _RUNTIME
        return admin_tenant_name

    def retrieve_admin_tenant_name(self, admin_tenant_name = "admin"):
        self.retrieve_tenant_name(tenant_name=admin_tenant_name)
        return admin_tenant_name

    @staticmethod
    def _retrieve_admin_username():
        admin_username = _RUNTIME
        return admin_username

    def retrieve_admin_username(self):
        admin_username = self.openstack.user_name
        return admin_username

    @staticmethod
    def _retrieve_admin_password():
        admin_password = _RUNTIME
        return admin_password

    def retrieve_admin_password(self):
        admin_password = self.openstack.user_password
        return admin_password

    @staticmethod
    def _retrieve_tenant_name():
        tenant_name = _RUNTIME
        return tenant_name

    def retrieve_tenant_name(self, tenant_name="demo"):
        if self._tenant_exist(name=tenant_name):
            return tenant_name
        ret = self._tenant_create(name=tenant_name)
        return tenant_name

    @staticmethod
    def _retrieve_alt_tenant_name():
        alt_tenant_name = _RUNTIME
        return alt_tenant_name

    def retrieve_alt_tenant_name(self, alt_tenant_name="alt_demo"):
        self.retrieve_tenant_name(tenant_name=alt_tenant_name)
        return alt_tenant_name

    @staticmethod
    def _retrieve_username():
        username = _RUNTIME
        return username

    def retrieve_username(self, username="demo"):
        if self._user_exist(username):
            return username

        ret = self._user_create(username=username)
        return username

    @staticmethod
    def _retrieve_alt_username():
        alt_username = _RUNTIME
        return alt_username

    def retrieve_alt_username(self, alt_username="alt_demo"):
        self.retrieve_username(username=alt_username)
        return alt_username

    @staticmethod
    def _retrieve_password():
        password = _RUNTIME
        return password

    def retrieve_password(self, password=None):
        if password is None:
            return self._default_password()
        else:
            return password

    @staticmethod
    def _retrieve_alt_password():
        alt_password = _RUNTIME
        return alt_password

    def retrieve_alt_password(self, password=None):
        alt_password = self.retrieve_password(password=password)
        return alt_password

    @staticmethod
    def _retrieve_uri_v3():
        uri_v3 = _RUNTIME
        return uri_v3

    def retrieve_uri_v3(self):
        uri_v3 = "http://%s:%s/v3" % (self.openstack.host, self.keystone_port)
        return uri_v3

    @staticmethod
    def _retrieve_uri():
        uri = _RUNTIME
        return uri

    def retrieve_uri(self):
        uri = "http://%s:%s/v2.0/" % (self.openstack.host, self.keystone_port)
        return uri


class NetworkGroup(BaseGroup):
    def __init__(self):
        super(NetworkGroup, self).__init__()
        self.name = "network"
        self.defaults = [
            {
                "tenant_networks_reachable":
                    self._retrieve_tenant_networks_reachable(),
                "api_version": self._retrieve_api_version()
            }
        ]
        self.runtime = [
            {
                "default_network": self._retrieve_default_network(),
                "public_router_id": self._retrieve_public_router_id(),
                "public_network_id": self._retrieve_public_network_id()
            }
        ]
        self._group = t_config.NetworkGroup
        self.check_dup()
        self.neutron_client = None

    def _get_neutron_client(self):
        user_name = self.openstack.user_name
        user_password = self.openstack.user_password
        tenant_name = self.openstack.tenant_name
        host = self.openstack.host
        auth_url = auth_url = "http://%s:5000/v2.0" % host
        self.neutron_client = neutron_c.Client(
            username=user_name,
            password=user_password,
            tenant_name=tenant_name,
            auth_url=auth_url
        )
        return self.neutron_client

    def _get_networks(self):
        if self.neutron_client is None:
            self._get_neutron_client()
        networks = self.neutron_client.list_networks()
        networks = networks["networks"]
        return networks

    def _get_subnets(self):
        if self.neutron_client is None:
            self._get_neutron_client()
        subnets = self.neutron_client.list_subnets()
        subnets = subnets["subnets"]
        return subnets

    def _get_routers(self):
        if self.neutron_client is None:
            self._get_neutron_client()
        routers = self.neutron_client.list_routers()
        routers = routers["routers"]
        return routers

    def _get_private_network_subnets_id(self):
        networks = self._get_networks()
        for network in networks:
            if network["name"] == "default_network":
                return network["subnets"]
        return None

    @staticmethod
    def _retrieve_default_network():
        default_network = _RUNTIME
        return default_network

    def retrieve_default_network(self):
        subnet_id = self._get_private_network_subnets_id()
        # subnet_id is a list
        if subnet_id is None:
            raise ValueError, "Can not get private subnets's id"
        subnets = self._get_subnets()
        for subnet in subnets:
            if subnet["id"] in subnet_id:
                return subnet["cidr"]
        raise ValueError, "There is not subnet whose id is '%s'" % subnet_id

    @staticmethod
    def _retrieve_public_router_id():
        public_router_id = _RUNTIME
        return public_router_id

    def retrieve_public_router_id(self):
        router_name = "default_router"
        routers = self._get_routers()
        for router in routers:
            if router["name"] == router_name:
                return router["id"]
        raise ValueError, "There is not router named for '%s'" % router_name

    @staticmethod
    def _retrieve_public_network_id():
        public_network_id = _RUNTIME
        return public_network_id

    def retrieve_public_network_id(self):
        network_name = "public"
        networks = self._get_networks()
        for network in networks:
            if network["name"] == network_name:
                return network["id"]
        raise ValueError, "There is no network named for '%s'" % network_name

    @staticmethod
    def _retrieve_tenant_networks_reachable():
        tenant_networks_reachable = False
        return tenant_networks_reachable

    @staticmethod
    def _retrieve_api_version():
        api_version = "2.0"
        return api_version


class NetworkFeatureEnabledGroup(BaseGroup):
    def __init__(self):
        super(NetworkFeatureEnabledGroup, self).__init__()
        self.name = "network-feature-enabled"
        self.defaults = [
            {
                "api_extensions": self._retrieve_api_extensions(),
                "ipv6_subnet_attributes":
                    self._retrieve_ipv6_subnet_attributes(),
                "ipv6": self._retrieve_ipv6()

            }
        ]
        self.runtime = []
        self._group = t_config.NetworkFeaturesGroup

        self.check_dup()

    @staticmethod
    def _retrieve_api_extensions():
        api_extensions = "all"
        return api_extensions

    @staticmethod
    def _retrieve_ipv6_subnet_attributes():
        ipv6_subnet_attributes = True
        return ipv6_subnet_attributes

    @staticmethod
    def _retrieve_ipv6():
        ipv6 = False
        return ipv6


class ServiceAvailableGroup(BaseGroup):
    def __init__(self):
        super(ServiceAvailableGroup, self).__init__()
        self.name = "service_available"
        self.defaults = [
            {
                "cinder": self._retrieve_cinder(),
                "neutron": self._retrieve_neutron(),
                "glance": self._retrieve_glance(),
                "swift": self._retrieve_swift(),
                "nova": self._retrieve_nova(),
                "heat": self._retrieve_heat(),
                "ceilometer": self._retrieve_ceilometer(),
                "horizon": self._retrieve_horizon()
            }
        ]
        self.runtime = []
        self._group = t_config.ServiceAvailableGroup

        self.check_dup()

    @staticmethod
    def _retrieve_cinder():
        cinder = True
        return cinder

    @staticmethod
    def _retrieve_neutron():
        neutron = True
        return neutron

    @staticmethod
    def _retrieve_glance():
        glance = True
        return glance

    @staticmethod
    def _retrieve_swift():
        swift = False
        return swift

    @staticmethod
    def _retrieve_nova():
        nova = True
        return nova

    @staticmethod
    def _retrieve_heat():
        heat = False
        return heat

    @staticmethod
    def _retrieve_ceilometer():
        ceilometer = True
        return ceilometer

    @staticmethod
    def _retrieve_horizon():
        horizon = True
        return horizon


class SfCommonGroup(BaseGroup):
    def __init__(self):
        super(SfCommonGroup, self).__init__()
        self.name = "sf_common_info"
        self.defaults = []
        self.runtime = [
            {
                "ctl_host": self._retrieve_ctl_host(),
                "ctl_ssh_port": self._retrieve_ctl_ssh_port(),
                "ctl_ssh_username": self._retrieve_ctl_ssh_username(),
                "ctl_ssh_password": self._retrieve_ctl_ssh_password(),
                "horizon_username": self._retrieve_horizon_username(),
                "horizon_password": self._retrieve_horizon_password()
            }
        ]
        self._group = t_config.SfCommonInfoGroup

        self.check_dup()

    @staticmethod
    def _retrieve_ctl_host():
        ctl_host = _RUNTIME
        return ctl_host

    def retrieve_ctl_host(self):
        server = self.openstack.host
        return server

    @staticmethod
    def _retrieve_ctl_ssh_port():
        ssh_port = 22
        return ssh_port

    def retrieve_ctl_ssh_port(self):
        ssh_port = self.openstack.ssh_port
        return ssh_port

    @staticmethod
    def _retrieve_ctl_ssh_username():
        ctl_ssh_username = "root"
        return ctl_ssh_username

    def retrieve_ctl_ssh_username(self):
        ctl_ssh_username = self.openstack.ssh_username
        return ctl_ssh_username

    @staticmethod
    def _retrieve_ctl_ssh_password():
        ctl_ssh_password = "1"
        return ctl_ssh_password

    def retrieve_ctl_ssh_password(self):
        ctl_ssh_password = self.openstack.ssh_password
        return ctl_ssh_password

    @staticmethod
    def _retrieve_horizon_username():
        horizon_username = "admin"
        return horizon_username

    def retrieve_horizon_username(self):
        horizon_username = self.openstack.user_name
        return horizon_username

    @staticmethod
    def _retrieve_horizon_password():
        horizon_password = "Admin123456"
        return horizon_password

    def retrieve_horizon_password(self):
        horizon_password = self.openstack.user_password
        return horizon_password


class OsloConcurrencyGroup(BaseGroup):
    def __init__(self):
        super(OsloConcurrencyGroup, self).__init__()
        self.name = "oslo_concurrency"
        self.defaults = [
            {
                "lock_path": self._retrieve_lock_path(),

            }
        ]
        self.runtime = []
        self._group = sf_config.OsloConcurrencyGroup

        self.check_dup()

    @staticmethod
    def _retrieve_lock_path():
        lock_path = "/tmp"
        return lock_path


class RetrieveOpenstackInfo(object):
    """Retrieve info from openstack info

    :param info: the info from webui.
    """

    def __init__(self, group, info):
        self.group = group
        self.name = self.group.name
        self.info = info

        # defaults, customer, runtime, values looks like [{},{}]
        self.customer = self._customer()
        self.defaults = self._defaults()
        self.runtime = self._runtime()
        self.values = []

        self.openstack = self._openstack(self.info)

    def _openstack(self, info):
        os_info = info["openstack"]
        o = None
        # try:
        o = ostack.Dev(os_info)
        # except Exception as e:
        # raise OpenstackInitError(msg=e.message)
        return o

    def check_customer_none(self, s_key):
        g_info = self.customer[self.name]
        if g_info is None:
            return True
        tmp = []
        flag = False
        for key_value in g_info:
            for key, value in key_value.items():

                if s_key == key and key_value[key] is "":
                    flag = True
                else:
                    tmp.append({key: value})

        self.customer[self.name] = tmp
        return flag

    def _delete_dup(self, c):
        """delete the duplicate keys when c and self.cusomer have the same key.

        :return the new dict which delete the same key
        """
        customer_keys = Utils.get_dict_keys(self.customer, self.name)
        temp = []
        if c is None or c is []:
            return temp
        for d_key_value in c:
            for d_key, d_value in d_key_value.items():
                if d_key in customer_keys and \
                        self.check_customer_none(d_key) is False:
                    continue
                else:
                    temp.append({d_key: d_value})
        return temp

    def _defaults(self):

        defaults = self.group.defaults
        defaults = self._delete_dup(defaults)
        return defaults

    def _runtime(self):
        runtime = self.group.runtime
        runtime = self._delete_dup(runtime)
        return runtime

    def _customer(self):

        if "customer" not in self.info:
            return None

        customer = self.info["customer"]
        flag = False
        for group in customer:
            if self.name in group.keys():
                flag = True
                customer = group
                break

        if flag is False:
            return None

        return customer

    def _retrieve(self):
        """
        Get the runtime value from openstack by calling the function rt_value
        in original runtime

        :param runtime:self.runtime or something like that
        :return: new runtimes with the values of keys
        """
        runtime_values = []
        for rt_key_value in self.runtime:

            for (rt_key, rt_value) in rt_key_value.items():
                func_m = rt_key
                rt_value = self.group.retrieve(func_m, self.openstack)
                runtime_values.append({rt_key:rt_value})

        return runtime_values

    def flag_changes(self):
        tmp = []
        flag = "sangforcustomer_"

        for key_value in self.values:
            for key, value in key_value.items():
                if isinstance(value, str) and flag in value:
                    continue
                else:
                    value = "%s%s" % (flag, value)
                tmp.append({key: value})

        self.values = tmp

    def _merge(self, c):
        """
        merge the c to self.values
        :param c: the self.runtime or self.defaults or something like that
        :return:values
        """
        if c is None or c == []:
            return True
        self.values.extend(c)

    def merge(self):
        self.runtime = self._retrieve()
        self.values = []
        self._merge(self.defaults)

        self._merge(self.runtime)
        if self.customer is not None and self.customer is not {}:
            self._merge(self.customer[self.name])

        self.flag_changes()

        return self.values

    def get_all_values(self):
        all_values = self.merge()
        return all_values


class RetrieveDefaultInfo(RetrieveOpenstackInfo):
    def __init__(self, info):
        group = DefaultGroup()
        super(RetrieveDefaultInfo, self).__init__(group, info)


class RetrieveAuthInfo(RetrieveOpenstackInfo):
    """Get and merge the info for auth group

    :param info: the info passed from others, such as webui or the caller.
    :param self.defaults: the values must be changed as default.Setting and
    handing is in class AuthGroup.
    :param self.customer: the values retrieved from the info.
    :param self.runtime: the values that must be retrieved from
    openstack runtime env.

    """

    def __init__(self, info):
        group = AuthGroup()
        super(RetrieveAuthInfo, self).__init__(group, info)


class RetrieveComputeInfo(RetrieveOpenstackInfo):
    def __init__(self, info):
        group = ComputeGroup()
        super(RetrieveComputeInfo, self).__init__(group, info)


class RetrieveComputerFeatureEnabledInfo(RetrieveOpenstackInfo):
    def __init__(self, info):
        group = ComputerFeatureEnabledGroup()
        super(RetrieveComputerFeatureEnabledInfo, self).__init__(group, info)


class RetrieveDashboardInfo(RetrieveOpenstackInfo):
    def __init__(self, info):
        group = DashboardGroup()
        super(RetrieveDashboardInfo, self).__init__(group, info)


class RetrieveIdentityInfo(RetrieveOpenstackInfo):
    def __init__(self, info):
        group = IdentityGroup()
        super(RetrieveIdentityInfo, self).__init__(group, info)


class RetrieveNetworkInfo(RetrieveOpenstackInfo):
    def __init__(self, info):
        group = NetworkGroup()
        super(RetrieveNetworkInfo, self).__init__(group, info)


class RetrieveNetworkFeatureEnabledInfo(RetrieveOpenstackInfo):
    def __init__(self, info):
        group = NetworkFeatureEnabledGroup()
        super(RetrieveNetworkFeatureEnabledInfo, self).__init__(group, info)


class RetrieveServiceAvailableInfo(RetrieveOpenstackInfo):
    def __init__(self, info):
        group = ServiceAvailableGroup()
        super(RetrieveServiceAvailableInfo, self).__init__(group, info)


class RetrieveSfCommonInfo(RetrieveOpenstackInfo):
    def __init__(self, info):
        group = SfCommonGroup()
        super(RetrieveSfCommonInfo, self).__init__(group, info)


class RetrieveOsloConcurrencyInfo(RetrieveOpenstackInfo):
    def __init__(self, info):
        group = OsloConcurrencyGroup()
        super(RetrieveOsloConcurrencyInfo, self).__init__(group, info)


class RetrieveTelemetryInfo(RetrieveOpenstackInfo):
    def __init__(self, info):
        group = TelemetryGroup()
        super(RetrieveTelemetryInfo, self).__init__(group, info)


def get_values(info):
    """Get the values to be replaced

    :return:
    """
    changes = []

    attrs = get_attributes()
    for attr in attrs:
        reg = r"^Retrieve.*Info$"
        if re.match(reg, attr) and attr is not "RetrieveOpenstackInfo":
            retrieve_c = values_module.__getattribute__(attr)
            retrieve = retrieve_c(info)
            tmp_info = retrieve.get_all_values()
            group = {retrieve.name: tmp_info}
            changes.append(group)

    """
    retrieve_c = values_module.__getattribute__("RetrieveAuthInfo")
    retrieve = retrieve_c(info)
    #retrieve = RetrieveAuthInfo(info)
    auth_info = retrieve.get_all_values()
    auth = {"auth": auth_info}
    changes.append(auth)

    retrieve = RetrieveComputeInfo(info)
    compute_info = retrieve.get_all_values()
    compute = {"compute": compute_info}
    changes.append(compute)
    """

    return changes


def get_values_for_ui():
    """
    auth = AuthGroup()
    compute = ComputeGroup()
    temp = {
       auth.name: auth.get_defaults_runtime(),
       compute.name: compute.get_defaults_runtime()
    }
    """

    temp = {}
    attr = get_attributes()
    reg = r"Group$"

    for group in attr:
        if re.search(reg, group) and group is not "BaseGroup":
            group_class = values_module.values_module.__getattribute__(group)
            g = group_class()
            temp[g.name] = g.get_defaults_runtime()
    return temp


def get_attributes():
    attributes = dir(values_module)
    return attributes


def change_values(src_file, dst_file, changes=None):
    if changes is True:
        return True

    if not os.path.exists(src_file):
        raise NoOriginalTempestFileError(src_file)

    if os.path.exists(dst_file):
        raise TempestFileExistError(dst_file)

    fp = open(src_file, "r")
