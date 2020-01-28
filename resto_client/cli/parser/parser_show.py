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

from resto_client.cli.resto_client_parameters import RestoClientParameters
from resto_client.cli.resto_client_settings import RESTO_CLIENT_SETTINGS
from resto_client.cli.resto_server_persisted import RestoServerPersisted

from .parser_common import (features_ids_argument_parser, credentials_options_parser,
                            EPILOG_FEATURES, server_option_parser, CliFunctionReturnType)
from .parser_settings import (SERVER_ARGNAME, COLLECTION_ARGNAME, FEATURES_IDS_ARGNAME,
                              WITH_STATS_ARGNAME, NO_STATS_ARGNAME)


def cli_show_settings(args: argparse.Namespace) -> CliFunctionReturnType:
    """
    CLI adapter to show settings function

    :param args: arguments parsed by the CLI parser
    :returns: the resto client parameters and the resto server possibly built by this command.
    """
    _ = args  # to avoid pylint warning
    print(RESTO_CLIENT_SETTINGS)
    return None, None


def cli_show_collection(args: argparse.Namespace) -> CliFunctionReturnType:
    """
    CLI adapter to list_collection function

    :param args: arguments parsed by the CLI parser
    :raises RestoClientUserError: when the resto service is not initialized
    :returns: the resto client parameters and the resto server possibly built by this command.
    """
    resto_server = RestoServerPersisted.build_from_argparse(
        args, debug_server=RestoClientParameters.is_debug())
    collection = resto_server.get_collection()
    print(collection)
    if not getattr(args, NO_STATS_ARGNAME):
        print(collection.statistics)
    return None, resto_server


def cli_show_server(args: argparse.Namespace) -> CliFunctionReturnType:
    """
    CLI adapter to display server information: name, collections and statistics

    :param args: arguments parsed by the CLI parser
    :raises RestoClientUserError: when no current server defined.
    :returns: the resto client parameters and the resto server possibly built by this command.
    """
    resto_server = RestoServerPersisted.build_from_argparse(
        args, debug_server=RestoClientParameters.is_debug())
    server_description = resto_server.show_server(with_stats=getattr(args, WITH_STATS_ARGNAME))
    print(server_description)
    return None, resto_server


def cli_show_features(args: argparse.Namespace) -> CliFunctionReturnType:
    """
    CLI adapter to show feature

    :param args: arguments parsed by the CLI parser
    :returns: the resto client parameters and the resto server possibly built by this command.
    """
    resto_server = RestoServerPersisted.build_from_argparse(
        args, debug_server=RestoClientParameters.is_debug())
    features = resto_server.get_features_from_ids(getattr(args, FEATURES_IDS_ARGNAME))
    for feature in features:
        print(feature)
    return None, resto_server


# We need to specify argparse._SubParsersAction for mypy to run. Thus pylint squeals.
# pylint: disable=protected-access
def add_show_subparser(sub_parsers: argparse._SubParsersAction) -> None:
    """
    Add the 'show' subparser
    """
    parser_show = sub_parsers.add_parser('show', help='show different server and client entities.',
                                         description='Show different resto_client entities.')
    help_msg = 'For more help: {} <entity> -h'.format(parser_show.prog)
    sub_parsers_show = parser_show.add_subparsers(description=help_msg)

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
                                            parents=[server_option_parser()])
    subparser.add_argument(COLLECTION_ARGNAME, nargs='?', help='name of the collection to show')
    subparser.add_argument('--nostats', dest=NO_STATS_ARGNAME, action='store_true',
                           help='disable statistics details')
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
    subparser.add_argument('--stats', dest=WITH_STATS_ARGNAME, action='store_true',
                           help='show collections statistics')
    subparser.add_argument(SERVER_ARGNAME, nargs='?', help='name of the server to display')
    subparser.set_defaults(func=cli_show_server)


def add_show_feature_parser(sub_parsers_show: argparse._SubParsersAction) -> None:
    """
    Update the 'show' command subparser with options for 'show feature'
    """
    subparser = sub_parsers_show.add_parser('feature', help='Show feature details',
                                            description='Show the details of one or several '
                                            'features specified by their identifiers.',
                                            epilog=EPILOG_FEATURES,
                                            parents=[features_ids_argument_parser(),
                                                     credentials_options_parser()])
    subparser.set_defaults(func=cli_show_features)
