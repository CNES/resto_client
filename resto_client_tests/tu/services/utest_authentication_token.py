# -*- coding: utf-8 -*-
"""
   Copyright 2020 CNES

   Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
   in compliance with the License. You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software distributed under the License
   is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
   or implied. See the License for the specific language governing permissions and
   limitations under the License.
"""
from typing import TYPE_CHECKING
import unittest
from unittest.mock import MagicMock

from resto_client.services.authentication_token import AuthenticationToken
from resto_client.services.resto_server import RestoServer


if TYPE_CHECKING:
    from resto_client.services.authentication_credentials import \
        AuthenticationCredentials  # @UnusedImport


class UTestAuthenticationToken(unittest.TestCase):
    """
    Unit Tests of the the authentication token class
    """

    credentials: 'AuthenticationCredentials'

    @classmethod
    def setUpClass(cls) -> None:
        super(UTestAuthenticationToken, cls).setUpClass()
        # We need to instantiate a RestoServer in order to retrieve a well-formed
        # AuthenticationCredentials
        server = RestoServer('kalideos', debug_server=True)
        # pylint: disable=protected-access
        cls.credentials = server._authentication_service._credentials

    def setUp(self) -> None:
        super(UTestAuthenticationToken, self).setUp()
        # Mock the token to a default state such that check_token returns False and
        # get_token returns an arbitrary value.
        self.token = AuthenticationToken(parent_credentials=self.credentials)
        setattr(self.token, '_get_token', MagicMock(return_value='abcdefghijklmnop'))
        setattr(self.token, '_check_token', MagicMock(return_value=False))
        setattr(self.token, '_revoke_token', MagicMock(return_value=None))

    def assert_requests_calls(self, nb_check_calls: int=0,
                              nb_get_calls: int=0, nb_revoke_calls: int=0) -> None:
        # pylint: disable=no-member, protected-access

        self.assertEqual(len(self.token._check_token.mock_calls), nb_check_calls)  # type: ignore
        self.assertEqual(len(self.token._get_token.mock_calls), nb_get_calls)  # type: ignore
        self.assertEqual(len(self.token._revoke_token.mock_calls), nb_revoke_calls)  # type: ignore

        self.token._check_token.reset_mock()  # type: ignore
        self.token._get_token.reset_mock()  # type: ignore
        self.token._revoke_token.reset_mock()  # type: ignore

    def test_n_token_getter_setter(self) -> None:

        # initially, the token value is not set
        self.assertIsNone(self.token.get_current_token_value())

        # accessing through its getter will trigger a check_token and then a get_token
        self.assertEqual(self.token.token_value, 'abcdefghijklmnop')
        # and retrieving it does not trigger any request.
        self.assert_requests_calls(nb_get_calls=1)

        # When we set a value in it, this value is supposed to be valid and returned as is.
        self.token.token_value = 'a token which will be supposed to be valid'
        self.assertEqual(self.token.token_value, 'a token which will be supposed to be valid')
        # and retrieving it does not trigger any request.
        self.assert_requests_calls()

        # Now we force token renewal
        self.token.renew_token()
        # which emit a revoke_token and a get_token
        self.assert_requests_calls(nb_get_calls=1, nb_revoke_calls=1)

        # The token value is now returned after issuing a get_token
        self.assertEqual(self.token.token_value, 'abcdefghijklmnop')
        # and retrieving it does not trigger any request.
        self.assert_requests_calls()

        # change the value returned by get_token and renew token again.
        setattr(self.token, '_get_token', MagicMock(return_value='=============='))
        self.token.renew_token()
        # a revoke_token and a get_token requests were emitted
        self.assert_requests_calls(nb_get_calls=1, nb_revoke_calls=1)
        self.assertEqual(self.token.token_value, '==============')
        # and retrieving it does not trigger any request.
        self.assert_requests_calls()

        # Set the token value to another predefined value.
        self.token.token_value = 'another token which will be supposed to be valid'
        # setting it did not trigger more requests.
        self.assert_requests_calls()
        self.assertEqual(self.token.token_value, 'another token which will be supposed to be valid')
        # and retrieving it does not trigger any request.
        self.assert_requests_calls()

        # Reset the token.
        self.token.reset_token()
        # does not trigger more requests.
        self.assert_requests_calls(nb_revoke_calls=1)
        # But retrieving it trigger check and get requests.
        retrieved_token = self.token.token_value
        self.assert_requests_calls(nb_get_calls=1)
        self.assertEqual(retrieved_token, '==============')

    def test_n_token_setter(self) -> None:
        """
        Test of the token_value setter
        """

        # initially, the token value is not set
        self.assertIsNone(self.token.get_current_token_value())

        # If we set a value, gotten from elsewhere (persisted for instance)
        self.token.token_value = 'a token which will be supposed to be valid'
        # no request is sent
        self.assert_requests_calls()
        # and this value is retrieved
        self.assertEqual(self.token.token_value, 'a token which will be supposed to be valid')
        # without sending requests
        self.assert_requests_calls()

        # if we try to set the token to None, we get an exception
        with self.assertRaises(TypeError):
            self.token.token_value = None  # type:ignore

    def test_n_token_reset(self) -> None:
        """
        Test of the token_value reset
        """

        # initially, the token value is not set
        self.assertIsNone(self.token.get_current_token_value())

        # If we reset the token
        self.token.reset_token()
        # no request is sent
        self.assert_requests_calls()
        # but retrieving the token
        retrieved_token = self.token.token_value
        # emit a get_token request
        self.assert_requests_calls(nb_get_calls=1)
        self.assertEqual(retrieved_token, 'abcdefghijklmnop')

        # retrieving the token again does not change its value
        self.assertEqual(self.token.token_value, 'abcdefghijklmnop')
        # and does not emit more requests
        self.assert_requests_calls()
