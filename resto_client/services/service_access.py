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
import copy
from typing import List, Dict, Union, TypeVar, Optional, TYPE_CHECKING  # @NoMove @UnusedImport
from urllib.parse import urljoin

from resto_client.base_exceptions import RestoClientUserError, RestoClientDesignError
from resto_client.generic.basic_types import URLType


if TYPE_CHECKING:
    from resto_client.requests.base_request import BaseRequest  # @UnusedImport

SA = TypeVar('SA', bound='ServiceAccess')

RoutesPatternsType = Dict[str, Dict[str, Dict[str, str]]]
"""
Routes patterns for a service are described in a dictionary whose key is the service protocol
and the value is another dictionary. This second dictionary has the request class name as its key,
and the route itself as the value. This route can be None in case it is not defined for some
protocol.
"""


class RestoClientUnsupportedRequest(RestoClientDesignError):
    """
    Exception raised when a request is unsupported by the service access.
    """


class ServiceAccess(ABC):
    """
    Abstract class holding the 2 parameters defining a service access: its URL and its protocol.

    Concrete class must define the protocols they support.
    """

    @classmethod
    @abstractmethod
    def routes_patterns(cls) -> RoutesPatternsType:
        """
        :returns: the set of routes patterns used by the service access.
        """

    @classmethod
    def supported_protocols(cls) -> List[str]:
        """
        :returns: the protocols supported by this type of service.
        """
        return list(cls.routes_patterns().keys())

    @classmethod
    @abstractmethod
    def service_type(cls) -> str:
        """
        :returns: the type of the service (e.g. 'resto', 'auth', etc.). Used for indexing purposes.
        """

    def __init__(self,
                 service_url: str,
                 service_protocol: str) -> None:
        """
        Constructor.

        :param service_url: the URL at which the service is available.
        :param service_protocol: the protocol implemented by the service.
        """
        self.detected_protocol: Optional[str] = None
        self.base_url = service_url
        self.protocol = service_protocol

    def get_route_pattern(self, request: 'BaseRequest') -> str:
        """
        Returns the route pattern for a request

        :param request: the request instance for which route must be found.
        :returns: the route pattern
        """
        return self._get_route_description_item(request, 'rel_url')

    def get_method(self, request: 'BaseRequest') -> str:
        """
        Returns the sending method for a request

        :param request: the request instance for which method must be found.
        :returns: the method
        """
        return self._get_route_description_item(request, 'method')

    def get_accept(self, request: 'BaseRequest') -> str:
        """
        Returns the response format accepted by a request

        :param request: the request instance for which response format must be found.
        :returns: the response format
        """
        return self._get_route_description_item(request, 'accept')

    def get_authentication(self, request: 'BaseRequest') -> str:
        """
        Returns the authentication type used by a request. Can be one of 'NEVER', 'ALWAYS',
        'OPPORTUNITY'.

        :param request: the request instance for which authentication type must be found.
        :returns: the authentication type
        """
        return self._get_route_description_item(request, 'authentication')

    def _get_route_description_item(self, request: 'BaseRequest', item: str) -> str:
        """
        Returns an item of the route description for a request

        :param request: the request instance for which route description must be found.
        :param item: name of the item to retrieve in  the route description.
        :returns: the item value
        :raises RestoClientUnsupportedRequest: when the item is not found in the route description.
        """
        route_descr = self._get_route_description(request)
        try:
            item_value = route_descr[item]
        except KeyError:
            msg = 'Item {} for {} request is undefined in route patterns for {} server.'
            raise RestoClientUnsupportedRequest(
                msg.format(item, type(request).__name__, request.get_server_name()))
        return item_value

    def _get_route_description(self, request: 'BaseRequest') -> Dict[str, str]:
        """
        Returns the route description for a request

        :param request: the request instance for which route description must be found.
        :returns: the route description
        :raises RestoClientUnsupportedRequest: when the request is not found in this service access.
        """
        routes = self.routes_patterns()[self.protocol]
        try:
            route = routes[type(request).__name__]
        except KeyError:
            msg = '{} request is undefined in route patterns for {} server.'
            raise RestoClientUnsupportedRequest(
                msg.format(type(request).__name__, request.get_server_name()))
        return route

    @property
    def base_url(self) -> str:
        """
        :returns: The current server URL
        """
        return self._base_url

    @base_url.setter
    def base_url(self, base_url: str) -> None:
        """
        Set or Unset (if None given) the server URL field

        :param base_url: the server URL to set
        """
        # Verify that parameter has a valid URL syntax and add a final '/' if necessary
        URLType(base_url, type(self).__name__)
        if urljoin(base_url, ' ')[:-1] != base_url:
            base_url = base_url + '/'
        self._base_url = base_url

    @property
    def protocol(self) -> str:
        """
        :returns: The current service protocol to use
        """
        return self._protocol

    @protocol.setter
    def protocol(self, protocol: str) -> None:
        """
        Set the service protocol field after verifying that it belongs to a list of protocols
        supported by this type of service access

        :param protocol: protocol to set
        :raises RestoClientUserError: when the protocol is unknown.
        """
        if protocol is not None and protocol not in self.supported_protocols():
            msg = '{} protocol is invalid for {}. Should be one of {}.'
            raise RestoClientUserError(msg.format(protocol, type(self),
                                                  ServiceAccess.supported_protocols()))
        self._protocol = protocol

    def __str__(self) -> str:
        result = 'service_type     : {}\n'.format(self.service_type())
        result += 'base_url         : {}\n'.format(self.base_url)
        result += 'protocol         : {}\n'.format(self.protocol)
        return result


