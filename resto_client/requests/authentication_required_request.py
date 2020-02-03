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
from typing import Dict, Union, Optional  # @NoMove

from requests import Response
from requests.auth import HTTPBasicAuth

from .authentication_optional_request import AuthenticationOptionalRequest
from .base_request import RestoRequestResult


class AuthenticationRequiredRequest(AuthenticationOptionalRequest):
    """
     Base class for several Resto Requests which do need authentication
    """
    authentication_required = True

    @property
    def http_basic_auth(self) -> HTTPBasicAuth:
        """
        :returns: the basic HTTP authorization for the service
        """
        return self.auth_service.http_basic_auth

    @property
    def authorization_data(self) -> Dict[str, Optional[str]]:
        """
        :returns: the authorization data for the service
        """
        return self.auth_service.authorization_data

    @abstractmethod
    def finalize_request(self) -> Optional[dict]:
        pass

    @abstractmethod
    def run_request(self) -> Union[Response, dict]:
        pass

    @abstractmethod
    def process_request_result(self, request_result: Response) -> RestoRequestResult:
        pass
