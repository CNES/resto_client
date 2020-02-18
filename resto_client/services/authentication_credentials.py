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
from typing import Optional, TYPE_CHECKING  # @NoMove

from resto_client.base_exceptions import RestoClientDesignError
from resto_client.requests.base_request import AccesDeniedError

from .authentication_account import AuthenticationAccount
from .authentication_token import AuthenticationToken, RestoClientTokenRenewed


if TYPE_CHECKING:
    from resto_client.services.authentication_service import AuthenticationService  # @UnusedImport


class AuthenticationCredentials(AuthenticationAccount, AuthenticationToken):
    """
    Class implementing the credentials for a connection: username, password.
    """

    @property
    def parent_server_name(self) -> str:
        """
        :returns: the name of the parent_server.
        """
        return self.parent_service.parent_server.server_name

    @property
    def parent_service(self) -> 'AuthenticationService':
        """
        :returns: the name of the parent_server.
        """
        return self._parent_service

    def __init__(self, authentication_service: 'AuthenticationService') -> None:
        """
        Constructor

        :param authentication_service: authentication service onto which these credentials are valid
        """
        self._parent_service = authentication_service

        AuthenticationAccount.__init__(self)
        AuthenticationToken.__init__(self)

    def set(self,
            username: Optional[str]=None,
            password: Optional[str]=None,
            token_value: Optional[str]=None) -> None:
        """
        Set or reset the username, the password and the token.

        If username is not None, it is set to the provided value if it is different from the
        already stored one and the password is stored whatever its value.
        If username is None and password is not, then only the password is updated with the
        provided value. Otherwise username and password are both reset.

        :param username: the username to register
        :param password: the account password
        :param token_value: a token associated to these credentials
        :raises RestoClientDesignError: when an unconsistent set of arguments is provided
        """
        if username is None and password is None and token_value is None:
            return

        if password is not None and token_value is not None:
            msg = 'Cannot define or change simultaneously password and token'
            raise RestoClientDesignError(msg)

        if username is None:
            if self._username is None:
                msg = 'Cannot set/reset password or token when username is undefined.'
                raise RestoClientDesignError(msg)

            # We already have a username and want to set/change password or token.
            if password is not None:
                self._password = password
            if token_value is None:
                self._reset_token()
            else:
                self.token_value = token_value

        else:
            # Take the new username definition, either with a password or with a token
            self._username = username.lower()  # resto server imposes lowercase account
            self._password = password
            if token_value is None:
                self._reset_token()
            else:
                self.token_value = token_value

    def reset_credentials(self) -> None:
        """
        Reset the credentials unconditionally.
        """
        self._reset_account()
        self._reset_token()

    def __str__(self) -> str:
        return 'username: {} / password: {} / token: {}'.format(self.username,
                                                                self.password,
                                                                self.current_token)
