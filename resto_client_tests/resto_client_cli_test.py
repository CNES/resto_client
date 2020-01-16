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
import sys
import io
from typing import List
from contextlib import redirect_stdout

from resto_client.cli.resto_client_cli import build_parser, resto_client_run
from resto_client.settings.resto_client_settings import RESTO_CLIENT_SETTINGS
from resto_client.base_exceptions import RestoClientError


def catch_output_from_run(test_args: dict) -> str:
    """
    Launch resto_client_run and catch output for test

    :param  test_args: dictionnary with cli verb, targeted collection, server name and product id
    :returns: output of a run
    """
    RESTO_CLIENT_SETTINGS.clear()
    try:
        arguments = test_args.pop('mandatory')
    except KeyError:
        msg_err = 'mandatory key is mandatory in test_args dict argument'
        raise RestoClientError(msg_err)

    for key, value in test_args.items():
        new_item = '--{}={}'.format(key, value)
        arguments.append(new_item)
    with redirect_stdout(io.StringIO()) as out_string_io:
        resto_client_run(arguments=arguments)
    output = out_string_io.getvalue()  # type: ignore
    return output


def print_parser_help(parser: argparse.ArgumentParser, arguments: List) -> None:
    """
    Print one help
    :param parser: a parser to launch
    :param list arguments: in the form [verb, action]
    """
    try:
        _ = parser.parse_args(arguments + ['--help'])
    except SystemExit:
        pass


def print_all_help(dict_arguments: dict) -> None:
    """
    Print one help
    :param dict_arguments: verb, action in a dictionary form => verb : list of actions
    """
    parser = build_parser()
    print_parser_help(parser, [])
    for verbe, actions in dict_arguments.items():
        print('\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print('                      {} '.format(verbe))
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print_parser_help(parser, [verbe])
        for action in actions:
            if action is not None:
                print('\n----------------------------------------------------')
                print('                      {}  {}'.format(verbe, action))
                print('----------------------------------------------------')
                print_parser_help(parser, [verbe, action])


def main() -> None:
    """
    Command line interface to access test to print all help.
    """
    settable_options = ['server', 'account', 'collection', 'region', 'download_dir', 'verbosity']
    dict_arguments = {'set': settable_options,
                      'unset': settable_options,
                      'show': ['settings', 'server', 'collection', 'feature'],
                      'download': ['product', 'quicklook', 'thumbnail', 'annexes'],
                      'search': [None],
                      'configure_server': ['create', 'delete', 'edit', 'show']}

    print_all_help(dict_arguments)


if __name__ == "__main__":
    sys.exit(main())  # type: ignore
