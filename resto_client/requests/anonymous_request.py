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
from abc import abstractmethod
from typing import Optional
from requests import Response

from .base_request import BaseRequest, RestoRequestResult


class AnonymousRequest(BaseRequest):
    """
     Base class for resto requests which does need authentication
    """

    def finalize_request(self) -> Optional[dict]:
        self.update_headers()
        return None

    def run_request(self) -> Response:
        return self.get_response_as_json()

    @abstractmethod
    def process_request_result(self, request_result: Response) -> RestoRequestResult:
        pass
