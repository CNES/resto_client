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
from typing import Optional, Dict  # @NoMove

import requests
from requests.auth import HTTPBasicAuth

from resto_client.requests.authentication_requests import (GetTokenRequest, CheckTokenRequest,
                                                           RevokeTokenRequest)
from resto_client.requests.utils import AccesDeniedError
from resto_client.settings.servers_database import DB_SERVERS

from .authentication_credentials import AuthenticationCredentials
from .base_service import BaseService
from .service_access import AuthenticationServiceAccess


class AuthenticationService(BaseService):
    """
        An authentication Service able to provide tokens, given credentials.
    """

    def __init__(self,
                 auth_access: AuthenticationServiceAccess,
                 username: Optional[str]=None,
                 password: Optional[str]=None) -> None:
        """
        Constructor

        :param auth_access: access to the authentication server.
        :param username: name of the account on the server
        :param password: user password
        """
        super(AuthenticationService, self).__init__(auth_access)
        # Credentials need to exist before calling  update_after_url_change
        self.credentials = AuthenticationCredentials(self)
        self.update_after_url_change()

        # Need to set username before password because username update will reset password
        if username is not None:
            self.credentials.set(username=username, password=password)

    def reset(self) -> None:
        self.credentials.reset()
        super(AuthenticationService, self).reset()

    @property
    def auth_service(self) -> 'AuthenticationService':
        """
        :returns: the authentication service of an AuthenticationService. By definition: self.
        """
        return self

    @classmethod
    def from_name(cls,
                  server_name: str,
                  username: Optional[str]=None,
                  password: Optional[str]=None) -> 'AuthenticationService':
        """
        Build an authentication service from the database of servers

        :param server_name: the name of the server to use in the database
        :param username: name of the account on the server
        :param  password: user password
        :returns: an authentication service corresponding to the server_name
        """
        server_description = DB_SERVERS.get_server(server_name)
        return cls(auth_access=server_description.auth_access, username=username, password=password)

    @classmethod
    def persisted(cls) -> 'AuthenticationService':
        """
        :returns: an authentication service from the persisted authentication access description.
        """
        # Retrieve persisted access to the authentication service
        auth_service_access = AuthenticationServiceAccess.persisted()
        instance = cls(auth_access=auth_service_access)
        instance.credentials = AuthenticationCredentials.persisted(instance)
        return instance

    def update_after_url_change(self) -> None:
        """
        Callback method to update service after base URL was possibly changed.
        """
        self.credentials = AuthenticationCredentials(authentication_service=self)
        self.credentials.set(username=None)

    @property
    def http_basic_auth(self) -> HTTPBasicAuth:
        """
        :returns: the basic HTTP authorization for the service
        """
        return self.credentials.http_basic_auth

    def get_auth_data(self) -> Dict[str, Optional[str]]:
        """
        :returns: the authorization data for the service
        """
        return self.credentials.auth_data

    def update_authorization_header(self, headers: dict, token_required: bool) -> None:
        """
        Update the Authorization header if possible

        :param headers: the headers into which the Authorization header must be recorded.
        :param token_required: If True ensure to retrieve an Authorization header, otherwise
                               provide it only if a valid token can be retrieved silently.
        """
        self.credentials.update_authorization_header(headers, token_required)


# ++++++++ From here we have the supported request to the service ++++++++++++

    def get_token(self) -> str:
        """
        :returns: a new token to use
        :raises AccesDeniedError: when credentials are not valid for the service.
        """
        try:
            new_token = GetTokenRequest(self).run()
        except AccesDeniedError as excp:
            # prevent from saving username by reset
            self.credentials.username = None  # type:ignore
            msg = 'Access Denied : (username, password) does not fit the server : {}'
            msg += '\nFollowing denied access, the username was reset.'
            raise AccesDeniedError(msg.format(self.service_access.base_url)) from excp
        return new_token

    def check_token(self) -> bool:
        """
        :returns: True if the token is still valid
        """
        if self.credentials.token_value is not None:
            return CheckTokenRequest(self, self.credentials.token_value).run()
        return False

    def revoke_token(self) -> Optional[requests.Response]:
        """
        Revoke the currently defined token.

        :returns: unknown result at the moment (not working)
        """
        if self.credentials.token_value is not None:
            return RevokeTokenRequest(self).run()
        return None
