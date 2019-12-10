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
import copy
from typing import Dict, List, Any, Optional  # @UnusedImport
import warnings

from resto_client.requests.base_request import BaseRequest
from resto_client.settings.resto_client_parameters import RestoClientParameters

from .resto_response import RestoResponse
from .resto_response_error import RestoResponseError


class RestoJsonResponse(RestoResponse):
    """
     Json responses received from Resto.
    """

    def __init__(self, request: BaseRequest, response: dict) -> None:
        """
        Constructor

        :param request: the parent request of this response
        :param response: the response received from the server and structured as a dict.
        :raises RestoResponseError: if the dictionary does not contain a valid Resto response.
        """
        super(RestoJsonResponse, self).__init__(request)

        self._original_response = response
        self._normalized_response: Dict[Any, Any] = {}

        self.identify_response()
        self.normalize_response()

    @abstractmethod
    def identify_response(self) -> None:
        """
        Verify that the response is a valid resto response for this class.

        :raises RestoResponseError: if the dictionary does not contain a valid Resto response.
        """

    def normalize_response(self) -> None:
        """
        Returns a normalized response whose structure does not depend on the server.
        """
        self._normalized_response = copy.deepcopy(self._original_response)

    @abstractmethod
    def as_resto_object(self) -> Any:
        """
        :returns: the response expressed as a Resto object
        """


class RestoJsonResponseSimple(RestoJsonResponse):
    """
     Simple responses received from Resto, containing only 'flat' fields.
    """

    @property
    @abstractmethod
    def needed_fields(self) -> List[str]:
        """
        :returns: the field names that the response must contain
        """

    def identify_response(self) -> None:
        """
        Verify that the response is a valid resto response for this class.

        :raises RestoResponseError: if the dictionary does not contain a valid Resto response.
        """
        for field in self.needed_fields:
            if field not in self._original_response:
                msg = 'Response to {} does not contain a {} field. Available fields: {}'
                raise RestoResponseError(msg.format(self.request_name, field,
                                                    self._original_response.keys()))

        response = copy.deepcopy(self._original_response)
        # Check that no other entries are contained in the response. Issue a warning if not.
        for field in self.needed_fields:
            response.pop(field)
        if response.keys() and RestoClientParameters.is_debug():
            msg = '{} response contains unknown entries: {}.'
            warnings.warn(msg.format(self.request_name, response))
