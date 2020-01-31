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
from urllib.parse import urljoin

from typing import Optional, Union, Dict, TYPE_CHECKING  # @UnusedImport @NoMove

from colorama import Fore, Style, colorama_text
from requests import post, Response
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError, SSLError

from resto_client.base_exceptions import RestoClientDesignError
from resto_client.entities.resto_collection import RestoCollection
from resto_client.entities.resto_collections import RestoCollections
from resto_client.services.base_service import BaseService

from .utils import AccesDeniedError, get_response


if TYPE_CHECKING:
    from resto_client.responses.resto_response import RestoResponse  # @UnusedImport


class BaseRequest(ABC):
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
        self.headers: Dict[str, str] = {}
        if not isinstance(service, BaseService):
            msg_err = 'Argument type must derive from <BaseService>. Found {}'
            raise TypeError(msg_err.format(type(service)))
        self.parent_service = service
        self.service_access = self.parent_service.service_access
        self.auth_service = self.parent_service.auth_service
        self._url_kwargs = url_kwargs
        if self.parent_service.parent_server.debug_server:
            with colorama_text():
                msg = 'Building request {} for {}'.format(type(self).__name__,
                                                          self.service_access.base_url)
                print(Fore.CYAN + msg + Style.RESET_ALL)

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
        Update the current headers with dic_input

        :param dict_input: entry to add in headers
        """
        if dict_input is not None:
            self.headers.update(dict_input)

    @abstractmethod
    def run(self) -> Union['RestoResponse', str, bool, RestoCollection, RestoCollections, None,
                           Response]:
        """
        Submit the request and provide its result

        :returns: an object of base type (bool,, str) or of a type from resto_client.entities
                  directly usable by resto_client.
        """

    @property
    def http_basic_auth(self) -> Optional[HTTPBasicAuth]:
        """
        The default basic HTTP authorization for the service (None)
        """
        return None

    @property
    def authorization_data(self) -> Optional[Dict[str, Optional[str]]]:
        """
        The default authorization data for the service (None)
        """
        return None

    def get_as_json(self) -> Union[dict, list, str, int, float, bool, None]:
        """
         This create and execute a GET request and return the response content interpreted as json
         or None if no json can be found
        """
        BaseRequest.update_headers(self, {'Accept': 'application/json'})
        result = get_response(self.get_url(), self.request_action,
                              headers=self.headers, auth=self.http_basic_auth)
        return result.json()

    def post_as_text(self, stream: bool=False) -> Optional[str]:
        """
         This create and execute a POST request and return the response content interpreted as text
         or None if no text can be found
        """
        result = self.post(stream=stream)
        response_text = result.text
        if response_text == 'Please set mail and password':
            msg = 'Connection Error : "{}", connection not allowed with ident/pass given'
            raise AccesDeniedError(msg.format(response_text))
        return response_text

    def post(self, stream: bool=False) -> Response:
        """
         This create and execute a POST request and return the response content
        """

        try:
            if 'Authorization' in self.headers:
                result = post(self.get_url(), headers=self.headers,
                              stream=stream)
            else:
                result = post(self.get_url(), headers=self.headers, auth=self.http_basic_auth,
                              stream=stream, data=self.authorization_data)
            result.raise_for_status()
        except (HTTPError, SSLError) as excp:
            msg = 'Error {} when {} {}.'
            raise Exception(msg.format(result.status_code, self.request_action,
                                       self.get_url())) from excp
        return result
