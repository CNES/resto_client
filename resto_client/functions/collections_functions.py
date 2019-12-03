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
from typing import Optional, Dict, Any

from resto_client.entities.resto_feature_collection import RestoFeatureCollection
from resto_client.services.resto_service import RestoService

from .resto_criteria import RestoCriteria


def search_collection(resto_service: RestoService,
                      collection_name: str,
                      region: str,
                      criteria: Optional[Dict[str, Any]]=None) -> Optional[RestoFeatureCollection]:
    """
    Search in a collection using selection criteria

    :param collection_name: name of the resto collection; iF None search all collections
    :param resto_service: the resto service to query
    :param region: the name of the region to use
    :param criteria: list of criterion for search
    :returns: the collection of retrieved features
    """
    new_criteria = RestoCriteria(resto_service.service_access.protocol)
    if criteria is not None:
        new_criteria.update(criteria)
    new_criteria.update({'region': region})

    search_feature_collection = resto_service.search_collection(new_criteria, collection_name)
    if len(search_feature_collection.all_id) == 1:
        search_result = search_feature_collection.features[0]
    elif not search_feature_collection.all_id:
        search_result = None
    else:
        search_result = search_feature_collection
    return search_result
