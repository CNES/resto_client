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

from .authentication_service import AuthenticationService
from .base_service import BaseService
from .service_access import ServiceAccess


class ApplicationService(BaseService):
    """
    An abstract base class for all application services which need an authentication service
    """

    def __init__(self,
                 service_access: ServiceAccess,
                 auth_service: AuthenticationService) -> None:
        """
        Constructor

        :param service_access: access to application service.
        :param auth_service: access to the Authentication service associated to this application
                             service.
        """
        super(ApplicationService, self).__init__(service_access=service_access)
        self.auth_service = auth_service

    @abstractmethod
    def update_after_url_change(self) -> None:
        """
        Callback method to update service after base URL has been changed.
        """
        super(ApplicationService, self).update_after_url_change()

    @abstractmethod
    def reset(self) -> None:
        """
        Reset the service to its creation state, and without any service access defined.
        """
        super(ApplicationService, self).reset()
        self.auth_service.reset()

    def __str__(self) -> str:
        result = super(ApplicationService, self).__str__()
        if self.auth_service == self:
            result += '    associated authentication service : self'
        else:
            result += '    associated authentication service : {}'.format(self.auth_service)
        return result
