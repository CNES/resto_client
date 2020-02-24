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
from typing import cast  # @NoMove

from resto_client.entities.resto_collections import RestoCollections
from resto_client.responses.collections_description import CollectionsDescription

from .resto_json_request import RestoJsonRequest


class DescribeRequest(RestoJsonRequest):
    """
     Request to retrieve the service description
    """
    request_action = 'getting service description'
    resto_response_cls = CollectionsDescription

    def run(self) -> RestoCollections:
        # overidding BaseRequest method, in order to specify the right type returned by this request
        return cast(RestoCollections, super(DescribeRequest, self).run())
