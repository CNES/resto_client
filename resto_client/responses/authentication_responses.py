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

from resto_client.requests.base_request import AccesDeniedError

from .resto_json_response import RestoJsonResponseSimple


class GetTokenResponse(RestoJsonResponseSimple):
    """
     Response received from GetTokenRequest.

     The normalized response for a GetToken request is defined by the following fields:

     - 'success': boolean True means that a token was retrieved successfully.
     - 'token': contains the token string. Exists only when 'success' is True.
     - 'message': contains the error reason when 'success' is False. Not available for all servers.
    """
    needed_fields: List[str] = []
    optional_fields = ['success', 'token', 'message']

    def normalize_response(self) -> None:
        """
        Returns a normalized response whose structure does not depend on the server.
        """
        # First copy the fields present in the original response.
        self._normalized_response = {}
        if 'success' in self._original_response:
            self._normalized_response['success'] = self._original_response['success']
        if 'token' in self._original_response:
            self._normalized_response['token'] = self._original_response['token']
        if 'message' in self._original_response:
            self._normalized_response['message'] = self._original_response['message']

        # Create a 'success' field if it was missing in the original response.
        if 'success' not in self._normalized_response:
            # Some servers signal failure by returning an empty token string.
            # It is also a failure to have no returned token field.
            self._normalized_response['success'] = self._normalized_response.get('token', '') != ''

    @property
    def token_value(self) -> str:
        """
        :returns: the token included in the response
        :raises AccesDeniedError: when the GetToken request was rejected for incorrect credentials.
        """
        if self._normalized_response['success']:
            return self._normalized_response['token']
        # response reported a failure. If a message is available use it otherwise create one.
        if 'message' in self._normalized_response:
            msg_excp = self._normalized_response['message']
        else:
            msg_excp = 'Invalid username/password'
        raise AccesDeniedError(msg_excp)

    def as_resto_object(self) -> 'GetTokenResponse':
        """
        :returns: the response expressed as a Resto response
        """
        return self


class CheckTokenResponse(RestoJsonResponseSimple):
    """
     Response received from CheckTokenRequest.
    """

    needed_fields = ['status', 'message']
    optional_fields: List[str] = []

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
