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

from resto_client.base_exceptions import RestoClientUserError
from resto_client.cli.resto_client_cli import resto_client_run
from resto_client.cli.resto_client_parameters import VERBOSITY_KEY, REGION_KEY, DOWNLOAD_DIR_KEY
from resto_client.cli.resto_client_settings import RESTO_CLIENT_DEFAULT_DOWNLOAD_DIR
from resto_client.cli.resto_server_persisted import COLLECTION_KEY
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
        self.assert_no_server_in_settings()
        # With server persisted and account persisted
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        resto_client_run(arguments=['set', 'account', 'test_account'])
        # Test setting of all default server
        resto_client_run(arguments=['unset', 'server'])
        self.assert_no_server_in_settings()

    def test_n_unset_server_noserver(self) -> None:
        """
        Unit test of unset server if there is no server in nominal cases
        """
        with self.assertRaises(RestoClientUserError) as ctxt:
            resto_client_run(arguments=['unset', 'server'])
        expected_msg = 'No persisted server and None is not a valid server name.'
        self.assertEqual(expected_msg, str(ctxt.exception))
        self.assert_no_server_in_settings()

    def test_n_unset_account(self) -> None:
        """
        Unit test of unset account in nominal cases
        """
        # With no server persisted
        with self.assertRaises(RestoClientUserError) as ctxt:
            resto_client_run(arguments=['unset', 'account'])
        expected_msg = 'No persisted server and None is not a valid server name.'
        self.assertEqual(expected_msg, str(ctxt.exception))
        self.assert_no_account_in_settings()

        # With server persisted and account already set
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        resto_client_run(arguments=['set', 'account', 'test_name'])
        resto_client_run(arguments=['unset', 'account'])
        self.assert_no_account_in_settings()

    def test_n_unset_collection(self) -> None:
        """
        Unit test of unset collection in nominal cases
        """
        # With no server persisted
        with self.assertRaises(RestoClientUserError) as ctxt:
            resto_client_run(arguments=['unset', 'collection'])
        expected_msg = 'No persisted server and None is not a valid server name.'
        self.assertEqual(expected_msg, str(ctxt.exception))
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
        self.assert_setting_equal(DOWNLOAD_DIR_KEY, directory_test)
        resto_client_run(arguments=['unset', 'download_dir'])
        self.assert_setting_equal(DOWNLOAD_DIR_KEY, str(RESTO_CLIENT_DEFAULT_DOWNLOAD_DIR))
        # With default directory persisted
        resto_client_run(arguments=['unset', 'download_dir'])
        self.assert_setting_equal(DOWNLOAD_DIR_KEY, str(RESTO_CLIENT_DEFAULT_DOWNLOAD_DIR))

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
