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
from typing import Optional, TYPE_CHECKING, Dict, Callable  # @UnusedImport @NoMove
from abc import ABC, abstractmethod
from base64 import b64encode
from getpass import getpass

from requests.auth import HTTPBasicAuth

from resto_client.base_exceptions import RestoClientDesignError

if TYPE_CHECKING:
    from resto_client.services.authentication_service import AuthenticationService  # @UnusedImport

AuthorizationDataType = Dict[str, Optional[str]]


class AuthenticationAccount(ABC):
    """
    Class implementing the account for a connection: username, password.
    """
    asking_input: Dict[str, Callable] = {'shown': input, 'hidden': getpass}

    def __init__(self, authentication_service: 'AuthenticationService') -> None:
        """
        Constructor

        :param authentication_service: authentication service onto which these credentials are valid
        """
        self.parent_service = authentication_service
        self.parent_server_name = authentication_service.parent_server.server_name

        self._username: Optional[str] = None
        self._password: Optional[str] = None

    def set_account(self,
                    username: Optional[str]=None,
                    password: Optional[str]=None) -> None:
        """
        Set or reset the username and the password.

        If username is not None, it is set to the provided value if it is different from the
        already stored one and the password is stored whatever its value.
        If username is None and password is not, then only the password is updated with the
        provided value. Otherwise username and password are both reset.

        :param username: the username to register
        :param password: the account password
        :raises RestoClientDesignError: when an unconsistent set of arguments is provided
        """
        # FIXME: is this method needed (see in conjunction with credentials.set())
        if username is None and password is None:
            return

        if username is None:
            if self._username is None:
                msg = 'Cannot set/reset password when username is undefined.'
                raise RestoClientDesignError(msg)

            # We already have a username and want to set/reset password.
            if password is not None:
                self._password = password

        else:
            # Take the new username definition, possibly with a password
            self._username = username.lower()  # resto server imposes lowercase account
            self._password = password

    def reset_account(self) -> None:
        """
        Reset the account unconditionally.
        """
        self._username = None
        self._password = None

    @property
    def username(self) -> Optional[str]:
        """
        :returns: the username
        """
        return self._username

    @property
    def password(self) -> Optional[str]:
        """
        :returns: the password
        """
        return self._password

    @property
    def account_defined(self) -> bool:
        """
        :returns: True if username and password are defined, but not necessarily valid.
        """
        return self.username is not None and self.password is not None

    @property
    def username_b64(self) -> str:
        """

        :returns: the username encoded as base64, suitable to insert in URLs
        :raises RestoClientDesignError: when trying to get base64 username while it is undefined.
        """
        if self.username is None:
            msg = 'Unable to provide base64 username when username undefined'
            raise RestoClientDesignError(msg)
        return b64encode(self.username.encode('UTF-8')).decode('UTF-8')

    def _ensure_account(self) -> None:
        """
        Verify that both username and password are defined, and request their values if it
        is not the case
        """
        if self.username is None:
            msg = "Please enter your username for {} server: ".format(self.parent_server_name)
            self.set(username=AuthenticationAccount.asking_input['shown'](msg))
        if self.password is None:
            msg = "Please enter your password for {} server: ".format(self.parent_server_name)
            self.set(password=AuthenticationAccount.asking_input['hidden'](msg))

    @abstractmethod
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

    @property
    def authorization_data(self) -> AuthorizationDataType:
        """
        :returns: the authorization data for the service
        """
        self._ensure_account()
        return {'ident': self.username,
                'pass': self.password}

    @property
    def http_basic_auth(self) -> HTTPBasicAuth:
        """
        :returns: the basic HTTP authorization for the service
        :raises RestoClientDesignError: when trying to build authentication while username or
                                        password is undefined.
        """
        self._ensure_account()
        if self.password is None:
            msg = 'Unable to provide http_basic_auth when password undefined'
            raise RestoClientDesignError(msg)
        if self.username is None:
            msg = 'Unable to provide http_basic_auth when username undefined'
            raise RestoClientDesignError(msg)
        return HTTPBasicAuth(self.username.encode('utf-8'), self.password.encode('utf-8'))

    def __str__(self) -> str:
        return 'username: {} / password: {}'.format(self.username, self.password)
