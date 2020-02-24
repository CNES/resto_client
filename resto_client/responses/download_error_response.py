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
from .resto_response_error import RestoResponseError


class DownloadErrorResponse(RestoJsonResponseSimple):
    """
    Response received during Download*Request when download cannot be done for some reason.
    """

    needed_fields = ['ErrorMessage', 'ErrorCode',
                     'feature', 'collection', 'license_id', 'license', 'user_id']
    optional_fields: List[str] = []

    def identify_response(self) -> None:
        """
        Verify that the response is a valid json response when download request are submitted.

        :raises RestoResponseError: if the dictionary does not contain a valid Resto response.
        """
        # Firstly verify that the needed fields are present and build standard normalized response.
        super(DownloadErrorResponse, self).identify_response()

        # Secondly verify that no code different from those we understand are present.
        if self._original_response['ErrorCode'] not in [3002, 3006]:
            msg = 'Received a DownloadErrorResponse with unsupported error code: {}.'
            raise RestoResponseError(msg.format(self._original_response['ErrorCode']))

    @property
    def download_need_license_signature(self) -> bool:
        """
        :returns: True if the user needs to sign the license specified in this error
        """
        return self._normalized_response['ErrorCode'] == 3002

    @property
    def license_to_sign(self) -> str:
        """
        :returns: the license_id of the license which must be signed by the user.
        """
        return self._normalized_response['license_id']

    @property
    def download_forbidden(self) -> bool:
        """
        :returns: True if the user has no right to request this product download.
        """
        return self._normalized_response['ErrorCode'] == 3006

    @property
    def requested_feature(self) -> str:
        """
        :returns: The feature id whose download has been requested.
        """
        return self._normalized_response['feature']

    def as_resto_object(self) -> 'DownloadErrorResponse':
        """
        :returns: the response expressed as a Resto object
        """
        return self
