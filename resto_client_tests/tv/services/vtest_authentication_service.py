# -*- coding: utf-8 -*-
"""
.. admonition:: License

   Copyright 2020 CNES

   Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
   in compliance with the License. You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software distributed under the License
   is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
   or implied. See the License for the specific language governing permissions and
   limitations under the License.
"""
from typing import cast
import unittest

from resto_client.base_exceptions import AccessDeniedError
from resto_client.services.authentication_service import AuthenticationService
from resto_client.services.resto_server import RestoServer
from resto_client.settings.servers_database import WELL_KNOWN_SERVERS


class VTestAuthenticationService(unittest.TestCase):
    """
    Validation Tests of the the authentication service when used with wrong account
    """

    def test_n_get_token_wrong_account(self) -> None:
        """
        Test of get_token when credentials are incorrect
        """
        for server_name in WELL_KNOWN_SERVERS:
            with self.subTest(server=server_name):
                server = RestoServer(server_name, debug_server=True)
                auth_service = server._authentication_service  # pylint:disable=protected-access
                auth_service = cast(AuthenticationService, auth_service)

                server.set_credentials(username='resto_client_test_account',
                                       password='wrong_password')
                expected_fmt = 'Access Denied : (username, password) does not fit the server: {}'
                with self.assertRaises(AccessDeniedError) as ctxt:
                    auth_service.get_authorization_header()
                self.assertIn(expected_fmt.format(server_name), str(ctxt.exception))
