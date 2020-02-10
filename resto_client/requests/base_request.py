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


# TODO: move in a module for requests specific exceptions
class AccesDeniedError(RestoClientUserError):
    """
    Exception corresponding to HTTP Error 403
    """


class RestoClientEmulatedResponse(RestoClientDesignError):
    """
    Exception raised when an emulated response is to be processed.
    """
    result: RestoRequestResult


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
        if not isinstance(service, BaseService):
            msg_err = 'Argument type must derive from <BaseService>. Found {}'
            raise TypeError(msg_err.format(type(service)))
        self.parent_service = service
        self.debug = self.parent_service.parent_server.debug_server
        if self.debug:
            with colorama_text():
                msg = 'Building request {} for {}'.format(type(self).__name__,
                                                          self.parent_service.get_base_url())
                print(Fore.CYAN + msg + Style.RESET_ALL)
        self._request_headers: Dict[str, str] = {}
        self._request_result: requests.Response
        self._url_kwargs = url_kwargs
        Authenticator.__init__(self, self.parent_service.auth_service)

    def get_server_name(self) -> Optional[str]:
        """
        :returns: the name of the server which uses this request.
        """
        return self.parent_service.parent_server.server_name

    def get_route(self) -> str:
        """
        :returns: The route pattern of this request
        """
        return self.parent_service.service_access.get_route_pattern(self)

    def get_protocol(self) -> str:
        """
        :returns: The protocol of this request
        """
        return self.parent_service.get_protocol()

    def get_url(self) -> str:
        """
        :returns: full url for this request
        """
        url_extension = self.get_route()
        return urljoin(self.parent_service.get_base_url(),
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
        THis is the main method of the request runner. Subclasses should override this method
        only for specifying the right return type that they are committed to return and which
        may differ from one request to the other.

        This method run the request in 3 steps :

        1. prepare the request. This must set _request_headers attribute to the desired state
        2. run the request. The request result is made available in  _request_result attribute
        3. process the request result

        Each of these steps is implemented by a dedicated method, and these are the only methods
        which should be overridden by the client classes.

        A special processing is done for what concerns exception handling:

        1- if request preparation raises a RestoClientEmulatedResponse, the request response
           is directly returned from the 'result' attribute of that exception
        2- TBD

        :returns: an object of one the types defined by RestoRequestResult,
                  directly usable by resto_client.
        """
        try:
            self.finalize_request()
        except RestoClientEmulatedResponse as excp:
            return excp.result
        # FIXME: filter https protocol exceptions and send others to process_request_result
        self.run_request()
        return self.process_request_result()

    def finalize_request(self) -> None:
        """
        Prepare the request before running it. This method may be overidden by client classes to
        set the headers or change the URL in order to fulfill their needs.
        Base class method update the headers, possibly setting the authentication headers and
        checks that the route is available.
        """
        self.update_headers()
        self.get_route()  # Will trigger an exception if the route is undefined

    def run_request(self) -> None:
        """
        Run the requests. This method may be overidden by client classes to select the method that
        suit their needs. Default is submitting a get request, requesting json response.
        """
        self.update_headers(dict_input={'Accept': 'application/json'})
        self._run_request_get()

    @abstractmethod
    def process_request_result(self) -> RestoRequestResult:
        """
        Method to be implemented by each request in order to process the content of the request
        response (self._request_result) and return a valid RestoRequestResult.
        """

    def _run_request_post(self, stream: bool=False) -> None:
        """
        Create and execute a POST request and store the response content

        :param stream: If True, only the response header will be retrieved, allowing to drive
                       the retrieval of the full response body within process_request_result()
        """
        self._do_run_request(requests.post, stream=stream)

    def _run_request_get(self, stream: bool=False) -> None:
        """
        Create and execute a GET request and store the response content

        :param stream: If True, only the response header will be retrieved, allowing to drive
                       the retrieval of the full response body within process_request_result()
        """
        self._do_run_request(requests.get, stream=stream)

    def _do_run_request(self, method: Callable[..., requests.Response], stream: bool=False) -> None:
        """
        Send the request using the specified method and stores the response content

        :param method: method to use for sending the request: requests.get() or requests.post()
        :param stream: If True, only the response header will be retrieved, allowing to drive
                       the retrieval of the full response body within process_request_result()
        :raises AccesDeniedError: if the request was refused because authentication failed.
        :raises Exception: for other exceptions
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
                # FIXME: Processing to be made by process_request_result ofclient classes
                msg = 'Error {} when {} for {}.'.format(self._request_result.status_code,
                                                        self.request_action, self.get_url())
                if self._request_result.status_code == 403:
                    raise AccesDeniedError(msg) from excp
            else:
                msg = 'Error when {} for {}.'.format(self.request_action, self.get_url())
            raise Exception(msg) from excp
        self._request_result = result
