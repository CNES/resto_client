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
from pathlib import Path

from resto_client.functions.feature_functions import download_features_files_from_id

from .cli_utils import build_resto_client_params, build_resto_server
from .parser_common import credentials_parser, features_in_collection_parser, EPILOG_FEATURES

# We need to specify argparse._SubParsersAction for mypy to run. Thus pylint squeals.
# pylint: disable=protected-access

EPILOG_DOWNLOAD_DIR = '''
Download directory is used to download all the files. If no directory
is specified a default one is used, whose location depends on your system.
'''


def cli_download_files(args: argparse.Namespace) -> None:
    """
    CLI adapter to download_features_files_from_id used by product, quicklook, thumbnail and annexes
    download sub-commands.

    :param args: arguments parsed by the CLI parser
    :type args: :class:`argparse.Namespace`
    """
    client_params = build_resto_client_params(args)
    resto_service = build_resto_server(args).resto_service
    download_features_files_from_id(resto_service, args.collection, args.feature_id,
                                    args.download_type, Path(client_params.download_dir))


def add_download_subparser(sub_parsers: argparse._SubParsersAction) -> None:
    """
    Add the 'download' subparser
    """
    parser_download = sub_parsers.add_parser('download', help='download features files: '
                                             'product, quicklook, thumbnail or annexes',
                                             description='Download feature files from the server.')
    help_msg = 'For more help: {} download <feature-file> -h'
    sub_parsers_download = parser_download.add_subparsers(
        description=help_msg.format(parser_download.prog), dest='download_type')

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
                                                parents=[features_in_collection_parser(),
                                                         credentials_parser()])
    subparser.add_argument("--directory", help="directory for download")
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
                                                parents=[features_in_collection_parser(),
                                                         credentials_parser()])
    subparser.add_argument("--directory", help="directory for download")
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
                                                parents=[features_in_collection_parser(),
                                                         credentials_parser()])
    subparser.add_argument("--directory", help="directory for download")
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
                                                parents=[features_in_collection_parser(),
                                                         credentials_parser()])
    subparser.add_argument("--directory", help="directory for download")
    subparser.set_defaults(func=cli_download_files)
