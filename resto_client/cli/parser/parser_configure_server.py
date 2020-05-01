# -*- coding: utf-8 -*-
"""
.. admonition:: License

   Copyright 2019 CNES

   Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
   in compliance with the License. You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software distributed under the License
   is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
   or implied. See the License for the specific language governing permissions and
   limitations under the License.
"""
import argparse

from resto_client.base_exceptions import RestoClientDesignError
from resto_client.services.service_access import (AuthenticationServiceAccess, RestoServiceAccess)
from resto_client.settings.resto_client_config import resto_client_print
from resto_client.settings.servers_database import DB_SERVERS

from .parser_common import CliFunctionReturnType
from .parser_settings import (SERVER_ARGNAME, RESTO_URL_ARGNAME, RESTO_PROTOCOL_ARGNAME,
                              AUTH_URL_ARGNAME, AUTH_PROTOCOL_ARGNAME)


def cli_create_server(args: argparse.Namespace) -> CliFunctionReturnType:
    """
    CLI adapter to create a server definition

    :param args: arguments parsed by the CLI parser
    :returns: the resto client parameters and the resto server possibly built by this command.
    """
    # TODO: Modify ServiceAcces such that lower is implemented in them
    resto_access = RestoServiceAccess(getattr(args, RESTO_URL_ARGNAME),
                                      getattr(args, RESTO_PROTOCOL_ARGNAME).lower())
    auth_access = AuthenticationServiceAccess(getattr(args, AUTH_URL_ARGNAME),
                                              getattr(args, AUTH_PROTOCOL_ARGNAME).lower())
    DB_SERVERS.create_server(getattr(args, SERVER_ARGNAME), resto_access, auth_access)
    return None, None


def cli_delete_server(args: argparse.Namespace) -> CliFunctionReturnType:
    """
    CLI adapter to delete a server definition

    :param args: arguments parsed by the CLI parser
    :returns: the resto client parameters and the resto server possibly built by this command.
    """
    DB_SERVERS.delete(getattr(args, SERVER_ARGNAME))
    return None, None


def cli_edit_server(args: argparse.Namespace) -> CliFunctionReturnType:
    """
    CLI adapter to edit the server characteristics

    :param args: arguments parsed by the CLI parser
    :raises RestoClientDesignError: unconditionally, as this function is not implemented yet
    """
    raise RestoClientDesignError('Edit server unimplemented')


def cli_show_servers(args: argparse.Namespace) -> CliFunctionReturnType:
    """
    CLI adapter to show the servers database

    :param args: arguments parsed by the CLI parser
    :returns: the resto client parameters and the resto server possibly built by this command.
    """
    _ = args  # to avoid pylint warning
    resto_client_print(DB_SERVERS)
    return None, None


# We need to specify argparse._SubParsersAction for mypy to run. Thus pylint squeals.
# pylint: disable=protected-access
def add_configure_server_subparser(sub_parsers: argparse._SubParsersAction) -> None:
    """
    Add the 'configure_server' subparser

    :param sub_parsers: argparse object used to add a parser for that subcommand.
    """
    parser_configure_server = sub_parsers.add_parser(
        'configure_server', help='configure servers known by resto_client.',
        description='Allows to create, modify or delete servers characteristics: url, type, etc.',
        epilog='Servers definition is stored in a configuration file and can be edited using this'
        ' command.')
    help_msg = 'For more help: {} <parameter> -h'.format(parser_configure_server.prog)
    sub_parsers_configure_server = parser_configure_server.add_subparsers(description=help_msg)

    add_config_server_create_parser(sub_parsers_configure_server)
    add_config_server_delete_parser(sub_parsers_configure_server)
    add_config_server_edit_parser(sub_parsers_configure_server)
    add_config_server_show_parser(sub_parsers_configure_server)


def add_config_server_create_parser(
        sub_parsers_configure_server: argparse._SubParsersAction) -> None:
    """
    Update the 'configure_server' command subparser with options for 'configure_server create'

    :param sub_parsers_configure_server: argparse object used to add a parser for that subcommand.
    """
    subparser = sub_parsers_configure_server.add_parser(
        'create', help='create a new server',
        description='Create a new server in the servers configuration database.')
    _add_positional_args_parser(subparser)
    subparser.set_defaults(func=cli_create_server)


def add_config_server_delete_parser(
        sub_parsers_configure_server: argparse._SubParsersAction) -> None:
    """
    Update the 'configure_server' command subparser with options for 'configure_server delete'

    :param sub_parsers_configure_server: argparse object used to add a parser for that subcommand.
    """
    subparser = sub_parsers_configure_server.add_parser(
        'delete', help='delete an existing server',
        description='Delete a server from the configuration database.')
    subparser.add_argument(SERVER_ARGNAME, help='name of the server to delete')
    subparser.set_defaults(func=cli_delete_server)


def add_config_server_edit_parser(
        sub_parsers_configure_server: argparse._SubParsersAction) -> None:
    """
    Update the 'configure_server' command subparser with options for 'configure_server edit'

    :param sub_parsers_configure_server: argparse object used to add a parser for that subcommand.
    """
    subparser = sub_parsers_configure_server.add_parser(
        'edit', help='edit server characteristics',
        description='Edit the characteristics of a server existing in the configuration database.')
    _add_positional_args_parser(subparser)
    subparser.set_defaults(func=cli_edit_server)


def add_config_server_show_parser(
        sub_parsers_configure_server: argparse._SubParsersAction) -> None:
    """
    Update the 'configure_server' command subparser with options for 'configure_server show'

    :param sub_parsers_configure_server: argparse object used to add a parser for that subcommand.
    """
    subparser = sub_parsers_configure_server.add_parser(
        'show', help='show servers database',
        description='Show all the servers defined in the database with their configuration.')
    subparser.set_defaults(func=cli_show_servers)


def _add_positional_args_parser(subparser: argparse.ArgumentParser) -> None:
    """
    Add the positional arguments parsing rules for configure_server subcommands

    :param subparser: parser to be supplemented with positional arguments.
    """
    subparser.add_argument(SERVER_ARGNAME, help='name of the server')
    group_resto = subparser.add_argument_group('resto service')
    group_resto.add_argument(RESTO_URL_ARGNAME, help='URL of the resto server')
    group_resto.add_argument(RESTO_PROTOCOL_ARGNAME,
                             choices=RestoServiceAccess.supported_protocols(),
                             help='Protocol of the resto server')
    group_auth = subparser.add_argument_group('authentication service')
    group_auth.add_argument(AUTH_URL_ARGNAME, nargs='?', help='URL of the authentication server')
    group_auth.add_argument(AUTH_PROTOCOL_ARGNAME,
                            choices=AuthenticationServiceAccess.supported_protocols(),
                            help='Protocol of the authentication server')
