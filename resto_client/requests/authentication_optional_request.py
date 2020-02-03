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
from abc import abstractmethod
from typing import Optional, Union, Dict  # @NoMove

from requests import Response
from requests.auth import HTTPBasicAuth

from .base_request import BaseRequest, RestoRequestResult


class AuthenticationOptionalRequest(BaseRequest):
    """
     Base class for several Resto Requests which can request Authentication
    """
    authentication_required = False

    def update_headers(self, dict_input: Optional[dict]=None) -> None:
        """
        Override BaseRequest.update_headers() to add authorization when available or required.

        :param dict_input: entries to add in headers
        """
        super(AuthenticationOptionalRequest, self).update_headers(dict_input)
        authorization_header = self.auth_service.get_authorization_header(
            self.authentication_required)
        super(AuthenticationOptionalRequest, self).update_headers(authorization_header)

    @property
    def http_basic_auth(self) -> Optional[HTTPBasicAuth]:
        """
        :returns: the basic HTTP authorization for the service
        """
        if self.authentication_required:
            return self.auth_service.http_basic_auth
        return super(AuthenticationOptionalRequest, self).http_basic_auth

    @property
    def authorization_data(self) -> Optional[Dict[str, Optional[str]]]:
        """
        :returns: the authorization data for the service
        """
        if self.authentication_required:
            return self.auth_service.authorization_data
        return super(AuthenticationOptionalRequest, self).authorization_data

    @abstractmethod
    def finalize_request(self) -> Optional[dict]:
        pass

    @abstractmethod
    def run_request(self) -> Union[Response, dict]:
        pass

    @abstractmethod
    def process_request_result(self, request_result: Response) -> RestoRequestResult:
        pass
