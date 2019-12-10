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

from typing import Optional, TYPE_CHECKING  # @UnusedImport

from .service_access import ServiceAccess

if TYPE_CHECKING:
    from resto_client.services.authentication_service import AuthenticationService  # @UnusedImport


class BaseService(ABC):
    """
    An abstract base class for all services
    """

    def __init__(self, service_access: ServiceAccess) -> None:
        """
        Constructor

        :param service_access: Service access.
        :raises RestoClientDesignError: when service_access is not of the right type
        """
        # Initialize from service_access.
        self.service_access = service_access
        self.service_access.set_service(self)

    @property
    @abstractmethod
    def auth_service(self) -> 'AuthenticationService':
        """
        :returns: the authentication service associated to this service.
        """

    @abstractmethod
    def update_after_url_change(self) -> None:
        """
        Callback method to update service after base URL has been changed.
        """

    @abstractmethod
    def reset(self) -> None:
        """
        Reset the service to its creation state, and without any service access defined.
        """
        self.service_access.reset()

    def __str__(self) -> str:
        result = str(self.service_access)
        if self.auth_service is None:
            result += '    associated authentication service : None'
        elif self.auth_service == self:
            result += '    associated authentication service : self'
        else:
            result += '    associated authentication service : {}'.format(self.auth_service)
        return result
