# -*- coding: utf-8 -*-
"""
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

from resto_client.cli.resto_client_parameters import RestoClientParameters, ALLOWED_VERBOSITY
from resto_client.cli.resto_server_persisted import RestoServerPersisted
from resto_client.functions.aoi_utils import find_region_choice

from .parser_common import CliFunctionReturnType
from .parser_settings import (SERVER_ARGNAME, ACCOUNT_ARGNAME, COLLECTION_ARGNAME,
                              DIRECTORY_ARGNAME, REGION_ARGNAME, VERBOSITY_ARGNAME)


def cli_set_server_parameter(args: argparse.Namespace) -> CliFunctionReturnType:
    """
    CLI adapter to set the persistent server parameters

    Parameters which can be set must belong to RestoServerPersisted.persisted_attributes list.
    They must appear with this exact name in the argparse.Namespace argument. However they can
    be absent or equal to None.

    :param args: arguments parsed by the CLI parser
    :returns: the resto client parameters and the resto server possibly built by this command.
    """
    resto_server = RestoServerPersisted.build_from_argparse(
        args, debug_server=RestoClientParameters.is_debug())
    return None, resto_server


def cli_set_client_parameter(args: argparse.Namespace) -> CliFunctionReturnType:
    """
    CLI adapter to set the persistent client parameters

    Parameters which can be set must belong to RestoClientParameters.persisted_attributes list.
    They must appear with this exact name in the argparse.Namespace argument. However they can
    be absent or equal to None.

    :param args: arguments parsed by the CLI parser
    :returns: the resto client parameters and the resto server possibly built by this command.
    """
    client_params = RestoClientParameters.build_from_argparse(args)
    return client_params, None


# We need to specify argparse._SubParsersAction for mypy to run. Thus pylint squeals.
# pylint: disable=protected-access
def add_set_subparser(sub_parsers: argparse._SubParsersAction) -> None:
    """
    Add the 'set' subparser
    """
    parser_set = sub_parsers.add_parser('set', help='set application parameters.',
                                        description='Set application parameters to be used by '
                                        ' subsequent commands.',
                                        epilog='Above parameters are stored in a configuration '
                                        'file and are retrieved from this file when a command '
                                        'needs them. Their values remain in use until they are '
                                        'changed by issuing another set command or '
                                        'by providing their new value through commands options. '
                                        'See the unset subcommand to restore their default values.')
    help_msg = 'For more help: {} <parameter> -h'.format(parser_set.prog)
    sub_parsers_set = parser_set.add_subparsers(description=help_msg)

    add_set_server_parser(sub_parsers_set)
    add_set_account_parser(sub_parsers_set)
    add_set_collection_parser(sub_parsers_set)
    add_set_download_dir_parser(sub_parsers_set)
    add_set_region_parser(sub_parsers_set)
    add_set_verbosity_parser(sub_parsers_set)


def add_set_server_parser(sub_parsers_set: argparse._SubParsersAction) -> None:
    """
    Update the 'set' command subparser with options for 'set server'
    """
    subparser = sub_parsers_set.add_parser('server', help='Set the resto server to use',
                                           description='Set the resto server to use in subsequent'
                                           ' commands.')
    subparser.add_argument(SERVER_ARGNAME, help='name of the resto server')
    subparser.set_defaults(func=cli_set_server_parameter)


def add_set_collection_parser(sub_parsers_set: argparse._SubParsersAction) -> None:
    """
    Update the 'set' command subparser with options for 'set collection'
    """
    subparser = sub_parsers_set.add_parser('collection', help='Set the collection to use',
                                           description='Set the collection to use in subsequent '
                                           'commands.',
                                           epilog='If the collection does not exist in the current '
                                           'server, an error is issued and the previously stored '
                                           'collection is kept unmodified.')
    subparser.add_argument(COLLECTION_ARGNAME, help='name of the collection to use')
    subparser.set_defaults(func=cli_set_server_parameter)


def add_set_account_parser(sub_parser_set: argparse._SubParsersAction) -> None:
    """
    Update the 'set' command subparser with options for 'set account'
    """
    subparser = sub_parser_set.add_parser('account', help='Set the account to use',
                                          description='Set the account to use in subsequent '
                                          'commands.',
                                          epilog='The account set by this command is not checked '
                                          'immediately. If it is not allowed on '
                                          'the server an error will be issued by the first '
                                          'command which will try to use it.')
    subparser.add_argument(ACCOUNT_ARGNAME, help='server account to use for subsequent requests')
    subparser.set_defaults(func=cli_set_server_parameter)


def add_set_download_dir_parser(sub_parser_set: argparse._SubParsersAction) -> None:
    """
    Update the 'set' command subparser with options for 'set download_dir'
    """
    subparser = sub_parser_set.add_parser('download_dir', help='Set download directory',
                                          description='Set the download directory to use in '
                                          'subsequent commands.',
                                          epilog='This directory will not be created by '
                                          'resto_client and must exist before being used.')
    subparser.add_argument(DIRECTORY_ARGNAME, help='full path of the directory to use for download')
    subparser.set_defaults(func=cli_set_client_parameter)


def add_set_region_parser(sub_parser_set: argparse._SubParsersAction) -> None:
    """
    Update the 'set' command subparser with options for 'set region'
    """
    subparser = sub_parser_set.add_parser('region', help='Set region/AOI for search',
                                          description='Set the region/area of interest to use in '
                                          'subsequent search requests.',
                                          epilog='Region can be one of the regions described by'
                                          ' geojson files in the internal zones database.')
    region_choices = find_region_choice()
    subparser.add_argument(REGION_ARGNAME, choices=region_choices, type=str.lower,
                           help='name of the region to use from the predefined zones database')
    subparser.set_defaults(func=cli_set_client_parameter)


def add_set_verbosity_parser(sub_parser_set: argparse._SubParsersAction) -> None:
    """
    Update the 'set' command subparser with options for 'set verbosity'
    """
    subparser = sub_parser_set.add_parser('verbosity', help='Set verbosity level for resto_client',
                                          description='Set the verbosity level to use in '
                                          'subsequent commands.')
    subparser.add_argument(VERBOSITY_ARGNAME, type=str.upper, choices=ALLOWED_VERBOSITY,
                           help='the verbosity level')
    subparser.set_defaults(func=cli_set_client_parameter)
