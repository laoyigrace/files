# Copyright 2012 SINA Corporation
# Copyright 2014 Cisco Systems, Inc.
# All Rights Reserved.
# Copyright 2014 Red Hat, Inc.
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

"""Sample configuration generator

Tool for generating a sample configuration file. See
../doc/source/generator.rst for details.

"""

import logging
import operator
import sys
import stevedore

import pkg_resources

from oslo_config import cfg
from oslo_config import generator as gen

LOG = logging.getLogger(__name__)

_generator_opts = [
    cfg.StrOpt('output-file',
               help='Path of the file to write to. Defaults to stdout.'),
    cfg.IntOpt('wrap-width',
               default=70,
               help='The maximum length of help lines.'),
    cfg.MultiStrOpt('namespace',
                    help='Option namespace under "oslo.config.opts" in which '
                         'to query for options.'),
]

_customer_opts = [
    cfg.StrOpt('customer-file',
               default='hello',
               help='Path of file to get the customer form webui '
                    'or something like that'),
]


def register_cli_opts(conf):
    """Register the formatter's CLI options with a ConfigOpts instance.

    Note, this must be done before the ConfigOpts instance is called to parse
    the configuration.

    :param conf: a ConfigOpts instance
    :raises: DuplicateOptError, ArgsAlreadyParsedError
    """
    conf.register_cli_opts(_generator_opts)
    conf.register_cli_opts(_customer_opts)


def on_load_failure_callback(*args, **kwargs):
    raise


def get_changes(conf):
    customer_file = (open(conf.customer_file, 'r'))
    content = customer_file.read()
    customer_file.close()

    return content


def _list_opts(namespaces):
    """List the options available via the given namespaces.

    :param namespaces: a list of namespaces registered under 'oslo.config.opts'
    :returns: a list of (namespace, [(group, [opt_1, opt_2])]) tuples
    """
    mgr = stevedore.named.NamedExtensionManager(
        'tac.generator.opts',
        names=namespaces,
        on_load_failure_callback=on_load_failure_callback,
        invoke_on_load=True)
    return [(ep.name, ep.obj) for ep in mgr]


def merge_opts(s_opts, d_opts):
    return d_opts


def generate(conf):
    """Generate a sample config file.

    List all of the options available via the namespaces specified in the given
    configuration and write a description of them to the specified output file.

    :param conf: a ConfigOpts instance containing the generator's configuration
    """
    conf.register_opts(_generator_opts)
    conf.register_opts(_customer_opts)

    output_file = (open(conf.output_file, 'w')
                   if conf.output_file else sys.stdout)

    formatter = gen._OptFormatter(output_file=output_file,
                                  wrap_width=conf.wrap_width)

    _opts = gen._list_opts(conf.namespace)

    groups = {'DEFAULT': []}
    for namespace, listing in _opts:
        for group, opts in listing:
            if not opts:
                continue
            namespaces = groups.setdefault(group or 'DEFAULT', [])
            namespaces.append((namespace, opts))

    def _output_opts(f, group, namespaces):
        if isinstance(group, cfg.OptGroup):
            group_name = group.name
        else:
            group_name = group

        f.write('[%s]\n' % group_name)

        for (namespace, opts) in sorted(namespaces,
                                        key=operator.itemgetter(0)):
            f.write('\n#\n# From %s\n#\n' % namespace)
            for opt in opts:
                f.write('\n')
                f.format(opt)

    _output_opts(formatter, 'DEFAULT', groups.pop('DEFAULT'))
    for group, namespaces in sorted(groups.items(),
                                    key=operator.itemgetter(0)):
        formatter.write('\n\n')
        _output_opts(formatter, group, namespaces)


def main(args=None):
    """The main function of oslo-config-generator."""
    version = pkg_resources.get_distribution('oslo.config').version
    logging.basicConfig(level=logging.WARN)
    conf = cfg.ConfigOpts()
    register_cli_opts(conf)
    conf(args, version=version)
    generate(conf)


if __name__ == '__main__':
    main()
