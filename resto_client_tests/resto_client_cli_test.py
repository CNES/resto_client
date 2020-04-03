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
import io
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import List
import unittest

from resto_client.cli.parser.resto_client_parser import build_parser
from resto_client.cli.resto_client_cli import resto_client_run
from resto_client.cli.resto_client_parameters import DOWNLOAD_DIR_KEY
from resto_client.cli.resto_client_settings import RESTO_CLIENT_SETTINGS
from resto_client.cli.resto_server_persisted import (SERVER_KEY, USERNAME_KEY, COLLECTION_KEY,
                                                     TOKEN_KEY)
import resto_client.settings.resto_client_config as resto_client_config


class TestRestoClientCli(unittest.TestCase):
    """
    Basic Tests Class for resto_client Unit Test
    """

    def setUp(self) -> None:
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(['set', 'verbosity', 'DEBUG'])

    def assert_not_in_settings(self, settings_key: str) -> None:
        """
        Verify that the provided key is absent from the settings.

        :param settings_key: name of the key to test
        """
        self.assertNotIn(settings_key, RESTO_CLIENT_SETTINGS)

    def assert_in_settings(self, settings_key: str) -> None:
        """
        Verify that the provided key is present in the settings and different from None.

        :param settings_key: name of the key to test
        """
        self.assertIn(settings_key, RESTO_CLIENT_SETTINGS)
        self.assertIsNotNone(RESTO_CLIENT_SETTINGS[settings_key])

    def assert_no_account_in_settings(self) -> None:
        """
        Verify that the account related keys are absent from the settings.
        """
        self.assert_not_in_settings(USERNAME_KEY)
        self.assert_not_in_settings(TOKEN_KEY)

    def assert_no_server_in_settings(self) -> None:
        """
        Verify that the server related keys are absent from the settings.
        """
        self.assert_not_in_settings(SERVER_KEY)
        self.assert_not_in_settings(COLLECTION_KEY)
        self.assert_no_account_in_settings()

    def assert_setting_equal(self, settings_key: str, expected_value: str) -> None:
        """
        Verify that the provided key is present in the settings and its value is equal to the
        expected one.

        :param settings_key: name of the key to test
        :param expected_value: expected value of the setting
        """
        self.assert_in_settings(settings_key)
        self.assertEqual(RESTO_CLIENT_SETTINGS[settings_key], expected_value)

    @staticmethod
    def get_downloaded_file_path(base_filename: str) -> Path:
        """
        Returns the path in the downlaod directory of a file specified by its basename.

        :param base_filename: base file name
        :returns: the path to the file
        """
        return (Path(RESTO_CLIENT_SETTINGS[DOWNLOAD_DIR_KEY]) /
                RESTO_CLIENT_SETTINGS[SERVER_KEY] / base_filename)

    def assert_downloaded_file_ok(self, base_filename: str) -> None:
        """
        Verify that the download file is correct.

        :param base_filename: base file name
        """
        downloaded_file_path = self.get_downloaded_file_path(base_filename)
        self.assertTrue(downloaded_file_path.is_file(),
                        'Could not find expected file: {}'.format(str(downloaded_file_path)))

    def do_test_download_file(self, command: List[str], expected_files: List[str]) -> None:
        """
        Test that the provided command, which is supposed to download one or several files,
        succeed in downloading them.

        :param command: list of words composing the command
        :param expected_files: the base file names of the expected downloaded files
        """
        with TemporaryDirectory() as tmp_dir:
            resto_client_run(arguments=['set', 'download_dir', tmp_dir])
            resto_client_run(arguments=command)
            for file_name in expected_files:
                self.assert_downloaded_file_ok(file_name)
        # verify removing of tmp_dir
        self.assertFalse(Path(tmp_dir).is_dir())

    @staticmethod
    def get_command_output(command: List[str]) -> str:
        """
        Runs the specified resto_client command and returns its output

        :param command: the command as a list of words
        :returns: the command output
        """
        previous_stdout = resto_client_config.RESTO_CLIENT_STDOUT
        new_stdout = io.StringIO()
        resto_client_config.RESTO_CLIENT_STDOUT = new_stdout
        resto_client_run(arguments=command)
        output = new_stdout.getvalue()
        new_stdout.close()
        resto_client_config.RESTO_CLIENT_STDOUT = previous_stdout
        print(output)
        return output.strip()


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
