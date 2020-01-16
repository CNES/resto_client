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

from resto_client.cli.resto_client_settings import RESTO_CLIENT_SETTINGS
from resto_client.generic.property_decoration import managed_getter, managed_setter


if TYPE_CHECKING:
    from resto_client.services.authentication_service import AuthenticationService  # @UnusedImport


class AuthenticationToken():
    """
    Class implementing the token for a connexion.
    """
    properties_storage = RESTO_CLIENT_SETTINGS

    def __init__(self, authentication_service: 'AuthenticationService') -> None:
        """
        Constructor

        :param authentication_service: parent authentication service for this token.
        """
        self._parent_service = authentication_service

    def reset(self) -> None:
        """
        Reset the token unconditionally.
        """
        self.token = None  # type: ignore

    @classmethod
    def persisted(cls, authentication_service: 'AuthenticationService') -> 'AuthenticationToken':
        """
        Create an instance from persisted attributes (token), connected to a provided
        authentication service.

        :param authentication_service: authentication service onto which this token valid
        :returns: a token instance from the persisted token
        """
        # We only need to create a standard instance, as persisted token will be retrieved at
        # first get(), if it exists.
        return cls(authentication_service)

    @property  # type: ignore
    @managed_getter()
    def token(self) -> Optional[str]:
        """
        :returns: The current token value
        """

    @token.setter  # type: ignore
    @managed_setter(pre_set_func='_check_token')
    def token(self, token_value: str) -> None:
        """
        Set the token value.

        :param token_value: If None, reset the token. If anything else, validate the current
                                   token or renew it if it is invalid.
        """

    def _check_token(self, unused_arg: Any) -> str:
        """
        Check function used by token setter as a callback.

        :returns: the token to use, either the previous one if still valid, or a new valid one
        """
        _ = unused_arg  # to avoid pylint warning
        # Trigger content retrieval from persisted value, if any
        new_token = self.token
        if not self.valid_token():
            new_token = self._parent_service.get_token()  # type: ignore
        return new_token

    def valid_token(self) -> bool:
        """
        :returns: True if the token is still valid, False otherwise
        """
        if self.token is None:
            return False
        return self._parent_service.check_token()

    def update_authorization_header(self,
                                    headers: dict,
                                    token_required: bool,
                                    username_defined: bool) -> None:
        """
        Update the Authorization header if the token is not None or if it is required.

        :param headers: the headers into which the Authorization header must be recorded.
        :param token_required: If True ensure to retrieve an Authorization header, otherwise
                               provide it only if a valid token can be retrieved silently.
        :param username_defined: True if a username is defined in the service credentials.
        """
        if token_required:
            self.token = 'A fake token value to trigger get_token()'   # type: ignore
        else:
            # If the token is valid use it, otherwise renew it if the username is not None
            if not self.valid_token():
                # Token is None or has been revoked. Make sure to store None for persistence
                self.reset()
                if username_defined:
                    self.token = 'A fake token value to trigger get_token()'  # type: ignore
        if self.token is not None:
            headers['Authorization'] = 'Bearer ' + self.token
