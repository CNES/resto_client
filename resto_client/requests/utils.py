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
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError, SSLError
from tqdm import tqdm

from resto_client.base_exceptions import RestoClientUserError


class AccesDeniedError(RestoClientUserError):
    """
    Exception corresponding to HTTP Error 403
    """


class RestrictedProductError(RestoClientUserError):
    """
    Exception used when a product exist but cannot be downloaded
    """


def get_response(url: str,
                 req_type: str,
                 headers: Optional[dict]=None,
                 auth: Optional[HTTPBasicAuth]=None,
                 stream: bool=False) -> requests.Response:
    """
     This create and execute a GET request and return the response content
    """
    result = None
    try:
        result = requests.get(url, headers=headers, auth=auth, stream=stream)
        result.raise_for_status()

    except (HTTPError, SSLError) as excp:
        if result is not None:
            msg = 'Error {} when {} for {}.'.format(result.status_code, req_type, url)
            if result.status_code == 403:
                raise AccesDeniedError(msg) from excp
        else:
            msg = 'Error when {} for {}.'.format(req_type, url)
        raise Exception(msg) from excp
    return result


def download_file(requ_result: requests.Response,
                  full_file_name: Path,
                  file_size: Optional[int]=None) -> None:
    """
    method called when we know that we have a file to download
    iterate a result created with GET with stream option and write it directly in a file
    """
    # Get and Save the result's size if not given
    if file_size is None:
        file_size = int(requ_result.headers.get('content-length', 0))

    block_size = 1024

    print('downloading file: {}'.format(full_file_name))

    with open(full_file_name, 'wb') as file_desc:
        # do iteration with progress bar using tqdm
        progress_bar = tqdm(unit="B", total=file_size, unit_scale=True, desc='Downloading')
        for block in requ_result.iter_content(block_size):
            progress_bar.update(len(block))
            file_desc.write(block)
