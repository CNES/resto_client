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
from typing import Optional  # @NoMove
from pathlib import Path
import requests
from tqdm import tqdm

from resto_client.settings.resto_client_config import resto_client_print


# TODO: move as part of process_request_result
def download_file(requ_result: requests.Response,
                  file_path: Path,
                  file_size: Optional[int]=None) -> None:
    """
    method called when we know that we have a file to download
    iterate a result created with GET with stream option and write it directly in a file
    """
    # Get and Save the result's size if not given
    if file_size is None:
        file_size = int(requ_result.headers.get('content-length', 0))

    block_size = 1024

    resto_client_print('downloading file: {}'.format(file_path))

    with open(file_path, 'wb') as file_desc:
        # do iteration with progress bar using tqdm
        progress_bar = tqdm(unit="B", total=file_size, unit_scale=True, desc='Downloading')
        for block in requ_result.iter_content(block_size):
            progress_bar.update(len(block))
            file_desc.write(block)
