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
from abc import ABC
from typing import TYPE_CHECKING, Optional  # @UnusedImport

from .service_access import ServiceAccess


if TYPE_CHECKING:
    from .authentication_service import AuthenticationService  # @UnusedImport
    from .resto_server import RestoServer  # @UnusedImport


class BaseService(ABC):
    """
    An abstract base class for all services
    """

    def __init__(self,
                 service_access: ServiceAccess,
                 auth_service: 'AuthenticationService',
                 parent_server: 'RestoServer') -> None:
        """
        Constructor

        :param service_access: Service access.
        :param auth_service: Authentication service associated to this service.
        :param parent_server: The server which uses this service.
        :raises RestoClientDesignError: when service_access is not of the right type
        """
        self.service_access = service_access
        self._auth_service = auth_service
        self.parent_server = parent_server

    @property
    def auth_service(self) -> 'AuthenticationService':
        """
        :returns: the authentication service associated to this application service.
        """
        return self._auth_service

    @auth_service.setter
    def auth_service(self, auth_service: 'AuthenticationService') -> None:
        self._auth_service = auth_service

    def __str__(self) -> str:
        result = str(self.service_access)
        if self.auth_service == self:
            result += '    associated authentication service : self'
        else:
            result += '    associated authentication service : {}'.format(self.auth_service)
        return result

    def get_base_url(self) -> str:
        """
        :returns: the base URL of the service.
        """
        return self.service_access.base_url

    def get_protocol(self) -> str:
        """
        :returns: the protocol of the service.
        """
        return self.service_access.protocol
