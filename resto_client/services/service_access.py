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
from typing import List, Dict, Union, TypeVar, Type, Optional, TYPE_CHECKING
from urllib.parse import urljoin

from resto_client.base_exceptions import RestoClientUserError, RestoClientDesignError
from resto_client.functions.utils import is_valid_url
from resto_client.generic.property_decoration import managed_getter, managed_setter

from resto_client.settings.resto_client_settings import RESTO_CLIENT_SETTINGS

if TYPE_CHECKING:
    from resto_client.services.base_service import BaseService  # @UnusedImport
    from resto_client.requests.base_request import BaseRequest  # @UnusedImport

SA = TypeVar('SA', bound='ServiceAccess')

RoutesPatternsType = Dict[str, Dict[str, Union[str, None]]]
"""
Routes patterns for a service are described in a dictionary whose key is the service protocol
and the value is another dictionary. This second dictionary has the request class name as its key,
and the route itself as the value. This route can be None in case it is not defined for some
protocol.
"""


class RestoClientNoPersistedAccess(RestoClientUserError):
    """ Exception raised when no persisted access found for the service """


class ServiceAccess(ABC):
    """
    Abstract class holding the 2 parameters defining a service access: its URL and its protocol.

    Concrete class must define the protocols they support.
    """
    properties_storage = RESTO_CLIENT_SETTINGS

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

    @classmethod
    def url_key(cls) -> str:
        """
        :returns: the key to use for url persistence for this service
        """
        return '{}_base_url'.format(cls.service_type())

    @classmethod
    def protocol_key(cls) -> str:
        """
        :returns: the key to use for protocol persistence for this service
        """
        return '{}_protocol'.format(cls.service_type())

    @classmethod
    def persisted(cls: Type[SA]) -> SA:
        """

        :returns: the persisted access for this service
        :raises RestoClientNoPersistedAccess: when no persisted attributes exist for this service
        """
        persisted_url = cls.properties_storage.get(cls.url_key())
        persisted_protocol = cls.properties_storage.get(cls.protocol_key())
        if persisted_url is None or persisted_protocol is None:
            msg = 'No server currently set in the persisted parameters.'
            raise RestoClientNoPersistedAccess(msg)
        return cls(persisted_url, persisted_protocol)

    def __init__(self,
                 service_url: str,
                 service_protocol: str) -> None:
        """
        Constructor.

        :param service_url: the URL at which the service is available.
        :param service_protocol: the protocol implemented by the service.
        """
        self.properties_name_prefix = self.service_type()

        self._parent_service = None

        service_url = self.check_url(service_url, type(self).__name__)
        service_protocol = self._check_protocol(service_protocol)
        self.detected_protocol: Optional[str] = None

        self.base_url = service_url  # type: ignore
        self.protocol = service_protocol  # type: ignore

    def set_service(self, parent_service: 'BaseService') -> None:
        """

        :param parent_service: the service using this service access.
        """
        self._parent_service = parent_service

    def reset(self) -> None:
        """
        Reset the service access to None.
        """
        self.protocol = None  # type: ignore
        self.base_url = None  # type: ignore

    def get_route_pattern(self, request: 'BaseRequest') -> Optional[str]:
        """
        Returns the route pattern for a request

        :param request: the request instance for which route must be found.
        :returns: the route pattern
        """
        routes = self.routes_patterns()[self.protocol]
        return routes[type(request).__name__]

    @staticmethod
    def check_url(base_url: str, service_name: str) -> str:
        """
        Test that URL has a valid syntax and normalize it with a final '/' if not present,
        in order to get right urljoin() results.

        :param base_url: the base url of the service
        :param service_name: the name of the service to report in exception messages.
        :returns: an URL with a final '/' if not present
        :raises RestoClientDesignError: when the URL is invalid.
        """
        if not is_valid_url(base_url):
            msg = 'url for {} is not a valid URL: {}.'
            raise RestoClientDesignError(msg.format(service_name, base_url))
        if urljoin(base_url, ' ')[:-1] != base_url:
            base_url = base_url + '/'
        return base_url

    @property  # type: ignore
    @managed_getter()
    def base_url(self) -> Optional[str]:
        """
        :returns: The current server URL
        """

    @base_url.setter  # type: ignore
    @managed_setter(pre_set_func='_check_url')
    def base_url(self, base_url: str) -> None:
        """
        Set or Unset (if None given) the server URL field

        :param base_url: the server URL to set
        """
        # Following code is called by managed_setter if and only if base_url has changed.
        # At that time, the property has been updated and can be gotten through the getter.
        _ = base_url
        if self._parent_service is not None:
            self._parent_service.update_after_url_change()

    def _check_url(self, base_url: str) -> str:
        """
        Test that URL has a valid syntax and normalize it with a final '/' if not present,
        in order to get right urljoin() results.

        :param base_url: the base url of the service
        :returns: an URL with a final '/' if not present
        :raises RestoClientDesignError: when the URL is invalid.
        """
        return ServiceAccess.check_url(base_url, type(self).__name__)

    @property  # type: ignore
    @managed_getter()
    def protocol(self) -> Optional[str]:
        """
        :returns: The current service protocol to use
        """

    @protocol.setter  # type: ignore
    @managed_setter(pre_set_func='_check_protocol')
    def protocol(self, protocol: Optional[str]) -> None:
        """
        Set or Unset (if None given) the service protocol field

        :param protocol: protocol to set
        """

    @classmethod
    def _check_protocol(cls, protocol: str) -> str:
        """
        Verify that protocol belongs to a list of protocols supported by this type of service
        access.

        :param protocol: the protocol name
        :raises RestoClientUserError: when the protocol is unknown.
        :returns: the service protocol
        """
        if protocol not in cls.supported_protocols():
            msg = '{} protocol is invalid for {}. Should be one of {}.'
            raise RestoClientUserError(msg.format(protocol, cls.__name__,
                                                  cls.supported_protocols()))
        return protocol

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
