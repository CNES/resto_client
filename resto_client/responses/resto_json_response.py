# -*- coding: utf-8 -*-
"""
.. admonition:: License

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
from typing import Dict, List, Any, Optional, TYPE_CHECKING  # @UnusedImport
import warnings

from resto_client.base_exceptions import InvalidResponse

from .resto_response import RestoResponse


if TYPE_CHECKING:
    from resto_client.requests.base_request import BaseRequest  # @UnusedImport


class RestoJsonResponse(RestoResponse):
    """
     Abstract base class for responses received in Json format.
    """

    def __init__(self, request: 'BaseRequest', response: dict) -> None:
        """
        :param request: the parent request of this response
        :param response: the response received from the server and structured as a dict.
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

        :raises InvalidResponse: if the dictionary does not contain a valid Resto response.
        """

    def normalize_response(self) -> None:
        """
        Returns a normalized response whose structure does not depend on the server.

        This method should be overidden by client classes. Default is to copy the original response.
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

    @property
    @abstractmethod
    def optional_fields(self) -> List[str]:
        """
        :returns: the field names that the response contains optionally
        """

    def identify_response(self) -> None:
        """
        Verify that the response is a valid resto response for this class.

        :raises InvalidResponse: if the dictionary does not contain a valid Resto response.
        """
        # First verify that all needed fields are present. Raise an exception when some are missing
        for field in self.needed_fields:
            if field not in self._original_response:
                msg = 'Response to {} does not contain a "{}" field. Available fields: {}'
                raise InvalidResponse(msg.format(self.request_name, field,
                                                 self._original_response.keys()))

        # Then check that no other entries than those defined as needed or optional
        # are contained in the response. Issue a warning if not when in debug mode.
        response = copy.deepcopy(self._original_response)
        for field in self.needed_fields:
            response.pop(field)
        for field in self.optional_fields:
            response.pop(field, None)
        if response.keys() and self._parent_request.debug:  # type: ignore
            msg = '{} response contains unknown entries: {}.'
            warnings.warn(msg.format(self.request_name, response))
