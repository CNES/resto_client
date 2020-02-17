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
from typing import Optional, Any, TYPE_CHECKING  # @UnusedImport

from resto_client.base_exceptions import RestoClientDesignError
from resto_client.requests.authentication_requests import (GetTokenRequest, CheckTokenRequest,
                                                           RevokeTokenRequest)
from resto_client.requests.base_request import AccesDeniedError
from resto_client.services.service_access import RestoClientUnsupportedRequest


if TYPE_CHECKING:
    from .authentication_credentials import AuthenticationCredentials  # @UnusedImport


class RestoClientTokenRenewed(RestoClientDesignError):
    """
    Exception raised when trying to get token value while its renewal is ongoing
    """


class RestoClientNoToken(RestoClientDesignError):
    """
    Exception raised when no token is available and can be retrieved
    """


class AuthenticationToken():
    """
    Class implementing the token for a connexion.
    """

    def __init__(self, parent_credentials: 'AuthenticationCredentials') -> None:
        """
        Constructor

        :param parent_credentials: parent credentials of this token.
        """
        # FIXME: replace parent_credentials by parent_service (credentiass are not needed here)
        self.parent_credentials = parent_credentials
        self._token_value: Optional[str] = None
        self._being_renewed = False
        self._being_revoked = False

    def get_current_token_value(self) -> Optional[str]:
        """

        :returns: the current token value, without trying to update it.
        """
        return self._token_value

    @property
    def token_value(self) -> str:
        """
        :returns: the current token value or a renewed value if the current token is invalid.
        :raises RestoClientTokenRenewed: when trying to get the token while its renewal is ongoing
        """
        if self._being_renewed or self._being_revoked:
            raise RestoClientTokenRenewed('cannot provide a token while renewal/revoke is ongoing')
        if self._token_value is not None:
            return self._token_value
#         check_ok: bool = self.parent_credentials.check_token(self._token_value)
#         if not check_ok:
        try:
            self.renew()
        except AccesDeniedError:
            self._being_renewed = False
            self._being_revoked = False
            raise
        if self._token_value is None:
            raise RestoClientNoToken('No token available and unable to retrieve one')
        return self._token_value

    @token_value.setter
    def token_value(self, token_value: str) -> None:
        """
        Set the token value.

        :param token_value: Store the token assuming that it is  valid.
        """
        self._token_value = token_value

    def ensure(self) -> None:
        """
        Ensure that we have a valid current token. If we have no current token or if the
        current token is rejected by the service, get a new token.
        """
        if self._token_value is None or not self._check_token(self._token_value):
            self.renew()

    def renew(self) -> None:
        """
        Renew the current token unconditionally, by getting a new value from the server
        """
        # FIXME: decide if renewal management must be kept or not.
        if not self._being_renewed:
            self._being_renewed = True
            self.reset()
            self.token_value = self._get_token()
            self._being_renewed = False

    def reset(self) -> None:
        """
        Forget the currently defined token, if any.
        """
        if self._token_value is not None:
            if not self._being_revoked:
                self._being_revoked = True
                self._revoke_token()
                self._being_revoked = False
            self._token_value = None

# ++++++++ From here we have the calls to the requests handling tokens on the service ++++++++++++
    def _revoke_token(self) -> None:
        """
        Revoke the currently defined token.
        """
        # FIXME: it is surprising that the token value is not passed as an argument.
        try:
            RevokeTokenRequest(self.parent_credentials.parent_service).run()
        except RestoClientUnsupportedRequest:
            # We have done our best, but some resto servers does not support RevokeToken.
            # Consider that token was revoked.
            pass

    def _check_token(self, token: str) -> bool:
        """
        Run a check token request.

        :returns: True if the token is valid, False otherwise
        """
        return CheckTokenRequest(self.parent_credentials.parent_service, token).run()

    def _get_token(self) -> str:
        """
        :returns: a new token to use
        :raises AccesDeniedError: when credentials are not valid for the service.
        """
        return GetTokenRequest(self.parent_credentials.parent_service).run()

    def __str__(self) -> str:
        result_fmt = 'Token status : being_renewed: {} value: {}'
        return result_fmt.format(self._being_renewed, self._token_value)
