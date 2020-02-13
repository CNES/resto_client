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


if TYPE_CHECKING:
    from .authentication_credentials import AuthenticationCredentials  # @UnusedImport


class AuthenticationToken():
    """
    Class implementing the token for a connexion.
    """

    def __init__(self, parent_credentials: 'AuthenticationCredentials') -> None:
        """
        Constructor

        :param parent_credentials: parent credentials of this token.
        """
        self.parent_credentials = parent_credentials
        self._token_value: Optional[str] = None
        self._should_be_valid = False
        self._being_renewed = False

    def __str__(self) -> str:
        result_fmt = 'Token status :\nshould_be_valid: {}  being_renewed: {} value: {}'
        return result_fmt.format(self._should_be_valid, self._being_renewed, self._token_value)

    @property
    def token_value(self) -> Optional[str]:
        """
        :returns: The current token, either None or a validated value.
        """
        if self._being_renewed:
            return None
        if self._token_value is not None:
            if not self._should_be_valid:
                self._should_be_valid = self.parent_credentials.check_token(self._token_value)
                self._renew()
        return self._token_value

    @token_value.setter
    def token_value(self, token_value: Optional[str]) -> None:
        """
        Set the token value.

        :param token_value: If None, reset the token. Otherwise store the token assuming that it is
                            valid.
        """
        self._token_value = token_value
        self._should_be_valid = token_value is not None

    def _renew(self) -> None:
        """
        Renew the current token if it may be invalid, by getting a new value from the server
        """
        if not self._should_be_valid:
            self._force_renew()

    def _force_renew(self) -> None:
        """
        Renew the current token unconditionaly, by getting a new value from the server
        """
        if not self._being_renewed:
            self._being_renewed = True
            self.token_value = self.parent_credentials.get_token()
            self._being_renewed = False

    def get_authorization_header(self,
                                 authentication_required: bool,
                                 username_defined: bool) -> dict:
        """
        Build the Authorization header if the token is not None or if it is required.

        :param authentication_required: If True ensure to retrieve an Authorization header,
                                        otherwise provide it only if a valid token can be
                                        retrieved silently.
        :param username_defined: True if a username is defined in the service credentials.
        :returns: the authorization header
        """
        authorization_header = {}
        if authentication_required:
            self._renew()
        else:
            if username_defined:
                self._renew()
        # Get token_value only once in order to avoid unnecessary getter call.
        tok_value = self.token_value
        if tok_value is not None:
            authorization_header['Authorization'] = 'Bearer ' + tok_value
        return authorization_header
