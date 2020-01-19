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
import unittest

from resto_client.base_exceptions import RestoClientDesignError, RestoClientUserError
from resto_client.cli.resto_client_cli import resto_client_run
from resto_client.cli.resto_client_settings import RESTO_CLIENT_SETTINGS
from resto_client.settings.servers_database import (DB_SERVERS,
                                                    RESTO_URL_KEY, RESTO_PROTOCOL_KEY,
                                                    AUTH_URL_KEY, AUTH_PROTOCOL_KEY)


class UTestCliConfigureServer(unittest.TestCase):
    """
    Unit Tests of the cli configure_server module
    create,delete,show, edit (not implemented)
    """

    def test_n_config_server_show(self) -> None:
        """
        Unit test of config_server show in nominal cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        with redirect_stdout(io.StringIO()) as out_string_io:
            resto_client_run(arguments=['configure_server', 'show'])
        output = out_string_io.getvalue()  # type: ignore
        self.assertIn('Settings from : resto_client_server_settings.json', output)

    def test_n_config_server_create_del(self) -> None:
        """
        Unit test of config_server create in nominal cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['configure_server', 'create', 'kalid',
                                    'https://www.kalideos.fr/resto2', 'dotcloud',
                                    'https://www.kalideos.fr/resto2', 'default',
                                    ])
        expect_dic = {RESTO_URL_KEY: 'https://www.kalideos.fr/resto2/',
                      RESTO_PROTOCOL_KEY: 'dotcloud',
                      AUTH_URL_KEY: 'https://www.kalideos.fr/resto2/',
                      AUTH_PROTOCOL_KEY: 'default'}

        self.assertEqual(DB_SERVERS.db_servers['kalid'], expect_dic)
        resto_client_run(arguments=['configure_server', 'delete', 'kalid'])
        self.assertTrue('kalid' not in DB_SERVERS.db_servers)

    def test_d_config_server_create(self) -> None:
        """
        Unit test of config_server create in degraded cases
        """
        RESTO_CLIENT_SETTINGS.clear()
        resto_client_run(arguments=['set', 'verbosity', 'DEBUG'])
        # if server already exist
        with self.assertRaises(RestoClientUserError) as context:
            resto_client_run(arguments=['configure_server', 'create', 'kalideos',
                                        'https://www.kalideos.fr/resto2', 'dotcloud',
                                        'https://www.kalideos.fr/resto2', 'default',
                                        ])
        self.assertEqual('Server kalideos already exists in the server database.',
                         str(context.exception))

        # if not enough argument in parser
        with self.assertRaises(SystemExit) as context2:
            resto_client_run(arguments=['configure_server', 'create', 'kalideos',
                                        'https://www.kalideos.fr/resto2', 'dotcloud',
                                        'https://www.kalideos.fr/resto2',
                                        ])
        self.assertEqual('2', str(context2.exception))

    def test_d_config_server_edit(self) -> None:
        """
        Unit test of config_server edit in degraded cases cause not implemented
        """
        RESTO_CLIENT_SETTINGS.clear()
        # configure_server edit not implemented yet
        with self.assertRaises(RestoClientDesignError) as context:
            resto_client_run(arguments=['configure_server', 'edit', 'kalideos',
                                        'https://www.kalideos.fr/resto2', 'dotcloud',
                                        'https://www.kalideos.fr/resto2', 'default', ])
        self.assertEqual('Edit server unimplemented', str(context.exception))
