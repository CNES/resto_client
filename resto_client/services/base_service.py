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
from typing import TYPE_CHECKING, cast

from .service_access import ServiceAccess


if TYPE_CHECKING:
    from .authentication_service import AuthenticationService  # @UnusedImport


class BaseService(ABC):
    """
    An abstract base class for all services
    """

    def __init__(self, service_access: ServiceAccess, parent_server: str) -> None:
        """
        Constructor

        :param service_access: Service access.
        :param parent_server: Name of the server which uses this service.
        :raises RestoClientDesignError: when service_access is not of the right type
        """
        self.service_access = service_access
        self._auth_service = self
        self.parent_server_name = parent_server

    @abstractmethod
    def update_after_url_change(self) -> None:
        """
        Callback method to update service after base URL has been changed.
        """

    @property
    def auth_service(self) -> 'AuthenticationService':
        """
        :returns: the authentication service associated to this application service.
        """
        return cast('AuthenticationService', self._auth_service)

    @auth_service.setter
    def auth_service(self, auth_service: 'AuthenticationService') -> None:
        self._auth_service = auth_service

    def __str__(self) -> str:
        return str(self.service_access)
