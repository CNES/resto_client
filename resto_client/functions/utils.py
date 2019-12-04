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
from urllib.parse import urlparse, urlunparse
from mimetypes import guess_extension, MimeTypes
from typing import Optional


def contract_url(full_url: str) -> str:
    """
    Contract a url to appear with ...

    :param full_url: full url to contract for printing
    :returns: contracted url
    """
    url_lst = list(urlparse(full_url))
    # delete params, query and fragment
    for i in [3, 4, 5]:
        url_lst[i] = ''
    # reduce url : path parts
    path_parts = url_lst[2].split('/')
    url_lst[2] = '/'.join((path_parts[0], '...', path_parts[-2], path_parts[-1]))
    contracted_url = urlunparse(url_lst)

    return contracted_url


def is_valid_url(url: str) -> bool:
    """
    Validate if the passed argument looks like a valid url.

    :param url: url to check
    :returns: True if the argument looks like a valid URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def guess_extension_with_charset(content_type: str) -> Optional[str]:
    """
    Guess proper extension to use, even if charset is present in content_type

    :param content_type: content_type to check
    :returns: extension
    """
    guess_from = content_type
    for kind_of_mimetype in MimeTypes().types_map_inv:
        for key in kind_of_mimetype:
            if content_type.startswith(str(key)):
                guess_from = str(key)
    return guess_extension(guess_from.strip())
