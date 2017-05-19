import logging as std_logging
import os


from oslo_config import cfg
from oslo_log import log as logging
from oslo_log import _options as log_opts
from tempest import config
from tempest import sf_config

import customers
import values


_CONF = cfg.CONF

_opts = config._opts
_opts.extend(sf_config._opts)
_opts.extend(log_opts.list_opts())

# auto_demo shows how to add group and key-value in this file
auto_demo_group = cfg.OptGroup(name='auto_demo',
                               title="Used to extend for sangfor ")

AutoDemoGroup = [
    cfg.StrOpt('auto_demo',
               default="hello_auto_demo",
               help="This is a demo")
]

_opts.append((auto_demo_group, AutoDemoGroup))

mq_host = "rabbitmq.cpt.com"
mq_port = 5672
customer_obj = customers.CustomersInfo(mq_host, mq_port)
info = customer_obj.parse()

changes = values.get_values(info)

# A demo of info is as follows
# info = {
#     "openstack": {
#         "ssh_host": "localhost",
#         "ssh_port": 22,
#         "ssh_username": "root",
#         "ssh_password": "admin123"
#     },
#     "customer": [
#         {
#             "auth": [{"test_accounts_file": "hello"}]
#         },
#         {"compute": []},
#         {"default": []}
#     ]
# }


# A demo of changes is as follows
# [
#     {
#         'auth':
#             [
#                 {'test_accounts_file': 'sangforcustomer_zombie_test'},
#                 {'allow_tenant_isolation': 'sangforcustomer_3'}
#             ]
#     },
#     {
#         'compute':
#             [
#                 {'image_ref': 'sangforcustomer_customer_image_ref'}
#             ]
#     }
# ]


def change_value(group, key, value, x_opts):
    temp_opts = []
    for g, o in x_opts:
        temp_o = []

        if (g is not None and g.name == group) or (g is None and group == "DEFAULT"):
            for opt in o:
                opt_name = opt.name
                t_opt_name = opt_name.replace("-", "_")
                if opt.name == key or t_opt_name == key:
                    opt.default = value
                temp_o.append(opt)
        else:
            temp_o = o
        temp_opts.append((g, temp_o))
    x_opts = temp_opts
    return x_opts


def change_values(changes, x_opts):

    for change in changes:
        for (group, kvs) in change.items():
            for kv in kvs:
                if len(kv) >= 0:
                    x_opts = change_value(
                        group, kv.keys()[0], kv.values()[0], x_opts)

    return x_opts


_opts = change_values(changes, _opts)


def register_opts():
    for g, o in _opts:
        register_opt_group(_CONF, g, o)


def change_opts_default():
    pass


def list_opts():
    """Return a list of oslo.config options available.

    The purpose of this is to allow tools like the Oslo sample config file
    generator to discover the options exposed to users.
    """
    return [(getattr(g, 'name', None), o) for g, o in _opts]


# this should never be called outside of this class
class AUTOTempestConfigPrivate(sf_config.SFTempestConfigPrivate):
    """Provides OpenStack configuration information."""
    def __init__(self, parse_conf=True, config_path=None):
        """Initialize a configuration from a conf directory and conf file."""
        # super(SFTempestConfigPrivate, self).__init__(parse_conf, config_path)
        config_files = []
        failsafe_path = "/etc/tempest/" + self.DEFAULT_CONFIG_FILE

        if config_path:
            path = config_path
        else:
            # Environment variables override defaults...
            conf_dir = os.environ.get('TEMPEST_CONFIG_DIR',
                                      self.DEFAULT_CONFIG_DIR)
            conf_file = os.environ.get('TEMPEST_CONFIG',
                                       self.DEFAULT_CONFIG_FILE)

            path = os.path.join(conf_dir, conf_file)

        if not os.path.isfile(path):
            path = failsafe_path

        # only parse the config file if we expect one to exist. This is needed
        # to remove an issue with the config file up to date checker.
        if parse_conf:
            config_files.append(path)
        logging.register_options(_CONF)
        if os.path.isfile(path):
            _CONF([], project='tempest', default_config_files=config_files)
        else:
            _CONF([], project='tempest')
        logging.setup(_CONF, 'tempest')
        LOG = logging.getLogger('tempest')
        LOG.info("Using tempest config file %s" % path)
        register_opts()
        self._set_attrs()
        if parse_conf:
            _CONF.log_opt_values(LOG, std_logging.DEBUG)


class AUTOTempestConfigProxy(sf_config.SFTempestConfigProxy):
    _config = None
    _path = None

    def __getattr__(self, attr):
        if not self._config:
            self._fix_log_levels()
            self._config = AUTOTempestConfigPrivate(config_path=self._path)

        return getattr(self._config, attr)


CONF = AUTOTempestConfigProxy()
