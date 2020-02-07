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
from typing import Optional, Union, Dict, Callable  # @NoMove @UnusedImport

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


# TODO: move in authenticator?
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
        self._request_headers: Dict[str, str] = {}
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
            self._request_headers.update(dict_input)
        self.update_authorization_headers(self._request_headers)

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
        self.run_request_get()

    @abstractmethod
    def process_request_result(self) -> RestoRequestResult:
        pass

    def run_request_post(self, stream: bool=False) -> None:
        """
         This create and execute a POST request and store the response content
        """
        self._do_run_request(requests.post, stream=stream)

    def run_request_get(self, stream: bool=False) -> None:
        """
         This create and execute a GET request and store the response content
        """
        self._do_run_request(requests.get, stream=stream)

    def _do_run_request(self, method: Callable[..., requests.Response], stream: bool=False) -> None:
        """
         This sends a request using the specified method and stores the response content
        """
        auth_arg, data_arg = self._get_authentication_arguments(self._request_headers)
        result = None
        try:
            result = method(self.get_url(),
                            headers=self._request_headers, stream=stream,
                            auth=auth_arg, data=data_arg)
            result.raise_for_status()

        except (HTTPError, SSLError) as excp:
            if result is not None:
                self._request_result = result
                msg = 'Error {} when {} for {}.'.format(self._request_result.status_code,
                                                        self.request_action, self.get_url())
                if self._request_result.status_code == 403:
                    raise AccesDeniedError(msg) from excp
            else:
                msg = 'Error when {} for {}.'.format(self.request_action, self.get_url())
            raise Exception(msg) from excp
        self._request_result = result
