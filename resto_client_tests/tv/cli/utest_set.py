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
from contextlib import redirect_stdout
import io
from pathlib import Path

from resto_client.base_exceptions import RestoClientUserError
from resto_client.cli.resto_client_cli import resto_client_run
from resto_client.cli.resto_client_parameters import VERBOSITY_KEY, REGION_KEY, DOWNLOAD_DIR_KEY
from resto_client.cli.resto_server_persisted import (SERVER_KEY, USERNAME_KEY, COLLECTION_KEY,
                                                     TOKEN_KEY)
from resto_client.cli.resto_server_persisted import RestoClientNoPersistedServer
from resto_client.settings.servers_database import WELL_KNOWN_SERVERS
from resto_client_tests.resto_client_cli_test import TestRestoClientCli


class UTestCliSet(TestRestoClientCli):
    """
    Unit Tests of the cli set module
    server, account, collection, download_dir, region, verbosity
    """

    def test_n_set_server(self) -> None:
        """
        Unit test of set server in nominal cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        # Test setting of all default server
        for server_name in WELL_KNOWN_SERVERS:
            resto_client_run(arguments=['set', 'server', server_name])
            self.assert_setting_equal(SERVER_KEY, server_name)
            self.assert_no_account_in_settings()

    def test_n_set_account(self) -> None:
        """
        Unit test of set account in nominal cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        # With no account already set
        resto_client_run(arguments=['set', 'account', 'test_name1'])
        self.assert_setting_equal(USERNAME_KEY, 'test_name1')
        self.assert_not_in_settings(TOKEN_KEY)
        # With account already persisted
        resto_client_run(arguments=['set', 'account', 'test_name2'])
        self.assert_setting_equal(USERNAME_KEY, 'test_name2')
        self.assert_not_in_settings(TOKEN_KEY)

    def test_n_set_collection(self) -> None:
        """
        Unit test of set collection in nominal cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        # With no collection already set
        resto_client_run(arguments=['set', 'collection', 'KALCNES'])
        self.assert_setting_equal(COLLECTION_KEY, 'KALCNES')
        # With collection already persisted
        resto_client_run(arguments=['set', 'collection', 'KALHAITI'])
        self.assert_setting_equal(COLLECTION_KEY, 'KALHAITI')

    def test_n_set_region(self) -> None:
        """
        Unit test of set region in nominal cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        resto_client_run(arguments=['set', 'region', 'bretagne'])
        self.assert_setting_equal(REGION_KEY, 'bretagne.geojson')
        # With region already persisted
        resto_client_run(arguments=['set', 'region', 'alpes'])
        self.assert_setting_equal(REGION_KEY, 'alpes.geojson')

    def test_n_set_download_dir(self) -> None:
        """
        Unit test of set download directory in nominal cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        # get an existing directory for test
        directory_test_1 = Path.home()
        resto_client_run(arguments=['set', 'download_dir', str(directory_test_1)])
        self.assert_setting_equal(DOWNLOAD_DIR_KEY, str(directory_test_1))
        # With download directory already persisted
        directory_test_2 = directory_test_1.parent
        resto_client_run(arguments=['set', 'download_dir', str(directory_test_2)])
        self.assert_setting_equal(DOWNLOAD_DIR_KEY, str(directory_test_2))

    def test_n_set_verbosity(self) -> None:
        """
        Unit test of set verbosity in nominal cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        self.assert_setting_equal(VERBOSITY_KEY, 'DEBUG')
        # With verbosity already persisted
        resto_client_run(arguments=['set', 'verbosity', 'NORMAL'])
        self.assert_setting_equal(VERBOSITY_KEY, 'NORMAL')

    def test_n_set_server_reinit(self) -> None:
        """
        Unit test of set server with already saved parameters in nominal cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        # First set server with parameters
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        resto_client_run(arguments=['set', 'account', 'fake_user@example.com'])
        resto_client_run(arguments=['set', 'collection', 'KALCNES'])
        # Then set another server
        resto_client_run(arguments=['set', 'server', 'peps'])
        # Verify resetting of parameters
        self.assert_setting_equal(SERVER_KEY, 'peps')
        self.assert_not_in_settings(COLLECTION_KEY)
        self.assert_no_account_in_settings()

    def test_n_set_server_mono_col(self) -> None:
        """
        Unit test of set server with a server with one collection in nominal cases
        """
        resto_client_run(arguments=['set', 'server', 'ro'])
        self.assert_setting_equal(COLLECTION_KEY, 'ROHAITI')

    def test_d_set_server(self) -> None:
        """
        Unit test of set server in degraded cases
        """
        with redirect_stdout(io.StringIO()) as out_string_io:
            resto_client_run(arguments=['set', 'server', 'bad_server'])
        output = out_string_io.getvalue().strip()  # type: ignore
        msg = 'No persisted server and bad_server is not a valid server name.'
        self.assertIn(msg, output)

    def test_d_set_account(self) -> None:
        """
        Unit test of set account in degraded cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        with self.assertRaises(RestoClientNoPersistedServer):
            resto_client_run(arguments=['set', 'account', 'test_name'])
        # Verify non-setting of parameters
        self.assert_no_account_in_settings()

    def test_d_set_collection(self) -> None:
        """
        Unit test of set collection in degraded cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        with self.assertRaises(RestoClientUserError) as context:
            resto_client_run(arguments=['set', 'collection', 'Bad_Collection'])
        self.assertEqual('No collection found with name Bad_Collection', str(context.exception))

    def test_d_set_download_dir(self) -> None:
        """
        Unit test of set download directory in degraded cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        with self.assertRaises(NotADirectoryError) as context:
            resto_client_run(arguments=['set', 'download_dir', 'ICI'])
        self.assertEqual('ICI', str(context.exception))

    # Following errors are processed by argparse directly.

    def test_d_set_region(self) -> None:
        """
        Unit test of set region in degraded cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        with self.assertRaises(SystemExit) as context:
            resto_client_run(arguments=['set', 'region', 'JaimeLaBretagne'])
        # should raise this exception after a argparse.ArgumentError
        # because argument region: invalid choice
        self.assertEqual('2', str(context.exception))

    def test_d_set_verbosity(self) -> None:
        """
        Unit test of set verbosity in degraded cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        with self.assertRaises(SystemExit) as context:
            resto_client_run(arguments=['set', 'verbosity', 'Parle_Moi'])
        # should raise this exception after a argparse.ArgumentError
        # because argument verbosity: invalid choice
        self.assertEqual('2', str(context.exception))