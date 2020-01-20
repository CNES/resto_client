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

from resto_client.services.resto_server import RestoServer


# TODO: move as a method of RestoServer ?
def download_features_files_from_id(resto_server: RestoServer,
                                    features_ids: Union[str, List[str]],
                                    file_type: str,
                                    download_dir: Path) -> List[str]:
    """
    Download different file from id(s)

    :param features_ids: id(s) of the feature(s) which as a file to download
    :param resto_server: the resto server to query
    :param download_dir: the path to the directory where download must be done.
    :param file_type: type of file to download: product, quicklook, thumbnail or annexes
    """
    if not isinstance(features_ids, list):
        features_ids = [features_ids]

    # Issue a search request into the collection to retrieve features.
    features = resto_server.get_features_from_ids(features_ids)

    downloaded_filenames: List[str] = []
    for feature in features:
        # Do download
        downloaded_filename = resto_server.download_feature_file(feature, file_type, download_dir)
        if downloaded_filename is not None:
            downloaded_filenames.append(downloaded_filename)
    return downloaded_filenames
