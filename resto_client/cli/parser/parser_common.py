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
                              VERBOSITY_ARGNAME, FEATURES_IDS_ARGNAME, DIRECTORY_ARGNAME)

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


# TODO: parameterize by displaying system dependent directory or persisted directory
EPILOG_DOWNLOAD_DIR = '''
Download directory is used to download all the files. If no directory
is specified a default one is used, whose location depends on your system.
'''


def credentials_options_parser() -> ArgumentParser:
    """
    Creates a parser suitable to parse the credentials options for different subparsers
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--username', dest=ACCOUNT_ARGNAME, help='registered resto account')
    parser.add_argument('--password', dest=PASSWORD_ARGNAME, help='account password')
    return parser


def server_option_parser() -> ArgumentParser:
    """
    Creates a parser suitable to parse the server name option in different subparsers
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--server', dest=SERVER_ARGNAME,
                        help='name of the server to be used (default: current server)')
    return parser


def collection_option_parser() -> ArgumentParser:
    """
    Creates a parser suitable to parse the collection option in different subparsers
    """
    parser = ArgumentParser(add_help=False, parents=[server_option_parser()])
    parser.add_argument('--collection', dest=COLLECTION_ARGNAME,
                        help='name of the collection to use')
    return parser


def download_dir_option_parser() -> ArgumentParser:
    """
    Creates a parser suitable to parse the download_dir option in different subparsers
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--download_dir', dest=DIRECTORY_ARGNAME,
                        help='path to the directory where to download results')
    return parser


def features_ids_argument_parser() -> ArgumentParser:
    """
    Creates a parser suitable to parse the argument describing features ids in different subparsers
    """
    parser = ArgumentParser(add_help=False, parents=[collection_option_parser()])
    parser.add_argument(FEATURES_IDS_ARGNAME, nargs='+',
                        help='features identifiers or features UUIDs')
    return parser


def verbosity_option_parser() -> ArgumentParser:
    """
    Creates a parser suitable to parse the verbosity option in different subparsers
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--verbosity', dest=VERBOSITY_ARGNAME, type=str.upper,
                        choices=ALLOWED_VERBOSITY,
                        help='verbosity level to use for this command and subsequent ones.')
    return parser
