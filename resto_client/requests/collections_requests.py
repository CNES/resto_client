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
from typing import TYPE_CHECKING, Optional

from requests import Response

from resto_client.entities.resto_collection import RestoCollection
from resto_client.entities.resto_collections import RestoCollections
from resto_client.entities.resto_criteria import RestoCriteria
from resto_client.responses.collection_description import CollectionDescription
from resto_client.responses.collections_description import CollectionsDescription
from resto_client.responses.feature_collection_response import FeatureCollectionResponse
from resto_client.responses.resto_response_error import RestoResponseError

from .authentication_optional_request import AuthenticationOptionalRequest
from .base_request import RestoRequestResult

if TYPE_CHECKING:
    from resto_client.services.resto_service import RestoService  # @UnusedImport
    from resto_client.responses.resto_response import RestoResponse  # @UnusedImport


class GetCollectionRequest(AuthenticationOptionalRequest):
    """
     Request accessing a single collection
    """

    request_action = 'getting collection'
    authentication_type = 'NEVER'

    def process_request_result(self, request_result: Response) -> RestoCollection:
        collection_response = CollectionDescription(self, request_result.json())
        return collection_response.as_resto_object()


class SearchCollectionRequest(AuthenticationOptionalRequest):
    """
     Request searching a single collection
    """

    request_action = 'searching'

    def __init__(self, service: 'RestoService',
                 collection: str, criteria: Optional[RestoCriteria] = None) -> None:
        """
        Constructor

        :param service: resto service
        :param collection: collection name
        :param criteria: give all criteria for search using a dictionnary
        """
        # initiate request with asking number of total items
        criteria_url = '_rc=true&'
        if criteria is not None:
            for key, value in criteria.items():
                criteria_url += '{}={}&'.format(key, value)
        super(SearchCollectionRequest, self).__init__(service,
                                                      collection=collection,
                                                      criteria_url=criteria_url)

    def run_request(self) -> Response:
        return self.get_response_as_json()

    def process_request_result(self, request_result: Response) -> RestoRequestResult:
        feature_collection_response = FeatureCollectionResponse(self, request_result.json())
        return feature_collection_response.as_resto_object()


class GetCollectionsRequest(AuthenticationOptionalRequest):
    """
     Request retrieving all the service collections
    """

    request_action = 'listing collections'
    authentication_type = 'NEVER'

    def process_request_result(self, request_result: Response) -> RestoCollections:
        try:
            collections_descr = CollectionsDescription(self, request_result.json())
        except RestoResponseError:
            msg = 'URL {} does not point to a valid resto server'
            raise ValueError(msg.format(self.service_access.base_url))

        return collections_descr.as_resto_object()
