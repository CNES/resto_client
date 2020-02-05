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
from typing import TYPE_CHECKING, cast  # @NoMove

from requests import Response

from resto_client.responses.authentication_responses import GetTokenResponse, CheckTokenResponse
from resto_client.services.service_access import RestoClientUnsupportedRequest

from .base_request import BaseRequest, RestoClientEmulatedResponse
from .utils import AccesDeniedError

if TYPE_CHECKING:
    from resto_client.services.resto_service import RestoService  # @UnusedImport
    from resto_client.services.authentication_service import AuthenticationService  # @UnusedImport


class RevokeTokenRequest(BaseRequest):
    """
     Request to revoke a token, and thus disconnecting the user.
    """

    request_action = 'revoking token'
    authentication_type = 'ALWAYS'

    def run(self) -> Response:
        # overidding BaseRequest method, in order to specify the right type returned by this request
        return cast(Response, super(RevokeTokenRequest, self).run())

    def run_request(self) -> Response:
        return self.post()

    def process_request_result(self) -> Response:
        return self._request_result


class GetTokenRequest(BaseRequest):
    """
     Request to retrieve the token associated to the user
    """
    request_action = 'getting token'
    authentication_type = 'ALWAYS'

    def run(self) -> str:
        # overidding BaseRequest method, in order to specify the right type returned by this request
        return cast(str, super(GetTokenRequest, self).run())

    def finalize_request(self) -> None:
        # No call to update_headers(), in order to avoid recursive calls
        return None

    def run_request(self) -> Response:
        if self.service_access.protocol in ['sso_dotcloud', 'sso_theia']:
            response = self.post()
        else:
            response = self.get_response_as_json()
        return response

    def process_request_result(self) -> str:
        # FIXME: check if text could be tested instead of protocol
        if self.service_access.protocol == 'sso_theia':
            response_text = self._request_result.text
            if response_text == 'Please set mail and password':
                msg = 'Connection Error : "{}", connection not allowed with ident/pass given'
                raise AccesDeniedError(msg.format(response_text))
            return GetTokenResponse(self, {'token': response_text}).as_resto_object()
        return GetTokenResponse(self, self._request_result.json()).as_resto_object()


class CheckTokenRequest(BaseRequest):
    """
     Request to check a service token.
    """
    request_action = 'checking token'
    authentication_type = 'NEVER'

    def __init__(self, service: 'AuthenticationService', token: str) -> None:
        """
        :param service: authentication service
        :param token: token to be checked
        :raises TypeError: when token argument type is not an str
        """
        if not isinstance(token, str):
            raise TypeError('token argument must be of type <str>')
        super(CheckTokenRequest, self).__init__(service, token=token)

    def run(self) -> bool:
        # overidding BaseRequest method, in order to specify the right type returned by this request
        return cast(bool, super(CheckTokenRequest, self).run())

    def finalize_request(self) -> None:
        try:
            super(CheckTokenRequest, self).finalize_request()
        except RestoClientUnsupportedRequest:
            print('emulating unsupported CheckTokenRequest')
            emulated_response = RestoClientEmulatedResponse()
            emulated_json = {'status': 'error', 'message': 'user not connected'}
            emulated_response.result = CheckTokenResponse(self, emulated_json).as_resto_object()
            raise emulated_response

    def process_request_result(self) -> bool:
        return CheckTokenResponse(self, self._request_result.json()).as_resto_object()
