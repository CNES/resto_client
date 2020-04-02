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

import json
from pathlib import Path

import geojson
from prettytable import PrettyTable

from .resto_feature import RestoFeature


class RestoFeatureCollection(geojson.FeatureCollection):
    """
     Class representing a Resto feature collection.
    """

    def __init__(self, feature_coll_descr: dict) -> None:
        """
        Constructor

        :param feature_coll_descr: Feature collection description
        :raises TypeError: When type in descriptor is different from 'FeatureCollection'
        """
        if feature_coll_descr['type'] != 'FeatureCollection':
            msg = 'Cannot create a feature collection whose type is not FeatureCollection'
            raise TypeError(msg)

        self.resto_features = [RestoFeature(desc) for desc in feature_coll_descr['features']]
        super(RestoFeatureCollection, self).__init__(properties=feature_coll_descr['properties'],
                                                     features=self.resto_features)

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
        :returns: the identifiers of all features in this feature collection
        """
        return [feature.product_identifier for feature in self.features]

    def get_feature(self, feature_id: str) -> RestoFeature:
        """
        Get the feature from this features collection with the requested id

        :param feature_id: identifier of the feature to retrieve
        :returns: a resto feature
        :raises KeyError: when no feature with the specified identifier can be found.
        """
        result = [feat for feat in self.resto_features if feat.product_identifier == feature_id]
        if len(result) != 1:
            raise KeyError(f'No feature found with id: {feature_id}')
        return result[0]

    def write_json(self, dir_path: Path) -> Path:
        """
        Save the current entity in a json file
        :param dir_path: Path where to write the json
        :returns: Path of the saved json file
        """
        json_name = 'request_{}.json'.format(self.identifier)
        with open(dir_path / json_name, 'w') as stream:
            json.dump(self, stream, indent=2)
        return dir_path / json_name

    def __str__(self) -> str:

        if self.properties is not None:
            result = '\nProperties available for the FeatureCollection\n'
            feat_table = PrettyTable()
            feat_table.field_names = ['Property', 'Value']
            feat_table.align['Value'] = 'l'
            feat_table.align['Property'] = 'l'

            for product_property in self.properties:
                show_param = str(self.properties[product_property])
                feat_table.add_row([product_property, show_param])

            feat_table.add_row(["all_id", str(self.all_id)])
            result += feat_table.get_string()
            result += '\n'
        return result
