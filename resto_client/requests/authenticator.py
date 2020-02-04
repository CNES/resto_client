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
from typing import Optional, Dict, TYPE_CHECKING  # @NoMove

from requests.auth import HTTPBasicAuth

if TYPE_CHECKING:
    from resto_client.services.authentication_service import AuthenticationService  # @UnusedImport


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
    def authentication_required(self) -> bool:
        """
        :returns: a flag telling if the request requires authentication or not.
        """
        return self.authentication_type == 'ALWAYS'

    @property
    def anonymous_request(self) -> bool:
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
        if not self.anonymous_request:
            authorization_header = self.auth_service.get_authorization_header(
                self.authentication_required)
            request_header.update(authorization_header)

    @property
    def http_basic_auth(self) -> Optional[HTTPBasicAuth]:
        """
        :returns: the basic HTTP authorization for the service
        """
        if not self.anonymous_request:
            if self.authentication_required:
                return self.auth_service.http_basic_auth
        return None

    @property
    def authorization_data(self) -> Optional[Dict[str, Optional[str]]]:
        """
        :returns: the authorization data for the service
        """
        if not self.anonymous_request:
            if self.authentication_required:
                return self.auth_service.authorization_data
        return None
