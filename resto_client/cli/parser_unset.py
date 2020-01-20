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

from resto_client.cli.cli_utils import build_resto_client_params, build_resto_server_persistable


# We need to specify argparse._SubParsersAction for mypy to run. Thus pylint squeals.
# pylint: disable=protected-access
def cli_unset_server(args: argparse.Namespace) -> None:
    """
    CLI adapter to unset the persistent server parameters

    :param args: arguments parsed by the CLI parser
    """
    args.server_params = build_resto_server_persistable(args)
    args.server_params.server_name = None


def cli_unset_collection(args: argparse.Namespace) -> None:
    """
    CLI adapter to unset the persistent default collection to be used

    :param args: arguments parsed by the CLI parser
    """
    args.server_params = build_resto_server_persistable(args)
    args.server_params.current_collection = None


def cli_unset_account(args: argparse.Namespace) -> None:
    """
    CLI adapter to unset the default account to be used.

    :param args: arguments parsed by the CLI parser
    """
    args.server_params = build_resto_server_persistable(args)
    args.server_params.set_credentials(username=None)


def cli_unset_download_dir(args: argparse.Namespace) -> None:
    """
    CLI adapter to unset download directory to be used

    :param args: arguments parsed by the CLI parser
    """
    args.client_params = build_resto_client_params(args)
    args.client_params.download_dir = None  # type: ignore


def cli_unset_region(args: argparse.Namespace) -> None:
    """
    CLI adapter to unset region/AOI to be used

    :param args: arguments parsed by the CLI parser
    """
    args.client_params = build_resto_client_params(args)
    args.client_params.region = None  # type: ignore


def cli_unset_verbosity(args: argparse.Namespace) -> None:
    """
    CLI adapter to unset verbosity level

    :param args: arguments parsed by the CLI parser
    """
    args.client_params = build_resto_client_params(args)
    args.client_params.verbosity = None  # type: ignore


def add_unset_subparser(sub_parsers: argparse._SubParsersAction) -> None:
    """
    Add the 'unset' subparser
    """
    parser_unset = sub_parsers.add_parser('unset', help='unset application parameters: '
                                          'server, account, collection, download_dir, region, '
                                          'verbosity',
                                          description='Reset application parameters to their '
                                          ' default values.')
    help_msg = 'For more help: {} unset <parameter> -h'
    sub_parsers_unset = parser_unset.add_subparsers(description=help_msg.format(parser_unset.prog))

    add_unset_server_parser(sub_parsers_unset)
    add_unset_account_parser(sub_parsers_unset)
    add_unset_collection_parser(sub_parsers_unset)
    add_unset_download_dir_parser(sub_parsers_unset)
    add_unset_region(sub_parsers_unset)
    add_unset_verbosity(sub_parsers_unset)


def add_unset_server_parser(sub_parsers_unset: argparse._SubParsersAction) -> None:
    """
    Update the 'unset' command subparser with options for 'unset server'
    """
    subparser = sub_parsers_unset.add_parser('server', help='Unset the resto server to use',
                                             description='Unset the stored resto server.',
                                             epilog='The stored collection and account parameters '
                                             'are also unset by this command.')
    subparser.add_argument('server_name', help="name of the server to delete from database",
                           nargs='?')
    subparser.set_defaults(func=cli_unset_server)


def add_unset_collection_parser(sub_parsers_unset: argparse._SubParsersAction) -> None:
    """
    Update the 'unset' command subparser with options for 'unset collection'
    """
    subparser = sub_parsers_unset.add_parser('collection', help='Unset the collection to use',
                                             description='Unset the stored collection name.',)
    subparser.set_defaults(func=cli_unset_collection)


def add_unset_account_parser(sub_parsers_unset: argparse._SubParsersAction) -> None:
    """
    Update the 'unset' command subparser with options for 'unset account'
    """
    subparser = sub_parsers_unset.add_parser('account', help='Unset account to use',
                                             description='Unset the stored account.')
    subparser.set_defaults(func=cli_unset_account)


def add_unset_download_dir_parser(sub_parsers_unset: argparse._SubParsersAction) -> None:
    """
    Update the 'unset' command subparser with options for 'unset download_dir'
    """
    subparser = sub_parsers_unset.add_parser('download_dir', help='Unset download directory',
                                             description='Unset the stored download directory.')
    subparser.set_defaults(func=cli_unset_download_dir)


def add_unset_region(sub_parsers_unset: argparse._SubParsersAction) -> None:
    """
    Update the 'unset' command subparser with options for 'unset region'
    """
    subparser = sub_parsers_unset.add_parser('region', help='Unset region',
                                             description='Unset the stored region/AOI.')
    subparser.set_defaults(func=cli_unset_region)


def add_unset_verbosity(sub_parsers_unset: argparse._SubParsersAction) -> None:
    """
    Update the 'unset' command subparser with options for 'unset verbosity'
    """
    subparser = sub_parsers_unset.add_parser('verbosity', help='Unset verbosity',
                                             description='Unset the stored verbosity level.')
    subparser.set_defaults(func=cli_unset_verbosity)
