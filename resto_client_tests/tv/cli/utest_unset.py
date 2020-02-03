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
from pathlib import Path

from resto_client.cli.resto_client_cli import resto_client_run
from resto_client.cli.resto_client_parameters import VERBOSITY_KEY, REGION_KEY, DOWNLOAD_DIR_KEY
from resto_client.cli.resto_client_settings import RESTO_CLIENT_SETTINGS
from resto_client.cli.resto_server_persisted import (SERVER_KEY, USERNAME_KEY, COLLECTION_KEY,
                                                     TOKEN_KEY)
from resto_client.generic.user_dirs import user_download_dir
from resto_client_tests.resto_client_cli_test import TestRestoClientCli


class UTestCliUnset(TestRestoClientCli):
    """
    Unit Tests of the cli unset module
    server, account, collection, download_dir, region, verbosity
    """

    def test_n_unset_server(self) -> None:
        """
        Unit test of unset server in nominal cases
        """
        # With server persisted and no account persisted
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        # Test setting of all default server
        resto_client_run(arguments=['unset', 'server'])
        self.assert_not_in_settings(SERVER_KEY)
        self.assert_not_in_settings(COLLECTION_KEY)
        self.assert_not_in_settings(USERNAME_KEY)
        self.assert_not_in_settings(TOKEN_KEY)
        # With server persisted and account persisted
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        resto_client_run(arguments=['set', 'account', 'test_account'])
        # Test setting of all default server
        resto_client_run(arguments=['unset', 'server'])
        self.assert_not_in_settings(SERVER_KEY)
        self.assert_not_in_settings(COLLECTION_KEY)
        self.assert_not_in_settings(USERNAME_KEY)
        self.assert_not_in_settings(TOKEN_KEY)

    def test_n_unset_server_noserver(self) -> None:
        """
        Unit test of unset server if there is no server in nominal cases
        """
        resto_client_run(arguments=['unset', 'server'])
        resto_client_run(arguments=['unset', 'server'])
        self.assert_not_in_settings(SERVER_KEY)
        self.assert_not_in_settings(COLLECTION_KEY)
        self.assert_not_in_settings(USERNAME_KEY)
        self.assert_not_in_settings(TOKEN_KEY)

    def test_n_unset_account(self) -> None:
        """
        Unit test of unset account in nominal cases
        """
        # With no server persisted
        resto_client_run(arguments=['unset', 'account'])
        self.assert_not_in_settings(USERNAME_KEY)
        self.assert_not_in_settings(TOKEN_KEY)
        # With server persisted and account already set
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        resto_client_run(arguments=['set', 'account', 'test_name'])
        # With no account already set
        resto_client_run(arguments=['unset', 'account'])
        self.assert_not_in_settings(USERNAME_KEY)
        self.assert_not_in_settings(TOKEN_KEY)

    def test_n_unset_collection(self) -> None:
        """
        Unit test of unset collection in nominal cases
        """
        # With no server persisted
        resto_client_run(arguments=['unset', 'collection'])
        self.assert_not_in_settings(COLLECTION_KEY)
        # With server persisted and collection already set
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        resto_client_run(arguments=['set', 'collection', 'KALCNES'])
        resto_client_run(arguments=['unset', 'collection'])
        self.assert_not_in_settings(COLLECTION_KEY)
        # With server persisted and no collection persisted
        resto_client_run(arguments=['unset', 'collection'])
        self.assert_not_in_settings(COLLECTION_KEY)

    def test_n_unset_region(self) -> None:
        """
        Unit test of unset region in nominal cases
        """
        # With region already persisted
        resto_client_run(arguments=['set', 'region', 'bretagne'])
        resto_client_run(arguments=['unset', 'region'])
        self.assert_not_in_settings(REGION_KEY)
        # With no region persisted
        resto_client_run(arguments=['unset', 'region'])
        self.assert_not_in_settings(REGION_KEY)

    def test_n_unset_download_dir(self) -> None:
        """
        Unit test of unset download directory in nominal cases
        """
        # With download directory already persisted
        directory_test = str(Path.home())
        resto_client_run(arguments=['set', 'download_dir', directory_test])
        self.assertEqual(RESTO_CLIENT_SETTINGS[DOWNLOAD_DIR_KEY], directory_test)
        resto_client_run(arguments=['unset', 'download_dir'])
        self.assertEqual(RESTO_CLIENT_SETTINGS[DOWNLOAD_DIR_KEY], str(user_download_dir()))
        # With default directory persisted
        resto_client_run(arguments=['unset', 'download_dir'])
        self.assertEqual(RESTO_CLIENT_SETTINGS[DOWNLOAD_DIR_KEY], str(user_download_dir()))

    def test_n_unset_verbosity(self) -> None:
        """
        Unit test of unset verbosity in nominal cases
        """
        # With verbosity already persisted
        resto_client_run(arguments=['set', 'verbosity', 'NORMAL'])
        resto_client_run(arguments=['unset', 'verbosity'])
        self.assert_not_in_settings(VERBOSITY_KEY)
        # With no verbosity persisted
        resto_client_run(arguments=['unset', 'verbosity'])
        self.assert_not_in_settings(VERBOSITY_KEY)
