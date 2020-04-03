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

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from resto_client.requests.base_request import BaseRequest  # @UnusedImport


class RestoResponse(ABC):
    """
     Base class for all Resto Responses classes.
    """

    def __init__(self, request: 'BaseRequest') -> None:
        """
        Constructor

        :param request: the parent request of this response
        """
        self._parent_request = request

    @property
    def request_name(self) -> str:
        """
        :returns: the parent request class name
        """
        return type(self._parent_request).__name__

    @abstractmethod
    def as_resto_object(self) -> Any:
        """
        :returns: the response expressed as a Resto object
        """

    @property
    def detected_protocol(self) -> Optional[str]:
        """
        :returns: the protocol of this response
        """
        return self._parent_request.parent_service.service_access.detected_protocol

    @detected_protocol.setter
    def detected_protocol(self, protocol: Optional[str]) -> None:
        self._parent_request.parent_service.service_access.detected_protocol = protocol
