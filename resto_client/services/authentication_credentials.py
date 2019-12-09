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

from resto_client.generic.property_decoration import managed_getter, managed_setter
from resto_client.settings.resto_client_settings import RESTO_CLIENT_SETTINGS

from .authentication_token import AuthenticationToken


if TYPE_CHECKING:
    from resto_client.services.authentication_service import AuthenticationService  # @UnusedImport


class AuthenticationCredentials():
    """
    Class implementing the credentials for a connection: username, password.
    """
    asking_input: Dict[str, Callable] = {'shown': input, 'hidden': getpass}
    properties_storage = RESTO_CLIENT_SETTINGS

    def __init__(self, authentication_service: 'AuthenticationService') -> None:
        """
        Constructor

        :param authentication_service: authentication service onto which these credentials are valid
        """
        self.parent_service = authentication_service

        self._password: Optional[str] = None
        self._token = AuthenticationToken(self)

    def set(self, username: Optional[str]=None, password: Optional[str]=None) -> None:
        """
        Set or reset the username or password or both.

        If username is not None, it is set to the provided value if it is different from the
        already stored one and the password is stored whatever its value.
        If username is None and password is not, then only the password is updated with the
        provided value. Otherwise username and password are both reset.

        :param username: the username to register
        :param password: the account password
        """
        if username is None:
            if password is None:
                # Reset username because no new password specified
                self.username = None  # type: ignore
            self._token.reset()
        else:
            username = self._check_username(username)  # normalize username
            # Set username and password if new username is different from stored one.
            if username != self.username:
                self.username = username    # type: ignore # will trigger password reset
                self._token.reset()
        self._password = password  # set password either to None or to a defined value

    def reset(self) -> None:
        """
        Reset the username and password unconditionally.
        """
        self.set(username=None, password=None)

    @classmethod
    def persisted(cls,
                  authentication_service: 'AuthenticationService') -> 'AuthenticationCredentials':
        """
        Create an instance from persisted attributes (username), connected to a provided
        authentication service.

        :param authentication_service: authentication service onto which these credentials are valid
        :returns: a credentials instance from the persisted username
        """
        # We only need to create a standard instance, as persisted username and tokenwill be
        # retrieved at first get(), if they exists.
        persisted_username = cls.properties_storage.get('username')
        instance = cls(authentication_service)
        persisted_token = AuthenticationToken.persisted(instance)
        instance.username = persisted_username  # type: ignore
        instance._token = persisted_token
        return instance

    @property
    def token_value(self) -> Optional[str]:
        """
        :return: the token value associated to these credentials, or None if not available.
        """
        return self._token.token

    @property  # type: ignore
    @managed_getter()
    def username(self) -> Optional[str]:
        """
        :returns: the username
        """

    @username.setter  # type: ignore
    @managed_setter(pre_set_func='_check_username')
    def username(self, username: str) -> None:
        """
        Set the username

        :param username: the username to set
        """
        # Following code is called by managed_setter if and only if base_url has changed.
        # At that time, the property has been updated and can be gotten through the getter.
        _ = username  # to avoid pylint warning

        self._password = None  # reset password
        self._token.reset()  # reset token

    def _check_username(self, username: str) -> str:
        """
        Check function used by username setter as a callback.

        :param username: the resto username to register
        :returns: the lowercased username
        :raises ValueError: when setting username while no server defined.
        """
        # Normalize username as lowercase
        username = username.lower()
        # if there is no service but a try to set account
        if self.parent_service.service_access.base_url is None:
            raise ValueError('You can t set an account without first setting up a server')
        return username

    @property
    def username_b64(self) -> str:
        """

        :returns: the username encoded as base64, suitable to insert in URLs
        """
        return b64encode(self.username.encode('UTF-8')).decode('UTF-8')

    def _ensure_credentials(self) -> None:
        """
        Verify that both username and password are defined, and request their values if it
        is not the case
        """
        if self.username is None:
            msg = "Please enter your username : "
            self.username = AuthenticationCredentials.asking_input['shown'](msg)  # type: ignore
        if self._password is None:
            msg = "Please enter your password : "
            self._password = AuthenticationCredentials.asking_input['hidden'](msg)

    @property
    def authorization_data(self) -> Dict[str, Optional[str]]:
        """
        :returns: the authorization data for the service
        """
        self._ensure_credentials()
        return {'ident': self.username,
                'pass': self._password}

    @property
    def http_basic_auth(self) -> HTTPBasicAuth:
        """
        :returns: the basic HTTP authorization for the service
        """
        self._ensure_credentials()
        return HTTPBasicAuth(self.username, self._password)

    def update_authorization_header(self, headers: dict, token_required: bool) -> None:
        """
        Update the Authorization headers if possible

        :param headers: the headers into which the Authorization header must be recorded.
        :param token_required: If True ensure to retrieve an Authorization header, otherwise
                               provide it only if a valid token can be retrieved silently.
        """
        username_defined = self.username is not None
        self._token.update_authorization_header(headers, token_required, username_defined)

    def __str__(self) -> str:
        return 'username: {} / password: {} \ntoken: {}'.format(self.username,
                                                                self._password,
                                                                self._token.token)
