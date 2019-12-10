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
from resto_client.entities.resto_collection import RestoCollection

from .collections_description import rebuild_os_description
from .resto_json_response import RestoJsonResponseSimple


class CollectionDescription(RestoJsonResponseSimple):
    """
     Response received from GetCollectionRequest.
    """

    needed_fields = ['license', 'model', 'name', 'osDescription', 'statistics', 'status']
    optional_fields = ['owner']

    def normalize_response(self) -> None:
        """
        Normalize the original response in a response whose structure does not depend on the server.
        """
        super(CollectionDescription, self).normalize_response()
        # Add a owner field if not present
        if 'owner' not in self._normalized_response:
            self._normalized_response['owner'] = None
        normalized_osdescr = self._normalized_response['osDescription']
        self._normalized_response['osDescription'] = rebuild_os_description(normalized_osdescr)

    def as_resto_object(self) -> RestoCollection:
        """
        :returns: the received resto collection
        """
        return RestoCollection(self._normalized_response)
