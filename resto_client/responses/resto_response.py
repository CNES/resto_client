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

from typing import Any

from resto_client.requests.base_request import BaseRequest


class RestoResponse(ABC):
    """
     Base class for all Resto Responses classes.
    """

    def __init__(self, request: BaseRequest) -> None:
        """
        Constructor

        :param request: the parent request of this response
        :raises TypeError: if the first argument is not of the right type (BaseRequest)
        """
        if not issubclass(type(request), BaseRequest):
            msg_err = 'request argument type must derive from: {}. Found a {} type which is not.'
            base_type_name = BaseRequest.__name__  # @UndefinedVariable
            raise TypeError(msg_err.format(base_type_name, type(request).__name__))
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
