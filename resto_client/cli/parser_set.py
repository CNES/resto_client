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

from resto_client.functions.aoi_utils import find_region_choice
from resto_client.settings.resto_client_parameters import ALLOWED_VERBOSITY

from .cli_utils import build_resto_client_params, build_resto_server


# We need to specify argparse._SubParsersAction for mypy to run. Thus pylint squeals.
# pylint: disable=protected-access
def cli_set_server(args: argparse.Namespace) -> None:
    """
    CLI adapter to set the persistent server parameters

    :param args: arguments parsed by the CLI parser
    """
    unused_server = build_resto_server(args)


def cli_set_collection(args: argparse.Namespace) -> None:
    """
    CLI adapter to set the collection to use

    :param args: arguments parsed by the CLI parser
    """
    service = build_resto_server(args).resto_service
    service.current_collection = args.collection


def cli_set_account(args: argparse.Namespace) -> None:
    """
    CLI adapter to set the account to use

    :param args: arguments parsed by the CLI parser
    """
    unused_server = build_resto_server(args)


def cli_set_download_dir(args: argparse.Namespace) -> None:
    """
    CLI adapter to set the default download directory

    :param args: arguments parsed by the CLI parser
    """
    client_params = build_resto_client_params(args)
    client_params.download_dir = args.path  # type: ignore


def cli_set_region(args: argparse.Namespace) -> None:
    """
    CLI adapter to set the default region/AOI for search

    :param args: arguments parsed by the CLI parser
    """
    client_params = build_resto_client_params(args)
    client_params.region = args.region  # type: ignore


def cli_set_verbosity(args: argparse.Namespace) -> None:
    """
    CLI adapter to set the verbosity level

    :param args: arguments parsed by the CLI parser
    """
    client_params = build_resto_client_params(args)
    client_params.verbosity = args.verbosity  # type: ignore


def add_set_subparser(sub_parsers: argparse._SubParsersAction) -> None:
    """
    Add the 'set' subparser
    """
    parser_set = sub_parsers.add_parser('set', help='set application parameters: '
                                        'server, account, collection, download_dir, region, '
                                        ' verbosity',
                                        description='Set application parameters to be used by '
                                        ' subsequent commands.',
                                        epilog='Above parameters are stored in a configuration '
                                        'file and are retrieved from this file when a command '
                                        'needs them. Their values remain in use until they are '
                                        'changed by issuing another set command or '
                                        'by providing their new value through commands options. '
                                        'See the unset subcommand to restore their default values.')
    help_msg = 'For more help: {} set <parameter> -h'
    sub_parsers_set = parser_set.add_subparsers(description=help_msg.format(parser_set.prog))

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
                                           description='Set the resto server to use.')
    subparser.add_argument("server_name", help="name of the resto server")
    subparser.set_defaults(func=cli_set_server)


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
    # We can't used collection parent here because collection is here mandatory
    subparser.add_argument("collection", help="name of the collection to be used")
    subparser.set_defaults(func=cli_set_collection)


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
    subparser.add_argument("username", help="server account to use for subsequent requests")
    subparser.set_defaults(func=cli_set_account)


def add_set_download_dir_parser(sub_parser_set: argparse._SubParsersAction) -> None:
    """
    Update the 'set' command subparser with options for 'set download_dir'
    """
    subparser = sub_parser_set.add_parser('download_dir', help='Set download directory to use',
                                          description='Set the download directory to use in '
                                          'subsequent download.',
                                          epilog='The path need to exist to be operational.')
    subparser.add_argument("path", help="full path of the directory to use for download")
    subparser.set_defaults(func=cli_set_download_dir)


def add_set_region_parser(sub_parser_set: argparse._SubParsersAction) -> None:
    """
    Update the 'set' command subparser with options for 'set region'
    """
    subparser = sub_parser_set.add_parser('region', help='Set region/AOI for search',
                                          description='Set the region/area of interest to use in '
                                          'subsequent search.',
                                          epilog='Region s file .geojson must be present in zones '
                                          'folder')
    region_choices = find_region_choice()
    subparser.add_argument('region', help='the chosen key-word will search for the corresponding '
                           'file in the appropriate folder', choices=region_choices, type=str.lower)
    subparser.set_defaults(func=cli_set_region)


def add_set_verbosity_parser(sub_parser_set: argparse._SubParsersAction) -> None:
    """
    Update the 'set' command subparser with options for 'set verbosity'
    """
    subparser = sub_parser_set.add_parser('verbosity', help='Set verbosity level for resto_client',
                                          description='Set the verbosity level to use throughout '
                                          'resto_client.')
    subparser.add_argument('verbosity', help='the verbosity level', choices=ALLOWED_VERBOSITY,
                           type=str.upper)
    subparser.set_defaults(func=cli_set_verbosity)
