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
from typing import Optional, Union  # @NoMove
from requests import Response

from resto_client.responses.resto_response import RestoResponse
from resto_client.services.base_service import BaseService

from .base_request import BaseRequest


class AuthenticationOptionalRequest(BaseRequest):
    """
     Base class for several Resto Requests which can request Authentication
    """
    authentication_required = False

    def __init__(self, service: BaseService, **url_kwargs: str) -> None:
        """
        Constructor

        :param service: service
        :param url_kwargs: keyword arguments which must be inserted into the URL pattern.
        :raises RestoClientDesignError: when the service is not of the right type
        """
        super(AuthenticationOptionalRequest, self).__init__(service, **url_kwargs)
        self.auth_service = service.auth_service

    def set_headers(self, dict_input: Optional[dict]=None) -> None:
        """
        Set headers because parent's abstract method

        :param dict_input: entries to add in headers
        """
        super(AuthenticationOptionalRequest, self).set_headers(dict_input)
        self.auth_service.update_authorization_header(self.headers, self.authentication_required)

    @abstractmethod
    def run(self) -> Union[RestoResponse, bool, str, None, Response]:
        pass
