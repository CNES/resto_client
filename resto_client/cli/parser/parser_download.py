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
from pathlib import Path

from resto_client.cli.resto_client_parameters import RestoClientParameters
from resto_client.cli.resto_server_persisted import RestoServerPersisted

from .parser_common import (credentials_options_parser, features_ids_argument_parser,
                            download_dir_option_parser, CliFunctionReturnType,
                            EPILOG_DOWNLOAD_DIR, EPILOG_FEATURES)

from .parser_settings import FEATURES_IDS_ARGNAME, DOWNLOAD_TYPE_ARGNAME


def cli_download_files(args: argparse.Namespace) -> CliFunctionReturnType:
    """
    CLI adapter to download_features_file_from_ids used by product, quicklook, thumbnail and annexes
    download sub-commands.

    :param args: arguments parsed by the CLI parser
    :returns: the resto client parameters and the resto server possibly built by this command.
    """
    client_params = RestoClientParameters.build_from_argparse(args)
    resto_server = RestoServerPersisted.build_from_argparse(
        args, debug_server=RestoClientParameters.is_debug())
    resto_server.download_features_file_from_ids(getattr(args, FEATURES_IDS_ARGNAME),
                                                 getattr(args, DOWNLOAD_TYPE_ARGNAME),
                                                 Path(client_params.download_dir))
    return client_params, resto_server


# We need to specify argparse._SubParsersAction for mypy to run. Thus pylint squeals.
# pylint: disable=protected-access
def add_download_subparser(sub_parsers: argparse._SubParsersAction) -> None:
    """
    Add the 'download' subparser
    """
    parser_download = sub_parsers.add_parser('download', help='download features files.',
                                             description='Download feature files from the server.')
    help_msg = 'For more help: {} <file-type> -h'.format(parser_download.prog)
    sub_parsers_download = parser_download.add_subparsers(description=help_msg,
                                                          dest=DOWNLOAD_TYPE_ARGNAME)

    add_download_product_parser(sub_parsers_download)
    add_download_quicklook_parser(sub_parsers_download)
    add_download_thumbnail_parser(sub_parsers_download)
    add_download_annexes_parser(sub_parsers_download)


def add_download_product_parser(sub_parsers_download: argparse._SubParsersAction) -> None:
    """
    Update the 'download' command subparser with options for 'download product'
    """
    # download product subparser
    subparser = sub_parsers_download.add_parser('product', help='Download feature(s) product(s)',
                                                description='Download product archive(s) '
                                                'corresponding to one or several features '
                                                'specified by their identifiers.',
                                                epilog=EPILOG_FEATURES + EPILOG_DOWNLOAD_DIR,
                                                parents=[features_ids_argument_parser(),
                                                         credentials_options_parser(),
                                                         download_dir_option_parser()])
    subparser.set_defaults(func=cli_download_files)


def add_download_quicklook_parser(sub_parsers_download: argparse._SubParsersAction) -> None:
    """
    Update the 'download' command subparser with options for 'download quicklook'
    """
    subparser = sub_parsers_download.add_parser('quicklook',
                                                help='Download feature(s) quicklook(s)',
                                                description='Download quicklook image(s) '
                                                'corresponding to one or several features '
                                                'specified by their identifiers.',
                                                epilog=EPILOG_FEATURES + EPILOG_DOWNLOAD_DIR,
                                                parents=[features_ids_argument_parser(),
                                                         credentials_options_parser(),
                                                         download_dir_option_parser()])
    subparser.set_defaults(func=cli_download_files)


def add_download_thumbnail_parser(sub_parsers_download: argparse._SubParsersAction) -> None:
    """
    Update the 'download' command subparser with options for 'download thumbnail'
    """
    subparser = sub_parsers_download.add_parser('thumbnail',
                                                help='Download feature(s) thumbnail(s)',
                                                description='Download thumbnail image(s) '
                                                'corresponding to one or several features '
                                                'specified by their identifiers.',
                                                epilog=EPILOG_FEATURES + EPILOG_DOWNLOAD_DIR,
                                                parents=[features_ids_argument_parser(),
                                                         credentials_options_parser(),
                                                         download_dir_option_parser()])
    subparser.set_defaults(func=cli_download_files)


def add_download_annexes_parser(sub_parsers_download: argparse._SubParsersAction) -> None:
    """
    Update the 'download' command subparser with options for 'download annexes'
    """
    subparser = sub_parsers_download.add_parser('annexes', help='Download feature(s) annex(es)',
                                                description='Download annexes html(s) '
                                                'corresponding to one or several features '
                                                'specified by their identifiers.',
                                                epilog=EPILOG_FEATURES + EPILOG_DOWNLOAD_DIR,
                                                parents=[features_ids_argument_parser(),
                                                         credentials_options_parser(),
                                                         download_dir_option_parser()])
    subparser.set_defaults(func=cli_download_files)
