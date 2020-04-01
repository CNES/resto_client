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
import copy
from typing import Optional

from resto_client.base_exceptions import (InconsistentResponse,
                                          IncomprehensibleResponse)
from resto_client.entities.resto_collection import RestoCollection
from resto_client.entities.resto_collections import RestoCollections

from .resto_json_response import RestoJsonResponse


OSDESCRIPTION_KEYS = ['ShortName', 'LongName', 'Description'
                      'Tags', 'Developer', 'Contact', 'Query', 'Attribution']


def rebuild_os_description(opensearch_description: dict) -> Optional[dict]:
    """
    Rebuild a normalized osDescription from an existing one or create a sensible one.

    If osDescription is multi-lingual, retain only one language, preferably english

    :param opensearch_description: the osDescription field to process
    :returns: osDescription english fields
    """
    normalized_osdescription = None
    if isinstance(opensearch_description, dict):
        if any([os_key in opensearch_description for os_key in OSDESCRIPTION_KEYS]):
            normalized_osdescription = copy.deepcopy(opensearch_description)
        elif 'en' in opensearch_description:
            normalized_osdescription = copy.deepcopy(opensearch_description['en'])
        elif 'fr' in opensearch_description:
            normalized_osdescription = copy.deepcopy(opensearch_description['fr'])

    return normalized_osdescription


def counting_stats(response_stat_collection: dict) -> int:
    """
    Count a correct total of features in all collections

    :param response_stat_collection: the collection field'd in response's statistics
    :returns: count of all features
    """
    count = 0
    for stat_collection in response_stat_collection.values():
        count += stat_collection
    return count


class CollectionsDescription(RestoJsonResponse):
    """
     Response received from DescribeRequest and GetCollectionsRequest.
    """

    def identify_response(self) -> None:
        """
        Verify that the response is a valid resto response for this class and set the resto type

        :raises InconsistentResponse: if the dictionary does not contain a valid Resto response.
        """
        detected_protocol = None
        # Find which kind of Resto server we could have
        if 'collections' in self._original_response:
            if 'statistics' in self._original_response:
                statistics_desc = self._original_response['statistics']
                if 'facets' in statistics_desc and 'count' in statistics_desc:
                    detected_protocol = 'peps_version'
                else:
                    detected_protocol = 'dotcloud'
            elif 'synthesis' in self._original_response:
                if 'statistics' in self._original_response['synthesis']:
                    statistics_desc = self._original_response['synthesis']['statistics']
                    if 'facets' in statistics_desc and 'count' in statistics_desc:
                        detected_protocol = 'theia_version'

        self.detected_protocol = detected_protocol
        if detected_protocol is None:
            raise IncomprehensibleResponse('Dictionary does not contain a valid Resto response')
        if self._parent_request.get_protocol() != detected_protocol:
            msg_fmt = 'Detected a {} response while waiting for a {} response.'
            msg = msg_fmt.format(detected_protocol, self._parent_request.get_protocol())
            raise InconsistentResponse(msg)

    def normalize_response(self) -> None:
        """
        Normalize the original response in a response whose structure does not depend on the server.
        """
        result = None
        if self.detected_protocol == 'theia_version':
            result = copy.deepcopy(self._original_response)
        elif self.detected_protocol == 'peps_version':
            result = {'collections': self._original_response['collections'],
                      'synthesis': {'name': '*',
                                    'osDescription': None,
                                    'statistics': self._original_response['statistics']}
                      }
        else:
            result = {'collections': self._original_response['collections'],
                      'synthesis': {'name': '*',
                                    'osDescription': None,
                                    'statistics': {'count': 0,
                                                   'facets': self._original_response['statistics']}}
                      }
        # Update synthesis fields
        # Correct synthesis statistics count
        count = 0
        if 'collection' in result['synthesis']['statistics']['facets']:
            count = counting_stats(result['synthesis']['statistics']['facets']['collection'])
        result['synthesis']['statistics']['count'] = count
        # rebuild an osDescription for synthesis
        os_description = rebuild_os_description(result['synthesis']['osDescription'])
        result['synthesis']['osDescription'] = os_description

        # rebuild osDescription for each collection
        for collection in result['collections']:
            collection['osDescription'] = rebuild_os_description(collection['osDescription'])

        self._normalized_response = result

    def as_resto_object(self) -> RestoCollections:
        """
        :returns: the received set of collections
        """
        synthesis = RestoCollection(self._normalized_response['synthesis'])
        collections = RestoCollections()
        collections.synthesis = synthesis

        for collection_desc in self._normalized_response['collections']:
            collections.add(RestoCollection(collection_desc))

        return collections
