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
from typing import TYPE_CHECKING, Optional, cast  # @NoMove

from resto_client.entities.resto_collection import RestoCollection
from resto_client.entities.resto_collections import RestoCollections
from resto_client.entities.resto_criteria import RestoCriteria
from resto_client.entities.resto_feature_collection import RestoFeatureCollection
from resto_client.responses.collection_description import CollectionDescription
from resto_client.responses.collections_description import CollectionsDescription
from resto_client.responses.feature_collection_response import FeatureCollectionResponse

from .resto_json_request import RestoJsonRequest


if TYPE_CHECKING:
    from resto_client.services.resto_service import RestoService  # @UnusedImport


class GetCollectionRequest(RestoJsonRequest):
    """
     Request accessing a single collection
    """

    request_action = 'getting collection'
    resto_response_cls = CollectionDescription

    def run(self) -> RestoCollection:
        # overidding BaseRequest method, in order to specify the right type returned by this request
        return cast(RestoCollection, super(GetCollectionRequest, self).run())


class SearchCollectionRequest(RestoJsonRequest):
    """
     Request searching a single collection
    """

    request_action = 'searching'
    resto_response_cls = FeatureCollectionResponse

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
        # TODO: move as a method of RestoCriteria?
        if criteria is not None:
            for key, value in criteria.items():
                criteria_url += '{}={}&'.format(key, value)
        super(SearchCollectionRequest, self).__init__(service,
                                                      collection=collection,
                                                      criteria_url=criteria_url)

    def run(self) -> RestoFeatureCollection:
        # overidding BaseRequest method, in order to specify the right type returned by this request
        return cast(RestoFeatureCollection, super(SearchCollectionRequest, self).run())


class GetCollectionsRequest(RestoJsonRequest):
    """
     Request retrieving all the service collections
    """

    request_action = 'listing collections'

    # TODO: parameterize duration into request description.
    caching_max_seconds = 10
    resto_response_cls = CollectionsDescription

    def run(self) -> RestoCollections:
        # overidding BaseRequest method, in order to specify the right type returned by this request
        return cast(RestoCollections, super(GetCollectionsRequest, self).run())