class AuthenticationServiceAccess(ServiceAccess):
    """
    Concrete Service Access class used for Authentication services.
    """

    @classmethod
    def service_type(cls) -> str:
        return 'auth'

    @classmethod
    def routes_patterns(cls) -> RoutesPatternsType:
        # Route patterns for an authentication service
        routes_patterns: RoutesPatternsType
        routes_patterns = {
            'default': {
                'GetTokenRequest': {
                    'rel_url': 'api/users/connect',
                    'method': 'get',
                    'accept': 'json',
                    'authentication': 'ALWAYS'},
                'RevokeTokenRequest': {
                    'rel_url': 'api/users/disconnect',
                    'method': 'post',
                    'accept': 'json',
                    'authentication': 'ALWAYS'},
                'CheckTokenRequest': {
                    'rel_url': 'api/users/checkToken?_tk={token}',
                    'method': 'get',
                    'accept': 'json',
                    'authentication': 'NEVER'},
            },
            'sso_theia': {
                'GetTokenRequest': {
                    'rel_url': '',
                    'method': 'post',
                    'accept': 'json',
                    'authentication': 'ALWAYS'},
            },
            'sso_dotcloud': {
                'GetTokenRequest': {
                    'rel_url': '',
                    'method': 'post',
                    'accept': 'json',
                    'authentication': 'ALWAYS'},
            }
        }
        return routes_patterns


class RestoServiceAccess(ServiceAccess):
    """
    Concrete Service Access class used for Resto services.
    """

    @classmethod
    def service_type(cls) -> str:
        return 'resto'

    @classmethod
    def routes_patterns(cls) -> RoutesPatternsType:
        # Route patterns for a resto service
        routes_patterns: RoutesPatternsType
        routes_patterns = {
            'dotcloud': {
                'DescribeRequest': {
                    'rel_url': 'api/collections/describe.json',
                    'method': 'get',
                    'accept': 'json',
                    'authentication': 'NEVER'},
                'GetCollectionsRequest': {
                    'rel_url': 'collections',
                    'method': 'get',
                    'accept': 'json',
                    'authentication': 'NEVER'},
                'GetCollectionRequest': {
                    'rel_url': 'collections/{collection}',
                    'method': 'get',
                    'accept': 'json',
                    'authentication': 'NEVER'},
                'SearchCollectionRequest': {
                    'rel_url': 'api/collections/{collection}/search.json?{criteria_url}',
                    'method': 'get',
                    'accept': 'json',
                    'authentication': 'OPPORTUNITY'},
                'SignLicenseRequest': {
                    'rel_url': 'api/users/{user}/signatures/{license_id}/',
                    'method': 'post',
                    'accept': 'json',
                    'authentication': 'ALWAYS'},
                'DownloadProductRequest': {  # No rel_url as URL in in the feature
                    'method': 'get',
                    'accept': 'json',
                    'authentication': 'ALWAYS'},
                'DownloadQuicklookRequest': {  # No rel_url as URL in in the feature
                    'method': 'get',
                    'accept': 'json',
                    'authentication': 'NEVER'},
                'DownloadThumbnailRequest': {  # No rel_url as URL in in the feature
                    'method': 'get',
                    'accept': 'json',
                    'authentication': 'NEVER'},
                'DownloadAnnexesRequest': {  # No rel_url as URL in in the feature
                    'method': 'get',
                    'accept': 'json',
                    'authentication': 'NEVER'},
            }
        }
        routes_patterns['peps_version'] = copy.deepcopy(routes_patterns['dotcloud'])
        # FIXME: No SignLicenseRequest in peps and theia?
        del routes_patterns['peps_version']['SignLicenseRequest']
        routes_patterns['theia_version'] = copy.deepcopy(routes_patterns['peps_version'])
        return routes_patterns
