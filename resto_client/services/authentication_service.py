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

from .authentication_credentials import AuthenticationCredentials
from .base_service import BaseService
from .service_access import AuthenticationServiceAccess


class AuthenticationService(BaseService):
    """
        An authentication Service able to provide tokens, given credentials.
    """

    def __init__(self, auth_access: AuthenticationServiceAccess) -> None:
        """
        Constructor

        :param auth_access: access to the authentication server.
        """
        super(AuthenticationService, self).__init__(auth_access)
        self._credentials = AuthenticationCredentials(authentication_service=self)

    def reset(self) -> None:
        self._credentials.reset()
        super(AuthenticationService, self).reset()

    def set_credentials(self, credentials: Optional[AuthenticationCredentials]=None,
                        username: Optional[str]=None, password: Optional[str]=None) -> None:
        """
        Set the credentials associated to this authentication service, either by providing
        a AuthenticationCredentials object or by specifying username or password or both.

        :param credentials: Credentials to associate to this authentication service
        :param username: name of the account on the server
        :param  password: user password
        """
        if credentials is not None:
            self._credentials = credentials
        else:
            self._credentials.set(username=username, password=password)

    def update_after_url_change(self) -> None:
        """
        Callback method to update service after base URL was possibly changed.
        """
        self._credentials.set()

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
    def authorization_data(self) -> Dict[str, Optional[str]]:
        """
        :returns: the authorization data for the service
        """
        return self._credentials.authorization_data

    def update_authorization_header(self, headers: dict, token_required: bool) -> None:
        """
        Update the Authorization header if possible

        :param headers: the headers into which the Authorization header must be recorded.
        :param token_required: If True ensure to retrieve an Authorization header, otherwise
                               provide it only if a valid token can be retrieved silently.
        """
        self._credentials.update_authorization_header(headers, token_required)


# ++++++++ From here we have the requests supported by the service ++++++++++++

    def get_token(self) -> str:
        """
        :returns: a new token to use
        :raises AccesDeniedError: when credentials are not valid for the service.
        """
        try:
            new_token = GetTokenRequest(self).run()
        except AccesDeniedError as excp:
            # prevent from saving username by reset
            print(self._credentials.username)
            print(self._credentials._password)
            self._credentials.set()  # reset username and password
            msg = 'Access Denied : (username, password) does not fit the server : {}'
            msg += '\nFollowing denied access, the username was reset.'
            raise AccesDeniedError(msg.format(self.service_access.base_url)) from excp
        return new_token

    def check_token(self) -> bool:
        """
        :returns: True if the token is still valid
        """
        if self._credentials.token_value is not None:
            return CheckTokenRequest(self, self._credentials.token_value).run()
        return False

    def revoke_token(self) -> Optional[requests.Response]:
        """
        Revoke the currently defined token.

        :returns: unknown result at the moment (not working)
        """
        if self._credentials.token_value is not None:
            return RevokeTokenRequest(self).run()
        return None

    def __str__(self) -> str:
        return super(AuthenticationService, self).__str__() + '\n' + str(self._credentials)
