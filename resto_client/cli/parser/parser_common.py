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
from argparse import ArgumentParser
from typing import Tuple, Optional

from resto_client.cli.resto_client_parameters import ALLOWED_VERBOSITY, RestoClientParameters
from resto_client.cli.resto_server_persisted import RestoServerPersisted

from .parser_settings import (SERVER_ARGNAME, ACCOUNT_ARGNAME, PASSWORD_ARGNAME, COLLECTION_ARGNAME,
                              VERBOSITY_ARGNAME)

# Return type of all functions activated by argparse for resto_client CLI.
CliFunctionReturnType = Tuple[Optional[RestoClientParameters], Optional[RestoServerPersisted]]

EPILOG_IDENTIFIERS = '''
Identifiers can be expressed as digits only identifier or as UUID,
possibly mixed in the list.
'''

EPILOG_CREDENTIALS = '''
<username> and <password> options may be needed to access features
which are not visible to all users. If defined by this command,
they replace the persisted values and remain active for all subsequent
commands. If the <password> option is not provided but is needed for
submitting a request, it will be interactively requested.
'''
EPILOG_FEATURES = EPILOG_IDENTIFIERS + EPILOG_CREDENTIALS


def credentials_parser() -> ArgumentParser:
    """
    Creates a parser suitable to parse the credentials options for different subparsers
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--username', help='registered resto account', dest=ACCOUNT_ARGNAME)
    parser.add_argument('--password', help='account password', dest=PASSWORD_ARGNAME)
    return parser


def server_nickname_parser() -> ArgumentParser:
    """
    Creates a parser suitable to parse the server nickname option in different subparsers
    """
    parser = ArgumentParser(add_help=False, parents=[verbosity_option_parser()])
    parser.add_argument('--server', help='name of the server to be used (default: current server)',
                        dest=SERVER_ARGNAME)
    return parser


def collection_parser() -> ArgumentParser:
    """
    Creates a parser suitable to parse the collection option in different subparsers
    """
    parser = ArgumentParser(add_help=False, parents=[server_nickname_parser()])
    parser.add_argument('--collection', help='name of the collection to use',
                        dest=COLLECTION_ARGNAME)
    return parser


def features_in_collection_parser() -> ArgumentParser:
    """
    Creates a parser suitable to parse the options describing features in different subparsers
    """
    parser = ArgumentParser(add_help=False, parents=[collection_parser()])
    parser.add_argument('feature_id', help='features identifiers or features UUIDs', nargs='+')
    return parser


def verbosity_option_parser() -> ArgumentParser:
    """
    Creates a parser suitable to parse the verbosity option in different subparsers
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--verbosity',
                        help='verbosity level to use for this command and subsequent ones.',
                        choices=ALLOWED_VERBOSITY, type=str.upper, dest=VERBOSITY_ARGNAME)
    return parser
