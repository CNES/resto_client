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


resto_client Command Line Interface (CLI)

Implemented commands (without options):

SET:
    > resto_client set server <server_url> ...
    > resto_client set account <account_id> ...
    > resto_client set collection <collection> ...

UNSET:
    > resto_client unset server
    > resto_client unset account
    > resto_client unset collection

SHOW:
    > resto_client show collections ...
    > resto_client show collection <collection> ...
    > resto_client show feature <collection> <feature_id> ...

DOWNLOAD:
    > resto_client download product <collection> <feature_id> ...
    > resto_client download quicklook <collection> <feature_id> ...
    > resto_client download thumbnail <collection> <feature_id> ...
    > resto_client download annexes <collection> <feature_id> ...

SEARCH:
    > resto_client search <collection> ...


Expected commands (without options):

    TBD
"""
from argparse import ArgumentParser

from .parser_configure_server import add_configure_server_subparser
from .parser_download import add_download_subparser
from .parser_search import add_search_subparser
from .parser_set import add_set_subparser
from .parser_show import add_show_subparser
from .parser_unset import add_unset_subparser


def build_parser() -> ArgumentParser:
    """Creates a parser suitable for parsing a command line invoking this program.

    :return: A CLI parser.
    """
    parser = ArgumentParser(description='A commmand line client to interact with resto servers.')

    help_msg = 'For more help: {} <sub_command> -h'
    sub_parsers = parser.add_subparsers(description=help_msg.format(parser.prog))

    add_set_subparser(sub_parsers)
    add_unset_subparser(sub_parsers)
    add_show_subparser(sub_parsers)
    add_download_subparser(sub_parsers)
    add_search_subparser(sub_parsers)
    add_configure_server_subparser(sub_parsers)

    return parser
