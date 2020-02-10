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

RoutesPatternsType = Dict[str, Dict[str, Union[str, None]]]
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
        :raises RestoClientUnsupportedRequest: when the request has no associated route in this
                                               service access.
        """
        routes = self.routes_patterns()[self.protocol]
        try:
            route = routes[type(request).__name__]
        except KeyError:
            msg = '{} request is undefined in route patterns for {} server.'
            raise RestoClientUnsupportedRequest(
                msg.format(type(request).__name__, request.get_server_name()))
        if route is None:
            msg = '{} request is declared as None in route patterns for {} server.'
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
        routes_patterns = {'default': {'GetTokenRequest': 'api/users/connect',
                                       'RevokeTokenRequest': 'api/users/disconnect',
                                       'CheckTokenRequest': 'api/users/checkToken?_tk={token}'
                                       },
                           'sso_theia': {'GetTokenRequest': '',
                                         'RevokeTokenRequest': None,
                                         'CheckTokenRequest': None
                                         },
                           'sso_dotcloud': {'GetTokenRequest': '',
                                            'RevokeTokenRequest': None,
                                            'CheckTokenRequest': None
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
        routes_patterns = {'dotcloud': {'DescribeRequest': 'api/collections/describe.json',
                                        'GetCollectionsRequest': 'collections',
                                        'GetCollectionRequest': 'collections/{collection}',
                                        'SearchCollectionRequest':
                                        'api/collections/{collection}/search.json?{criteria_url}',
                                        'GetFeatureByIDRequest':
                                        'api/collections/{collection}/search.json?{criteria_url}',
                                        'SignLicenseRequest':
                                        'api/users/{user}/signatures/{license_id}/'
                                        }
                           }
        routes_patterns['peps_version'] = copy.deepcopy(routes_patterns['dotcloud'])
        routes_patterns['peps_version']['SignLicenseRequest'] = None
        routes_patterns['theia_version'] = copy.deepcopy(routes_patterns['peps_version'])
        return routes_patterns
