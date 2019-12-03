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
from typing import List, Optional  # @NoMove

import geojson

from .resto_feature import RestoFeature


class RestoFeatureCollection(geojson.FeatureCollection):
    """
     Class representing a Resto feature collection.
    """

    def __init__(self, feature_coll_descr: dict) -> None:
        """
        Constructor

        :param feature_coll_descr: Feature collection description
        :raises ValueError: When type in descriptor is different from 'FeatureCollection'
        """
        if feature_coll_descr['type'] != 'FeatureCollection':
            msg = 'Cannot create a feature collection whose type is not FeatureCollection'
            raise ValueError(msg)

        resto_features = [RestoFeature(desc) for desc in feature_coll_descr['features']]
        super(RestoFeatureCollection, self).__init__(properties=feature_coll_descr['properties'],
                                                     features=resto_features)

    @property
    def identifier(self) -> str:
        """
        :returns: the feature collection's unique id
        """
        return self.properties['id']

    @property
    def query(self) -> str:
        """
        :returns: the query which created this feature collection
        """
        return self.properties['query']

    @property
    def total_results(self) -> Optional[int]:
        """
        :returns: the total number of results corresponding to the query (but not to this Feature
                  Collection)
        """
        return self.properties['totalResults']

    @property
    def start_index(self) -> int:
        """
        :returns: the index of the first feature in this feature collection within the whole query
                  result.
        """
        return self.properties['startIndex']

    @property
    def all_id(self) -> List[str]:
        """
        :returns: the identifiers of all feature in this feature collection
        """
        return [feature.product_identifier for feature in self.features]
