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

from requests.auth import HTTPBasicAuth

from .authentication_credentials import AuthenticationCredentials, AuthorizationDataType
from .base_service import BaseService
from .service_access import AuthenticationServiceAccess

if TYPE_CHECKING:
    from .resto_server import RestoServer  # @UnusedImport


class AuthenticationService(BaseService):
    """
        An authentication Service able to provide tokens, given credentials.
    """

    def __init__(self, auth_access: AuthenticationServiceAccess,
                 parent_server: 'RestoServer') -> None:
        """
        Constructor

        :param auth_access: access to the authentication server.
        :param parent_server: Server which uses this service.
        """
        super(AuthenticationService, self).__init__(auth_access, self, parent_server)
        self._credentials = AuthenticationCredentials(authentication_service=self)

    @property
    def username(self) -> Optional[str]:
        """
        :returns: the username to use with this authentication service
        """
        return self._credentials.username

    @property
    def account_defined(self) -> bool:
        """
        :returns: True if username and password are defined, but not necessarily valid.
        """
        return self._credentials.account_defined

    @property
    def token(self) -> Optional[str]:
        """
        :return: the token value currently active on this AuthenticationService, or None.
        """
        return self._credentials.token

    @property
    def token_available(self) -> bool:
        """
        :returns: True if username and password are defined, but not necessarily valid.
        """
        return self._credentials.token_available

    def reset_credentials(self) -> None:
        """
        Reset the credentials used by this authentication service.
        """
        self._credentials.reset()

    def set_credentials(self,
                        username: Optional[str]=None,
                        password: Optional[str]=None,
                        token_value: Optional[str]=None) -> None:
        """
        Set the credentials to be used this authentication service.

        :param username: name of the account on the server
        :param password: account password
        :param token_value: a token associated to these credentials
        """
        self._credentials.set(username=username, password=password, token_value=token_value)

    @property
    def http_basic_auth(self) -> HTTPBasicAuth:
        """
        :returns: the basic HTTP authorization for the service
        """
        return self._credentials.http_basic_auth

    @property
    def username_b64(self) -> str:
        """
        :returns: the base64 username associated to this service
        """
        return self._credentials.username_b64

    @property
    def authorization_data(self) -> AuthorizationDataType:
        """
        :returns: the authorization data for the service
        """
        return self._credentials.authorization_data

    def get_authorization_header(self) -> dict:
        """
        Get the Authorization header if possible

        :returns: the authorization header
        """
        return self._credentials.get_authorization_header()

    def __str__(self) -> str:
        return super(AuthenticationService, self).__str__() + '\n' + str(self._credentials)
