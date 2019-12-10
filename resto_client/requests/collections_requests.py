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
from typing import TYPE_CHECKING, cast

from resto_client.entities.resto_collection import RestoCollection
from resto_client.entities.resto_collections import RestoCollections
from resto_client.entities.resto_feature_collection import RestoFeatureCollection
from resto_client.functions.resto_criteria import RestoCriteria
from resto_client.responses.collection_description import CollectionDescription
from resto_client.responses.collections_description import CollectionsDescription
from resto_client.responses.feature_collection_response import FeatureCollectionResponse
from resto_client.responses.resto_response_error import RestoResponseError

from .anonymous_request import AnonymousRequest
from .authentication_optional_request import AuthenticationOptionalRequest

if TYPE_CHECKING:
    from resto_client.services.resto_service import RestoService  # @UnusedImport


class GetCollectionRequest(AnonymousRequest):
    """
     Request accessing a single collection
    """

    request_action = 'getting collection'

    def run(self) -> RestoCollection:
        """
         Execute the request to list a collection

        :returns: collection descriptor
        :raises ValueError: when no collection is currently defined
        """
        self.set_headers()
        json_response = cast(dict, self.get_as_json())
        collection_response = CollectionDescription(self, json_response)
        return collection_response.as_resto_object()


class SearchCollectionRequest(AuthenticationOptionalRequest):
    """
     Request searching a single collection
    """

    request_action = 'searching'

    def __init__(self, service: 'RestoService',
                 criteria: RestoCriteria, collection: str) -> None:
        """
        Constructor

        :param service: resto service
        :param criteria: give all criteria for search using a dictionnary
        :param collection: collection name
        :raises ValueError: When no collection can be found (given or persisted)
        """
        # initiate request with asking number of total items
        criteria_url = '_rc=true&'
        if criteria is not None:
            for key, value in criteria.items():
                criteria_url += '{}={}&'.format(key, value)
        super(SearchCollectionRequest, self).__init__(service,
                                                      collection=collection,
                                                      criteria_url=criteria_url)

    def run(self) -> RestoFeatureCollection:
        """
        Launch a search for given parameters in a collection

        :returns: the result of the search
        """

        self.set_headers()
        json_response = cast(dict, self.get_as_json())
        feature_collection_response = FeatureCollectionResponse(self, json_response)
        return feature_collection_response.as_resto_object()


class GetCollectionsRequest(AnonymousRequest):
    """
     Request retrieving all the service collections
    """

    request_action = 'listing collections'

    def run(self) -> RestoCollections:
        """
         Execute the request to list all collections

        :returns: the set of collections as well as the server synthesis
        :raises ValueError: when the service  URL does not point to a valid Resto server
        """
        self.set_headers()
        json_response = cast(dict, self.get_as_json())
        try:
            collections_descr = CollectionsDescription(self, json_response)
        except RestoResponseError:
            msg = 'URL {} does not point to a valid resto server'
            raise ValueError(msg.format(self.service_access.base_url))

        return collections_descr.as_resto_object()
