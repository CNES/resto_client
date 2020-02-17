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
from resto_client.requests.base_request import AccesDeniedError

from .authentication_token import AuthenticationToken, RestoClientTokenRenewed


if TYPE_CHECKING:
    from resto_client.services.authentication_service import AuthenticationService  # @UnusedImport

AuthorizationDataType = Dict[str, Optional[str]]


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
        self.parent_server_name = authentication_service.parent_server.server_name

        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._authentication_token = AuthenticationToken(self)

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
                self._authentication_token.reset()
            else:
                self._authentication_token.token_value = token_value

        else:
            # Take the new username definition, either with a password or with a token
            self._username = username.lower()  # resto server imposes lowercase account
            self._password = password
            if token_value is None:
                self._authentication_token.reset()
            else:
                self._authentication_token.token_value = token_value

    def reset(self) -> None:
        """
        Reset the credentials unconditionaly.
        """
        self._username = None
        self._password = None
        self._authentication_token.reset()

    @property
    def token(self) -> Optional[str]:
        """
        :return: the token value associated to these credentials, or None if not available.
        """
        return self._authentication_token.get_current_token_value()

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

    def _ensure_credentials(self) -> None:
        """
        Verify that both username and password are defined, and request their values if it
        is not the case
        """
        if self.username is None:
            msg = "Please enter your username for {} server: ".format(self.parent_server_name)
            self.set(username=AuthenticationCredentials.asking_input['shown'](msg))
        if self.password is None:
            msg = "Please enter your password for {} server: ".format(self.parent_server_name)
            self.set(password=AuthenticationCredentials.asking_input['hidden'](msg))

    @property
    def authorization_data(self) -> AuthorizationDataType:
        """
        :returns: the authorization data for the service
        """
        self._ensure_credentials()
        return {'ident': self.username,
                'pass': self.password}

    @property
    def http_basic_auth(self) -> HTTPBasicAuth:
        """
        :returns: the basic HTTP authorization for the service
        :raises RestoClientDesignError: when trying to build authentication while username or
                                        password is undefined.
        """
        self._ensure_credentials()
        if self.password is None:
            msg = 'Unable to provide http_basic_auth when password undefined'
            raise RestoClientDesignError(msg)
        if self.username is None:
            msg = 'Unable to provide http_basic_auth when username undefined'
            raise RestoClientDesignError(msg)
        return HTTPBasicAuth(self.username.encode('utf-8'), self.password.encode('utf-8'))

    def get_authorization_header(self, authentication_required: bool) -> dict:
        """
        Returns the Authorization headers if possible

        :param authentication_required: If True ensure to retrieve an Authorization header,
                                        otherwise provide it only if a valid token can be
                                        retrieved silently.
        :returns: the authorization header
        """
        username_defined = self.username is not None
        if authentication_required or username_defined:
            self._authentication_token.reset()
        # Get token_value only once in order to avoid unnecessary getter call.
        try:
            return {'Authorization': 'Bearer ' + self._authentication_token.token_value}
        except RestoClientTokenRenewed:
            return {}
        except AccesDeniedError as excp:
            self.reset()
            msg_fmt = 'Access Denied : (username, password) does not fit the server : {}'
            msg_fmt += '\nFollowing denied access, credentials were reset.'
            msg = msg_fmt.format(self.parent_server_name)
            raise AccesDeniedError(msg) from excp

    def __str__(self) -> str:
        return 'username: {} / password: {} \ntoken: {}'.format(self.username,
                                                                self.password,
                                                                self.token)
