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
from abc import ABC, abstractmethod
from typing import Optional, Any, TYPE_CHECKING  # @UnusedImport

from resto_client.base_exceptions import RestoClientDesignError
from resto_client.requests.authentication_requests import (GetTokenRequest, CheckTokenRequest,
                                                           RevokeTokenRequest)
from resto_client.requests.base_request import AccesDeniedError
from resto_client.services.service_access import RestoClientUnsupportedRequest


if TYPE_CHECKING:
    from resto_client.services.authentication_service import AuthenticationService  # @UnusedImport


class RestoClientNoToken(RestoClientDesignError):
    """
    Exception raised when no token is available and can be retrieved
    """


class AuthenticationToken(ABC):
    """
    Class implementing the token for a connexion.
    """

    @property
    @abstractmethod
    def parent_server_name(self) -> str:
        """
        :returns: the name of the parent_server.
        """

    @property
    @abstractmethod
    def parent_service(self) -> 'AuthenticationService':
        """
        :returns: the authentication service associated to this token
        """

    @abstractmethod
    def reset_credentials(self) -> None:
        """
        Reset the credentials unconditionally.
        """

    def __init__(self) -> None:
        """
        Constructor
        """
        self._token_value: Optional[str] = None

    @property
    def current_token(self) -> Optional[str]:
        """

        :returns: the current token value, without trying to update it.
        """
        return self._token_value

    @property
    def token_is_available(self) -> bool:
        """

        :returns: True if a current token value exists.
        """
        return self._token_value is not None

    @property
    def token_value(self) -> str:
        """
        :returns: the current token value or a renewed value if the current token is invalid.
        :raises AccesDeniedError: when authentication is refused when retrieving the token.
        :raises RestoClientNoToken: when server responded without providing a token.
        """
        if self._token_value is None:
            self._renew_token()
            if self._token_value is None:
                raise RestoClientNoToken('No token available and unable to retrieve one')
        return self._token_value

    @token_value.setter
    def token_value(self, token_value: str) -> None:
        """
        Set the token value.

        :param token_value: Store the token assuming that it is  valid.
        :raises TypeError: when trying to set the token to None
        """
        if token_value is None:
            raise TypeError('use AuthenticationToken._reset_token() if you want to reset a token')
        self._token_value = token_value

    def _ensure_token(self) -> None:
        """
        Ensure that we have a valid current token. If we have no current token or if the
        current token is rejected by the service, get a new token.
        """
        if self._token_value is None or not self._check_token(self._token_value):
            self._renew_token()

    def _renew_token(self) -> None:
        """
        Renew the current token unconditionally, by getting a new value from the server
        """
        self._reset_token()
        self.token_value = self._get_token()

    def _reset_token(self) -> None:
        """
        Forget the currently defined token, if any.
        """
        if self._token_value is not None:
            self._revoke_token()
            self._token_value = None

    def get_authorization_header(self) -> dict:
        """
        Returns the Authorization headers if possible

        :returns: the authorization header
        :raises AccesDeniedError: if token retrieval could not be made because of an authentication
                                  error.
        """
        try:
            return {'Authorization': 'Bearer ' + self.token_value}
        except AccesDeniedError as excp:
            self.reset_credentials()
            msg = f'Access Denied : (username, password) does not fit the server:'
            msg += f' {self.parent_server_name}\nFollowing denied access, credentials were reset.'
            raise AccesDeniedError(msg) from excp


# ++++++++ From here we have the calls to the requests handling tokens on the service ++++++++++++
    def _revoke_token(self) -> None:
        """
        Revoke the currently defined token.
        """
        # FIXME: it is surprising that the token value is not passed as an argument.
        try:
            RevokeTokenRequest(self.parent_service).run()
        except RestoClientUnsupportedRequest:
            # We have done our best, but some resto servers does not support RevokeToken.
            # Consider that token was revoked.
            pass

    def _check_token(self, token: str) -> bool:
        """
        Run a check token request.

        :returns: True if the token is valid, False otherwise
        """
        return CheckTokenRequest(self.parent_service, token=token).run()

    def _get_token(self) -> str:
        """
        :returns: a new token to use
        :raises AccesDeniedError: when credentials are not valid for the service.
        """
        return GetTokenRequest(self.parent_service).run()

    def __str__(self) -> str:
        return f'Token value: {self._token_value}'
