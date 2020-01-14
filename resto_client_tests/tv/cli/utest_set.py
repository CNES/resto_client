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
import unittest

from resto_client.base_exceptions import RestoClientUserError
from resto_client.cli.resto_client_cli import resto_client_run
from resto_client.cli.server_parameters import RestoClientNoPersistedServer
from resto_client.settings.resto_client_settings import RESTO_CLIENT_SETTINGS
from resto_client.settings.servers_database import WELL_KNOWN_SERVERS
from resto_client_tests.tv.cli.cli_utils import (USERNAME_KEY, DOWNLOAD_DIR_KEY,
                                                 TOKEN_KEY, VERBOSITY_KEY, REGION_KEY,
                                                 COLLECTION_KEY)


class UTestCliSet(unittest.TestCase):
    """
    Unit Tests of the cli set module
    server, account, collection, download_dir, region, verbosity
    """

    def test_n_set_server(self) -> None:
        """
        Unit test of set server in nominal cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        # Test setting of all default server
        for server_name in WELL_KNOWN_SERVERS:
            resto_client_run(arguments=['set', 'server', server_name])
            # Verify that RESTO_CLIENT_SETTINGS contain all server info from server database
            self.assertTrue('server_name' in RESTO_CLIENT_SETTINGS)
            self.assertEqual(RESTO_CLIENT_SETTINGS['server_name'], server_name)

    def test_n_set_account(self) -> None:
        """
        Unit test of set account in nominal cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        # With no account already set
        resto_client_run(arguments=['set', 'account', 'test_name1'])
        self.assertEqual('test_name1', RESTO_CLIENT_SETTINGS[USERNAME_KEY])
        # With account already persisted
        resto_client_run(arguments=['set', 'account', 'test_name2'])
        self.assertEqual('test_name2', RESTO_CLIENT_SETTINGS[USERNAME_KEY])

    def test_n_set_collection(self) -> None:
        """
        Unit test of set collection in nominal cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        # With no collection already set
        resto_client_run(arguments=['set', 'collection', 'KALCNES'])
        self.assertEqual('KALCNES', RESTO_CLIENT_SETTINGS[COLLECTION_KEY])
        # With collection already persisted
        resto_client_run(arguments=['set', 'collection', 'KALHAITI'])
        self.assertEqual('KALHAITI', RESTO_CLIENT_SETTINGS[COLLECTION_KEY])

    def test_n_set_region(self) -> None:
        """
        Unit test of set region in nominal cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        resto_client_run(arguments=['set', 'region', 'bretagne'])
        self.assertEqual('bretagne.geojson', RESTO_CLIENT_SETTINGS[REGION_KEY])
        # With region already persisted
        resto_client_run(arguments=['set', 'region', 'alpes'])
        self.assertEqual('alpes.geojson', RESTO_CLIENT_SETTINGS[REGION_KEY])

    def test_n_set_download_dir(self) -> None:
        """
        Unit test of set download directory in nominal cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        # get an existing directory for test
        directory_test_1 = Path.home()
        resto_client_run(arguments=['set', 'download_dir', str(directory_test_1)])
        self.assertEqual(str(directory_test_1), RESTO_CLIENT_SETTINGS[DOWNLOAD_DIR_KEY])
        # With download directory already persisted
        directory_test_2 = directory_test_1.parent
        resto_client_run(arguments=['set', 'download_dir', str(directory_test_2)])
        self.assertEqual(str(directory_test_2), RESTO_CLIENT_SETTINGS[DOWNLOAD_DIR_KEY])

    def test_n_set_verbosity(self) -> None:
        """
        Unit test of set verbosity in nominal cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        self.assertEqual('DEBUG', RESTO_CLIENT_SETTINGS[VERBOSITY_KEY])
        # With verbosity already persisted
        resto_client_run(arguments=['set', 'verbosity', 'NORMAL'])
        self.assertEqual('NORMAL', RESTO_CLIENT_SETTINGS[VERBOSITY_KEY])

    def test_n_set_server_reinit(self) -> None:
        """
        Unit test of set server with already saved parameters in nominal cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        # First set server with parameters
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        resto_client_run(arguments=['set', 'account', 'fake_user@example.com'])
        resto_client_run(arguments=['set', 'collection', 'KALCNES'])
        # Then set another server
        resto_client_run(arguments=['set', 'server', 'peps'])
        # Verify resetting of parameters
        self.assertTrue(USERNAME_KEY not in RESTO_CLIENT_SETTINGS)
        self.assertTrue(TOKEN_KEY not in RESTO_CLIENT_SETTINGS)
        self.assertTrue(COLLECTION_KEY not in RESTO_CLIENT_SETTINGS)

    def test_n_set_server_mono_col(self) -> None:
        """
        Unit test of set server with a server with one collection in nominal cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['set', 'server', 'ro'])
        self.assertTrue(RESTO_CLIENT_SETTINGS[COLLECTION_KEY], 'ROHAITI')

    def test_d_set_server(self) -> None:
        """
        Unit test of set server in degraded cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        with redirect_stdout(io.StringIO()) as out_string_io:
            resto_client_run(arguments=['set', 'server', 'bad_server'])
        output = out_string_io.getvalue().strip()  # type: ignore
        msg = 'Server bad_server does not exist in the servers database'
        self.assertIn(msg, output)

    def test_d_set_account(self) -> None:
        """
        Unit test of set account in degraded cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        with self.assertRaises(RestoClientNoPersistedServer):
            resto_client_run(arguments=['set', 'account', 'test_name'])
        # Verify non-setting of parameters
        self.assertTrue(USERNAME_KEY not in RESTO_CLIENT_SETTINGS)
        self.assertTrue(TOKEN_KEY not in RESTO_CLIENT_SETTINGS)

    def test_d_set_collection(self) -> None:
        """
        Unit test of set collection in degraded cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        resto_client_run(arguments=['set', 'server', 'kalideos'])
        with self.assertRaises(RestoClientUserError) as context:
            resto_client_run(arguments=['set', 'collection', 'Bad_Collection'])
        self.assertEqual('No collection found with name Bad_Collection', str(context.exception))

    def test_d_set_download_dir(self) -> None:
        """
        Unit test of set download directory in degraded cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        with self.assertRaises(NotADirectoryError) as context:
            resto_client_run(arguments=['set', 'download_dir', 'ICI'])
        self.assertEqual('ICI', str(context.exception))

    # Following errors are processed by argparse directly.

    def test_d_set_region(self) -> None:
        """
        Unit test of set region in degraded cases
        """
        RESTO_CLIENT_SETTINGS.clear()
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
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        with self.assertRaises(SystemExit) as context:
            resto_client_run(arguments=['set', 'verbosity', 'Parle_Moi'])
        # should raise this exception after a argparse.ArgumentError
        # because argument verbosity: invalid choice
        self.assertEqual('2', str(context.exception))
