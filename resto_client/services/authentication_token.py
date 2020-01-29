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
        self._unvalidated_token = True

    @property
    def token_value(self) -> Optional[str]:
        """
        :returns: The current token, either None or a validated value.
        """
        if self._token_value is not None:
            if self._unvalidated_token:
                self._unvalidated_token = not self.parent_credentials.check_token(self._token_value)
                if self._unvalidated_token:
                    self._token_value = self.parent_credentials.get_token()
                    self._unvalidated_token = self._token_value is None
        return self._token_value

    @token_value.setter
    def token_value(self, token_value: Optional[str]) -> None:
        """
        Set the token value.

        :param token_value: If None, reset the token. If different from current value,
                            validate the current
                                   token or renew it if it is invalid.
        """
        self._unvalidated_token = token_value is None or token_value != self.token_value
        self._token_value = token_value

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
            self.token_value = 'A fake token value to trigger get_token()'
        else:
            if username_defined:
                self.token_value = 'A fake token value to trigger get_token()'
        if self.token_value is not None:
            authorization_header['Authorization'] = 'Bearer ' + self.token_value
        return authorization_header
