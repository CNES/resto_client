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
from pathlib import Path
from urllib.parse import urljoin
from typing import Optional, Union, Dict, TYPE_CHECKING  # @UnusedImport @NoMove

from colorama import Fore, Style, colorama_text
from requests import post, Response
from requests.exceptions import HTTPError, SSLError

from resto_client.base_exceptions import RestoClientDesignError
from resto_client.entities.resto_collection import RestoCollection
from resto_client.entities.resto_collections import RestoCollections
from resto_client.responses.resto_response import RestoResponse  # @UnusedImport
from resto_client.services.base_service import BaseService

from .authenticator import Authenticator
from .utils import get_response


RestoRequestResult = Union[RestoResponse, Path, str,
                           bool, RestoCollection, RestoCollections, Response]


# TODO: make request result an attribute of the request runner
class BaseRequest(Authenticator):
    """
     Base class for all service Requests
    """

    @property
    @abstractmethod
    def request_action(self) -> str:
        """
        :returns: the action performed by this request.
        """

    def __init__(self, service: BaseService, **url_kwargs: str) -> None:
        """
        Constructor

        :param service: service
        :param url_kwargs: keyword arguments which must be inserted into the URL pattern.
        :raises TypeError: if the service argument is not derived from :class:`BaseService`.
        """
        # FIXME: Could it be better to check that the route is supported at creation time?
        # Problem: routes for DOnwloadRequests are not parameterized, but come from json response
        if not isinstance(service, BaseService):
            msg_err = 'Argument type must derive from <BaseService>. Found {}'
            raise TypeError(msg_err.format(type(service)))
        self.parent_service = service
        self.service_access = self.parent_service.service_access
        if self.parent_service.parent_server.debug_server:
            with colorama_text():
                msg = 'Building request {} for {}'.format(type(self).__name__,
                                                          self.service_access.base_url)
                print(Fore.CYAN + msg + Style.RESET_ALL)
        self.request_headers: Dict[str, str] = {}
        self._url_kwargs = url_kwargs
        Authenticator.__init__(self, self.parent_service.auth_service)

    def get_route(self) -> Optional[str]:
        """
        :returns: True if this request type is supported by the service, False otherwise.
        """
        return self.service_access.get_route_pattern(self)

    def supported_by_service(self) -> bool:
        """
        :returns: True if this request type is supported by the service, False otherwise.
        """
        return self.get_route() is not None

    def get_url(self) -> str:
        """
        :returns: full url for this request
        :raises RestoClientDesignError: when the request is unsupported by the service
        """
        url_extension = self.get_route()
        if url_extension is None:
            msg_fmt = 'Trying to build an URL for {} request, unsupported by the service.'
            raise RestoClientDesignError(msg_fmt.format(type(self).__name__))
        return urljoin(self.service_access.base_url,
                       url_extension.format(**self._url_kwargs))

    def update_headers(self, dict_input: Optional[dict]=None) -> None:
        """
        Update the headers with dict_input and with authorization header

        :param dict_input: entries to add in headers
        """
        if dict_input is not None:
            self.request_headers.update(dict_input)
        self.update_authorization_headers(self.request_headers)

# ++++++++++++++ Request runner +++++++++++++++++++++++++++++

    @abstractmethod
    def run(self) -> RestoRequestResult:
        """
        Submit the request and provide its result

        :returns: an object of base type (bool, str) or of a type from resto_client.entities
                  directly usable by resto_client.
        """
        fake_response = self.finalize_request()
        if fake_response is None:
            request_result = self.run_request()
            return self.process_request_result(request_result)
        return self.process_dict_result(fake_response)

    def finalize_request(self) -> Optional[dict]:
        self.update_headers()

    def run_request(self) -> Response:
        # Default is submitting a get request, requesting json response.
        return self.get_response_as_json()

    @abstractmethod
    def process_request_result(self, request_result: Response) -> RestoRequestResult:
        pass

    def process_dict_result(self, request_result: dict) -> RestoRequestResult:
        pass

    # FIXME/ Return type seems to always be a dict?
    def get_as_json(self) -> Union[dict, list, str, int, float, bool, None]:
        """
         This create and execute a GET request and return the response content interpreted as json
         or None if no json can be found
        """
        result = self.get_response_as_json()
        return result.json()

    def get_response_as_json(self) -> Response:
        """
         This create and execute a GET request imposing json response
        """
        self.update_headers(dict_input={'Accept': 'application/json'})
        return get_response(self.get_url(), self.request_action,
                            headers=self.request_headers, auth=self.http_basic_auth)

    def post(self, stream: bool=False) -> Response:
        """
         This create and execute a POST request and return the response content
        """

        try:
            if 'Authorization' in self.request_headers:
                result = post(self.get_url(), headers=self.request_headers,
                              stream=stream)
            else:
                result = post(self.get_url(), headers=self.request_headers, stream=stream,
                              auth=self.http_basic_auth, data=self.authorization_data)
            result.raise_for_status()
        except (HTTPError, SSLError) as excp:
            msg = 'Error {} when {} {}.'
            raise Exception(msg.format(result.status_code, self.request_action,
                                       self.get_url())) from excp
        return result
