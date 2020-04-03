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
from typing import List  # @UnusedImport

from .resto_json_response import RestoJsonResponseSimple


class SignLicenseResponse(RestoJsonResponseSimple):
    """
     Response received from SignLicenseRequest.
    """

    needed_fields = ['status', 'message']
    optional_fields: List[str] = []

    @property
    def is_signed(self) -> bool:
        """
        :returns: the signature validity
        """
        return self._normalized_response['status'] == 'success'

    @property
    def validation_message(self) -> str:
        """
        :returns: the signed license's validation message
        """
        return self._normalized_response['message']

    def as_resto_object(self) -> 'SignLicenseResponse':
        """
        :returns: the response expressed as a Resto object
        """
        return self
