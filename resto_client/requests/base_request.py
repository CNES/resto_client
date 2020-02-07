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
import requests
from requests.exceptions import HTTPError, SSLError

from resto_client.base_exceptions import RestoClientDesignError, RestoClientUserError
from resto_client.entities.resto_collection import RestoCollection
from resto_client.entities.resto_collections import RestoCollections
from resto_client.responses.resto_response import RestoResponse  # @UnusedImport
from resto_client.services.base_service import BaseService

from .authenticator import Authenticator


RestoRequestResult = Union[RestoResponse, Path, str,
                           bool, RestoCollection, RestoCollections, requests.Response]


# TODO: move somewhere else?
class AccesDeniedError(RestoClientUserError):
    """
    Exception corresponding to HTTP Error 403
    """


class RestoClientEmulatedResponse(RestoClientDesignError):
    """
    Exception raised when an emulated response is to be processed.
    """
    result: RestoRequestResult


# TODO: extract a RequestRunner side class?
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

    # FIXME: remove url parameters from constructor and make a special method for doing it
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
        self._request_result: requests.Response
        self._url_kwargs = url_kwargs
        Authenticator.__init__(self, self.parent_service.auth_service)

    def get_route(self) -> str:
        """
        :returns: The route pattern of this request
        """
        return self.service_access.get_route_pattern(self)

    def get_url(self) -> str:
        """
        :returns: full url for this request
        :raises RestoClientDesignError: when the request is unsupported by the service
        """
        url_extension = self.get_route()
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
        try:
            self.finalize_request()
        except RestoClientEmulatedResponse as excp:
            return excp.result
        self.run_request()
        return self.process_request_result()

    def finalize_request(self) -> None:
        self.update_headers()
        self.get_route()  # Will trigger an exception if the route is undefined

    def run_request(self) -> None:
        """
        Default is submitting a get request, requesting json response.
        """
        self.update_headers(dict_input={'Accept': 'application/json'})
        self.get_response()

    @abstractmethod
    def process_request_result(self) -> RestoRequestResult:
        pass

    def post(self, stream: bool=False) -> None:
        """
         This create and execute a POST request and store the response content
        """

        try:
            if 'Authorization' in self.request_headers:
                result = requests.post(self.get_url(), headers=self.request_headers,
                                       stream=stream)
            else:
                result = requests.post(self.get_url(), headers=self.request_headers, stream=stream,
                                       auth=self.http_basic_auth, data=self.authorization_data)
            result.raise_for_status()
        except (HTTPError, SSLError) as excp:
            msg = 'Error {} when {} {}.'
            raise Exception(msg.format(result.status_code, self.request_action,
                                       self.get_url())) from excp
        self._request_result = result

    # FIXME: factorize post() and get_response()
    def get_response(self, stream: bool=False) -> None:
        """
         This create and execute a GET request and store the response content
        """
        result = None
        try:
            if 'Authorization' in self.request_headers:
                result = requests.get(self.get_url(), headers=self.request_headers,
                                      auth=None, stream=stream)
            else:
                result = requests.get(self.get_url(), headers=self.request_headers,
                                      auth=self.http_basic_auth, stream=stream)
            result.raise_for_status()

        except (HTTPError, SSLError) as excp:
            if result is not None:
                self._request_result = result
                msg = 'Error {} when {} for {}.'.format(result.status_code, self.request_action,
                                                        self.get_url())
                if result.status_code == 403:
                    raise AccesDeniedError(msg) from excp
            else:
                msg = 'Error when {} for {}.'.format(self.request_action, self.get_url())
            raise Exception(msg) from excp
        self._request_result = result
