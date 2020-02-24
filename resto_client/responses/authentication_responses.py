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
from .resto_json_response import RestoJsonResponseSimple


class GetTokenResponse(RestoJsonResponseSimple):
    """
     Response received from GetTokenRequest.
    """
    needed_fields = ['token']

    def as_resto_object(self) -> str:
        """
        :returns: the response expressed as a Resto object
        """
        return self._normalized_response['token']


class CheckTokenResponse(RestoJsonResponseSimple):
    """
     Response received from CheckTokenRequest.
    """

    needed_fields = ['status', 'message']

    @property
    def is_valid(self) -> bool:
        """
        :returns: the token's validity
        """
        return self._normalized_response['status'] == 'success'

    @property
    def validation_message(self) -> bool:
        """
        :returns: the token's validation message
        """
        return self._normalized_response['message']

    def as_resto_object(self) -> 'CheckTokenResponse':
        """
        :returns: the response expressed as a Resto response
        """
        return self
