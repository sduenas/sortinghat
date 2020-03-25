# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2020 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#

import functools
import os.path

import click
import jinja2


from .client import SortingHatClient


_conn_options = [
    click.option('-u', '--user',
                 help="Name of the user to authenticate on the server."),
    click.option('-p', '--password',
                 help="Password to authenticate on the server."),
    click.option('--host',
                 default='localhost',
                 show_default=True,
                 help="Address to use for connection."),
    click.option('--port',
                 default=9314,
                 show_default=True,
                 help="Port number to use for connection."),
    click.option('--server-path',
                 show_default=True,
                 help="Path to the server API."),
    click.option('--disable-ssl',
                 is_flag=True,
                 help="Disable SSL/TSL connection.")
]


def sh_client_cmd_options(func):
    """Decorator to add options to a command to initialize a client."""

    for option in reversed(_conn_options):
        func = option(func)
    return func


def sh_client(func):
    """Decorator to initialize a SortingHat client.

    This decorator initializes a client that will be
    available in the context object.
    """
    @click.pass_context
    def initialize_client(ctx, *args, **kwargs):
        use_ssl = not kwargs['disable_ssl']

        # Create a client object and remember it as as the context object.
        client = SortingHatClient(kwargs['host'], port=kwargs['port'],
                                  path=kwargs['server_path'],
                                  user=kwargs['user'], password=kwargs['password'],
                                  ssl=use_ssl)
        ctx.obj = client

        return ctx.invoke(func, ctx, *args, **kwargs)
    return functools.update_wrapper(initialize_client, func)


def display(template, nl=True, **kwargs):
    """Render and display a template.

    Giving the name of a template with the parameter `template`,
    this function will locate and render it using the arguments
    passed as keywords.

    :param template: name of the template
    :param nl: if set to `True`, it renders a newline afterwards
    :param kwargs: list of attributes required to render the template
    """
    templates_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates")
    loader = jinja2.FileSystemLoader(templates_dir)
    env = jinja2.Environment(loader=loader,
                             lstrip_blocks=True, trim_blocks=True)

    t = env.get_template(template)
    s = t.render(**kwargs)
    click.echo(s, nl=nl)
