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
from base64 import b64encode
from getpass import getpass

from requests.auth import HTTPBasicAuth

from resto_client.base_exceptions import RestoClientDesignError

from .authentication_token import AuthenticationToken


if TYPE_CHECKING:
    from resto_client.services.authentication_service import AuthenticationService  # @UnusedImport


class AuthenticationCredentials():
    """
    Class implementing the credentials for a connection: username, password.
    """
    asking_input: Dict[str, Callable] = {'shown': input, 'hidden': getpass}

    def __init__(self, authentication_service: 'AuthenticationService') -> None:
        """
        Constructor

        :param authentication_service: authentication service onto which these credentials are valid
        """
        self.parent_service = authentication_service

        self._password: Optional[str] = None
        self._authentication_token = AuthenticationToken(self)
        self._username: Optional[str] = None

    def set(self, username: Optional[str]=None, password: Optional[str]=None) -> None:
        """
        Set or reset the username or password or both.

        If username is not None, it is set to the provided value if it is different from the
        already stored one and the password is stored whatever its value.
        If username is None and password is not, then only the password is updated with the
        provided value. Otherwise username and password are both reset.

        :param username: the username to register
        :param password: the account password
        """
        if username is None:
            if password is None:
                # Reset username because no new password specified
                self.username = None
            self._authentication_token.reset()
        else:
            username = username.lower()  # normalize username
            # Set username and password if new username is different from stored one.
            if username != self.username:
                self.username = username    # type: ignore # will trigger password reset
                self._authentication_token.reset()
        self._password = password  # set password either to None or to a defined value

    def reset(self) -> None:
        """
        Reset the username and password unconditionally.
        """
        self.set(username=None, password=None)

    @property
    def token(self) -> Optional[str]:
        """
        :return: the token value associated to these credentials, or None if not available.
        """
        return self._authentication_token.token_value

    @token.setter
    def token(self, token: str) -> None:
        self._authentication_token.token_value = token

    @property
    def username(self) -> Optional[str]:
        """
        :returns: the username
        """
        return self._username

    @username.setter
    def username(self, username: Optional[str]) -> None:
        if username is not None:
            username = username.lower()
            if username == self._username:
                # Nothing to change
                return
        self._username = username
        self._password = None  # reset password
        self._authentication_token.reset()  # reset token

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

    def _ensure_credentials(self) -> None:
        """
        Verify that both username and password are defined, and request their values if it
        is not the case
        """
        if self.username is None:
            msg = "Please enter your username : "
            self.username = AuthenticationCredentials.asking_input['shown'](msg)
        if self._password is None:
            msg = "Please enter your password : "
            self._password = AuthenticationCredentials.asking_input['hidden'](msg)

    @property
    def authorization_data(self) -> Dict[str, Optional[str]]:
        """
        :returns: the authorization data for the service
        """
        self._ensure_credentials()
        return {'ident': self.username,
                'pass': self._password}

    @property
    def http_basic_auth(self) -> HTTPBasicAuth:
        """
        :returns: the basic HTTP authorization for the service
        :raises RestoClientDesignError: when trying to build authentication while username or
                                        password is undefined.
        """
        self._ensure_credentials()
        if self._password is None:
            msg = 'Unable to provide http_basic_auth when password undefined'
            raise RestoClientDesignError(msg)
        if self.username is None:
            msg = 'Unable to provide http_basic_auth when username undefined'
            raise RestoClientDesignError(msg)
        return HTTPBasicAuth(self.username.encode('utf-8'), self._password.encode('utf-8'))

    def get_authorization_header(self, authentication_required: bool) -> dict:
        """
        Returns the Authorization headers if possible

        :param authentication_required: If True ensure to retrieve an Authorization header,
                                        otherwise provide it only if a valid token can be
                                        retrieved silently.
        :returns: the authorization header
        """
        username_defined = self.username is not None
        return self._authentication_token.get_authorization_header(authentication_required,
                                                                   username_defined)

    def check_token(self) -> bool:
        return self.parent_service.check_token()

    def get_token(self) -> str:
        return self.parent_service.get_token()

    def __str__(self) -> str:
        return 'username: {} / password: {} \ntoken: {}'.format(self.username,
                                                                self._password,
                                                                self.token)
