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

    help_msg = 'For more help: {} <sub_command> -h'.format(parser.prog)
    sub_parsers = parser.add_subparsers(description=help_msg)

    # TODO:Thnik about changing set to 'seet server|client [--option1=xxx] [--option2=yyy]
    add_set_subparser(sub_parsers)
    add_unset_subparser(sub_parsers)
    add_show_subparser(sub_parsers)
    add_download_subparser(sub_parsers)
    add_search_subparser(sub_parsers)
    add_configure_server_subparser(sub_parsers)

    return parser
