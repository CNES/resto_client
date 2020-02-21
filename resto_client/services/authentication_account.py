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
from typing import Optional, Dict, Callable  # @UnusedImport @NoMove
from abc import ABC, abstractmethod
from base64 import b64encode
from getpass import getpass

from requests.auth import HTTPBasicAuth

from resto_client.base_exceptions import RestoClientDesignError

AuthorizationDataType = Dict[str, Optional[str]]


class AuthenticationAccount(ABC):
    """
    Class implementing the account for a connection: username, password.
    """
    asking_input: Dict[str, Callable] = {'shown': input, 'hidden': getpass}

    def __init__(self, server_name: str) -> None:
        """
        Constructor
        """
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self.server_name = server_name

    def _set_account(self, username: Optional[str]=None, password: Optional[str]=None) -> bool:
        """
        Set or reset the username and the password.

        If username is not None, it is set to the provided value if it is different from the
        already stored one and the password is stored whatever its value.
        If username is None and password is not, then only the password is updated with the
        provided value. Otherwise username and password are both reset.

        :param username: the username to register
        :param password: the account password
        :returns: True if username and or password has been changed, False otherwise
        :raises RestoClientDesignError: when an unconsistent set of arguments is provided
        """
        change_username = True
        change_password = password != self._password
        if self._username is None and self._password is None:
            if username is None and password is not None:
                msg = 'Cannot set password because no username has been defined yet.'
                raise RestoClientDesignError(msg)
            change_username = username is not None

        if self._username is not None:
            if username is None:
                change_username = password is None
            else:
                change_username = username.lower() != self._username

        if change_username:
            self._username = username
        if change_password:
            self._password = password

        return change_username or change_password

    def _reset_account(self) -> None:
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
            msg = f'Please enter your username for {self.server_name} server: '
            new_username = AuthenticationAccount.asking_input['shown'](msg)
            self.set_credentials(username=new_username)
        if self.password is None:
            msg = f'Please enter your password for {self.server_name} server: '
            new_password = AuthenticationAccount.asking_input['hidden'](msg)
            self.set_credentials(password=new_password)

    # We have to define set_credentials as abstract because we need it to propagate
    # token reinitialization when defining new account via _ensure_account
    @abstractmethod
    def set_credentials(self,
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
        return f'username: {self.username} / password: {self.password}'
