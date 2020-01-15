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

from resto_client.functions.feature_functions import create_features_from_ids
from resto_client.settings.resto_client_settings import RESTO_CLIENT_SETTINGS

from .cli_utils import build_resto_server_parameters, build_resto_client_params
from .parser_common import (features_in_collection_parser, credentials_parser, EPILOG_FEATURES,
                            server_nickname_parser)

# We need to specify argparse._SubParsersAction for mypy to run. Thus pylint squeals.
# pylint: disable=protected-access


def cli_show_settings(args: argparse.Namespace) -> None:
    """
    CLI adapter to show settings function

    :param args: arguments parsed by the CLI parser
    """
    _ = args  # to avoid pylint warning
    print(RESTO_CLIENT_SETTINGS)


def cli_show_collection(args: argparse.Namespace) -> None:
    """
    CLI adapter to list_collection function

    :param args: arguments parsed by the CLI parser
    """
    _ = build_resto_client_params(args)  # To retrieve verbosity level from CLI
    resto_server = build_resto_server_parameters(args).resto_server
    service = resto_server.resto_service
    collection = service.get_collection(collection=resto_server.current_collection)
    print(collection)
    if not args.nostats:
        print(collection.statistics)


def cli_show_server(args: argparse.Namespace) -> None:
    """
    CLI adapter to display server information: name, collections and statistics

    :param args: arguments parsed by the CLI parser
    :raises RestoClientUserError: when no current server defined.
    """
    unused_client_params = build_resto_client_params(args)  # To retrieve verbosity level from CLI
    service = build_resto_server_parameters(args).resto_server.resto_service
    print(service.show(with_stats=args.stats))


def cli_show_features(args: argparse.Namespace) -> None:
    """
    CLI adapter to show feature

    :param args: arguments parsed by the CLI parser
    """
    unused_client_params = build_resto_client_params(args)  # To retrieve verbosity level from CLI
    resto_server = build_resto_server_parameters(args).resto_server
    # TODO: Use collection from resto_server_parameters
    features = create_features_from_ids(resto_server, resto_server.current_collection,
                                        args.feature_id)

    for feature in features:
        print(feature)


def add_show_subparser(sub_parsers: argparse._SubParsersAction) -> None:
    """
    Add the 'show' subparser
    """
    parser_show = sub_parsers.add_parser('show', help='show resto_client entities: '
                                         'settings, server, collection, feature',
                                         description='Show different resto_client entities.')
    help_msg = 'For more help: {} show <entity> -h'
    sub_parsers_show = parser_show.add_subparsers(description=help_msg.format(parser_show.prog))

    add_show_settings_parser(sub_parsers_show)
    add_show_server_parser(sub_parsers_show)
    add_show_collection_parser(sub_parsers_show)
    add_show_feature_parser(sub_parsers_show)


def add_show_settings_parser(sub_parsers_show: argparse._SubParsersAction) -> None:
    """
    Update the 'show' command subparser with options for 'show settings'
    """
    subparser = sub_parsers_show.add_parser('settings', help='Show application settings',
                                            description='Show the currently defined settings.')
    subparser.set_defaults(func=cli_show_settings)


def add_show_collection_parser(sub_parsers_show: argparse._SubParsersAction) -> None:
    """
    Update the 'show' command subparser with options for 'show collection'
    """
    subparser = sub_parsers_show.add_parser('collection', help='Show the details of a collection',
                                            description='Show the details of a collection including'
                                            ' statistics on its content.',
                                            parents=[server_nickname_parser()])
    subparser.add_argument("collection_name", help="name of the collection to show", nargs='?')
    subparser.add_argument("--nostats", action="store_true", help="disable statistics details")
    subparser.set_defaults(func=cli_show_collection)


def add_show_server_parser(sub_parsers_show: argparse._SubParsersAction) -> None:
    """
    Update the 'show' command subparser with options for 'show server'
    """
    subparser = sub_parsers_show.add_parser('server', help='Show the server details',
                                            description='Show the server characteristics '
                                            'with its collections and optionally their statistics.'
                                            'If no server name is provided, the current server '
                                            'will be displayed.')
    subparser.add_argument("--stats", action="store_true", help="show collections statistics")
    subparser.add_argument("server_name", help="name of the server to explore", nargs='?')
    subparser.set_defaults(func=cli_show_server)


def add_show_feature_parser(sub_parsers_show: argparse._SubParsersAction) -> None:
    """
    Update the 'show' command subparser with options for 'show feature'
    """
    subparser = sub_parsers_show.add_parser('feature', help='Show feature details',
                                            description='Show the details of one or several '
                                            'features specified by their identifiers.',
                                            epilog=EPILOG_FEATURES,
                                            parents=[features_in_collection_parser(),
                                                     credentials_parser()])
    subparser.set_defaults(func=cli_show_features)
