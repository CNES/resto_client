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
from typing import Union, Dict, Optional  # @NoMove

from requests import Response
from requests.auth import HTTPBasicAuth

from resto_client.responses.resto_response import RestoResponse

from .authentication_optional_request import AuthenticationOptionalRequest


class AuthenticationRequiredRequest(AuthenticationOptionalRequest):
    """
     Base class for several Resto Requests which do need authentication
    """
    token_required = True

    @property
    def authorization(self) -> HTTPBasicAuth:
        """
        :returns: the authorization for the service
        """
        return self.auth_service.get_http_basic_auth()

    @property
    def authorization_data(self) -> Dict[str, Optional[str]]:
        """
        :returns: the authorization for the service
        """
        return self.auth_service.get_auth_data()

    @abstractmethod
    def run(self) -> Union[RestoResponse, bool, str, None, Response]:
        pass
