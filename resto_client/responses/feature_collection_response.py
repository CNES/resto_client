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
from typing import List  # @UnusedImport

from resto_client.base_exceptions import InconsistentResponse, InvalidResponse
from resto_client.entities.resto_feature_collection import RestoFeatureCollection

from .resto_json_response import RestoJsonResponseSimple


class FeatureCollectionResponse(RestoJsonResponseSimple):
    """
     Response received from SearchCollectionRequest.
    """

    needed_fields = ['type', 'features', 'properties']
    optional_fields: List[str] = []

    def identify_response(self) -> None:
        """
        Verify that the response is a valid FeatureCollection geojson object.

        :raises InconsistentResponse: if the dictionary does not contain a valid Resto response.
        :raises InvalidResponse: if fields are not as expected.

        """
        # Firstly verify that the needed fields are present
        super(FeatureCollectionResponse, self).identify_response()

        # Secondly verify geojson constraints on these fields, (not verified by geojson package)
        if self._original_response['type'] != 'FeatureCollection':
            msg = 'Waited a FeatureCollection geojson response. Received a {} response instead.'
            raise InconsistentResponse(msg.format(self._original_response['type']))
        if not isinstance(self._original_response['features'], list):
            msg = 'features field in a FeatureCollection must be a list. Found a {} instead.'
            raise InvalidResponse(msg.format((self._original_response['features'])))
        if not isinstance(self._original_response['properties'], dict):
            msg = 'properties field in a FeatureCollection must be a dict. Found a {} instead.'
            raise InvalidResponse(msg.format((self._original_response['properties'])))

    def as_resto_object(self) -> RestoFeatureCollection:
        """
        :returns: the response expressed as a :class:`RestoFeatureCollection` object
        """
        return RestoFeatureCollection(self._normalized_response)
