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
from resto_client.base_exceptions import RestoClientUserError
from resto_client.cli.resto_client_cli import resto_client_run
from resto_client.cli.resto_server_persisted import (SERVER_KEY, USERNAME_KEY, COLLECTION_KEY,
                                                     TOKEN_KEY)
from resto_client.cli.resto_server_persisted import RestoClientNoPersistedServer
from resto_client.settings.servers_database import WELL_KNOWN_SERVERS
from resto_client_tests.resto_client_cli_test import TestRestoClientCli


class UTestSetServerParams(TestRestoClientCli):
    """
    Unit Tests of the cli set of RestoServerPersisted parameters
    server, account, collection
    """

    def test_n_set_server(self) -> None:
        """
        Unit test of set server in nominal cases
        """
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        # Test setting of all default server
        for server_name in WELL_KNOWN_SERVERS:
            with self.subTest(server=server_name):
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
        with self.assertRaises(RestoClientUserError) as ctxt:
            resto_client_run(arguments=['set', 'server', 'bad_server'])
        msg = 'No persisted server and bad_server is not a valid server name.'
        self.assertEqual(msg, str(ctxt.exception))

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


class UTestUnsetServerParams(TestRestoClientCli):
    """
    Unit Tests of the cli unset of RestoServerPersisted parameters
    server, account, collection
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
