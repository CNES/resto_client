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
from typing import Optional, Tuple, TYPE_CHECKING  # @NoMove

import requests


if TYPE_CHECKING:
    from resto_client.services.authentication_service import AuthenticationService  # @UnusedImport
    from resto_client.services.authentication_account import AuthorizationDataType  # @UnusedImport


class Authenticator(ABC):
    """
     Base class for all requests managing the request Authentication
    """

    @property
    @abstractmethod
    def authentication_type(self) -> str:
        """
        :returns: the authentication type of this request (NEVER or ALWAYS or OPPORTUNITY)
        """

    @property
    def _authentication_required(self) -> bool:
        """
        :returns: a flag telling if the request requires authentication or not.
        """
        return self.authentication_type == 'ALWAYS'

    @property
    def _anonymous_request(self) -> bool:
        """
        :returns: a flag telling if the request does not require authentication.
        """
        return self.authentication_type == 'NEVER'

    def __init__(self, service: 'AuthenticationService') -> None:
        """
        Constructor

        :param service: authentication service
        """
        self.auth_service = service

    def update_authorization_headers(self, request_header: dict) -> None:
        """
        :param request_header: the request headers to update with the authorization part
        """
        if self._authentication_required:
            authorization_header = self.auth_service.get_authorization_header()
            request_header.update(authorization_header)
            return
        if self.authentication_type == 'OPPORTUNITY' and (self.auth_service.account_defined or
                                                          self.auth_service.token_available):
            authorization_header = self.auth_service.get_authorization_header()
            request_header.update(authorization_header)
            return

    def _get_authentication_arguments(self, request_headers: dict) -> \
            Tuple[Optional[requests.auth.HTTPBasicAuth], Optional['AuthorizationDataType']]:
        """
         This create and execute a POST request and store the response content
        """
        if 'Authorization' in request_headers:
            return None, None
        return self.http_basic_auth, self.authorization_data

    @property
    def http_basic_auth(self) -> Optional[requests.auth.HTTPBasicAuth]:
        """
        :returns: the basic HTTP authorization for the request
        """
        return self.auth_service.http_basic_auth if self._authentication_required else None

    @property
    def authorization_data(self) -> Optional['AuthorizationDataType']:
        """
        :returns: the authorization data for the request
        """
        return self.auth_service.authorization_data if self._authentication_required else None
