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
from pathlib import Path
from typing import List, Union

from resto_client.entities.resto_feature import RestoFeature
from resto_client.services.resto_server import RestoServer


# TODO: declare optional arguments
def create_features_from_ids(server: RestoServer,
                             collection_name: str,
                             features_ids: Union[str, List[str]]) -> List[RestoFeature]:
    """
    Creates a list of resto features by querying Resto

    :param server: Resto server
    :param collection_name: Name of the collection containing features
    :param features_ids: Feature(s) identifier(s)
    :returns: a list of Resto features
    :raises ValueError: When retrieved feature id is different from requested feature id
    """
    features_list = []
    if not isinstance(features_ids, list):
        features_ids = [features_ids]

    for feature_id in features_ids:
        # TODO: Declare method in RestoServer as proxies
        feature = server.resto_service.get_feature_by_id(feature_id, collection_name)
        features_list.append(feature)

    return features_list

# TODO: declare optional arguments


def download_features_files_from_id(resto_server: RestoServer,
                                    collection: str,
                                    features_ids: Union[str, List[str]],
                                    file: str,
                                    download_dir: Path) -> None:
    """
    Download different file from id(s)

    :param collection: the resto collection name
    :param features_ids: id(s) of the feature(s) which as a file to download
    :param resto_server: the resto server to query
    :param download_dir: the path to the directory where download must be done.
    :param file: file to download product, quicklook, thumbnail or annexes
    :raises ValueError: if the file type is not supported
    :raises ValueError: if the product id is not found in the current collection
    """
    if not isinstance(features_ids, list):
        features_ids = [features_ids]

    # Issue a search request into the collection to retrieve features.
    resto_service = resto_server.resto_service
    features = create_features_from_ids(resto_server, collection, features_ids)

    for feature in features:
        # Do download
        # TODO: Declare method in RestoServer as proxies
        unused_downloaded_filename = resto_service.download_feature_file(feature,
                                                                         file,
                                                                         download_dir)
