# Copyright 2012 OpenStack Foundation
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

from __future__ import print_function

import logging as std_logging
import os

from oslo_config import cfg

from oslo_log import log as logging

import config

# TODO(marun) Replace use of oslo_config's global ConfigOpts
# (cfg.CONF) instance with a local instance (cfg.ConfigOpts()) once
# the cli tests move to the clients.  The cli tests rely on oslo
# incubator modules that use the global cfg.CONF.
_CONF = cfg.CONF


sf_ext_group = cfg.OptGroup(name='sf_ext',
                          title="Used to extend for sangfor")

SfExtGroup = [
    cfg.StrOpt('sf_ext_demo',
               default="hello_sf_ext_demo",
               help="This is a sangfor ext config demo for StrOpt"),
    cfg.BoolOpt('sf_ext_demo_bool',
                default=True,
                help="This is a sangfor ext config demo for BoolOpt",),
    cfg.ListOpt('sf_ext_demo_list',
                help="This is a sangfor ext config demo for BoolOpt",
                default=[])
]

oslo_currency_group = cfg.OptGroup(name='oslo_concurrency',
                          title="Used to extend for oslo_currency")
OsloConcurrencyGroup = [
    cfg.BoolOpt('disable_process_locking', default=False,
                help='Enables or disables inter-process locks.',
                deprecated_group='DEFAULT'),
    cfg.StrOpt('lock_path',
               default=os.environ.get("OSLO_LOCK_PATH"),
               help='Directory to use for lock files.  For security, the '
                    'specified directory should only be writable by the user '
                    'running the processes that need locking. '
                    'Defaults to environment variable OSLO_LOCK_PATH. '
                    'If external locks are used, a lock path must be set.',
               deprecated_group='DEFAULT')
]


_opts = [
    (sf_ext_group, SfExtGroup),
    (oslo_currency_group, OsloConcurrencyGroup)
]


def list_opts():
    """Return a list of oslo.config options available.

    The purpose of this is to allow tools like the Oslo sample config file
    generator to discover the options exposed to users.
    """
    return [(getattr(g, 'name', None), o) for g, o in _opts]


# this should never be called outside of this class
class SFTempestConfigPrivate(config.TempestConfigPrivate):
    """Provides OpenStack configuration information."""

    def _set_attrs(self):
        self.sf_ext = _CONF.sf_ext
        self.sf_notify = _CONF.sf_notify
        self.auth = _CONF.auth

    def __init__(self, parse_conf=True, config_path=None):
        """Initialize a configuration from a conf directory and conf file."""
        super(SFTempestConfigPrivate, self).__init__(parse_conf, config_path)


class SFTempestConfigProxy(config.TempestConfigProxy):
    _config = None
    _path = None

    def __getattr__(self, attr):
        if not self._config:
            self._fix_log_levels()
            self._config = SFTempestConfigPrivate(config_path=self._path)

        return getattr(self._config, attr)


CONF = SFTempestConfigProxy()
