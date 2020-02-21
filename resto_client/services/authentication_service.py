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

from resto_client.base_exceptions import RestoClientDesignError

from .authentication_account import AuthenticationAccount
from .authentication_token import AuthenticationToken
from .base_service import BaseService
from .service_access import AuthenticationServiceAccess


if TYPE_CHECKING:
    from .resto_server import RestoServer  # @UnusedImport


class AuthenticationService(BaseService, AuthenticationAccount, AuthenticationToken):
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
        BaseService.__init__(self, auth_access, self, parent_server)
        AuthenticationAccount.__init__(self)
        AuthenticationToken.__init__(self)

    @property
    def parent_server_name(self) -> str:
        """
        :returns: the name of the parent_server.
        """
        return self.parent_server.server_name

    @property
    def parent_service(self) -> 'AuthenticationService':
        """
        :returns: the name of the parent_server.
        """
        return self

    def set_credentials(self,
                        username: Optional[str]=None,
                        password: Optional[str]=None,
                        token_value: Optional[str]=None) -> None:
        """
        Set the credentials to be used by this authentication service.

        If username is not None, it is set to the provided value if it is different from the
        already stored one and the password is stored whatever its value.
        If username is None and password is not, then only the password is updated with the
        provided value. Otherwise username and password are both reset.

        :param username: name of the account on the server
        :param password: account password
        :param token_value: a token associated to these credentials
        :raises RestoClientDesignError: when an unconsistent set of arguments is provided
        """
        if username is None and password is None and token_value is None:
            # don't change anything
            return

        if password is not None and token_value is not None:
            msg = 'Cannot define or change simultaneously password and token'
            raise RestoClientDesignError(msg)

        if username is None and self._username is None:
            msg = 'Cannot change password and/or token when username is undefined.'
            raise RestoClientDesignError(msg)

        # Record the new account definition and reset current token if account was changed
        account_changed = self._set_account(username=username, password=password)
        if account_changed:
            self._reset_token()

        # We have an account and want to set its token.
        if token_value is not None:
            self.token_value = token_value

    def reset_credentials(self) -> None:
        """
        Reset the credentials unconditionally.
        """
        self._reset_account()
        self._reset_token()

    def __str__(self) -> str:
        credentials_str = 'username: {} / password: {} / token: {}'.format(self.username,
                                                                           self.password,
                                                                           self.current_token)

        return super(AuthenticationService, self).__str__() + credentials_str
