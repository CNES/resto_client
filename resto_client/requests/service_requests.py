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
from requests import Response

from resto_client.entities.resto_collections import RestoCollections
from resto_client.responses.collections_description import (CollectionsDescription,
                                                            RestoResponseError)

from .anonymous_request import AnonymousRequest


class DescribeRequest(AnonymousRequest):
    """
     Request to retrieve the service description
    """
    request_action = 'getting service description'

    def process_request_result(self, request_result: Response) -> RestoCollections:
        try:
            collections_descr = CollectionsDescription(self, request_result.json())
        except RestoResponseError:
            msg = 'URL {} does not point to a valid resto server'
            raise ValueError(msg.format(self.service_access.base_url))

        return collections_descr.as_resto_object()
