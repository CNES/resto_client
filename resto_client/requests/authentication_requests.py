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
from json.decoder import JSONDecodeError

from requests import Response

from resto_client.responses.authentication_responses import GetTokenResponse, CheckTokenResponse
from resto_client.services.service_access import RestoClientUnsupportedRequest

from .base_request import BaseRequest, RestoClientEmulatedResponse, AccesDeniedError

if TYPE_CHECKING:
    from resto_client.services.authentication_service import AuthenticationService  # @UnusedImport


class RevokeTokenRequest(BaseRequest):
    """
     Request to revoke a token, and thus disconnecting the user.
    """

    request_action = 'revoking token'

    def run(self) -> Response:
        # overidding BaseRequest method, in order to specify the right type returned by this request
        return cast(Response, super(RevokeTokenRequest, self).run())

    def process_request_result(self) -> Response:
        return self._request_result


class GetTokenRequest(BaseRequest):
    """
     Request to retrieve the token associated to the user
    """
    request_action = 'getting token'

    def run(self) -> str:
        # overidding BaseRequest method, in order to specify the right type returned by this request
        return cast(str, super(GetTokenRequest, self).run())

    def process_request_result(self) -> str:
        try:
            get_token_response_content = self._request_result.json()
        except JSONDecodeError:
            response_text = self._request_result.text
            # FIXME:For the sake of homogeneity, exception should be raised by GetTokenResponse,
            if response_text == 'Please set mail and password':
                msg = 'Connection Error : "{}", connection not allowed with ident/pass given'
                raise AccesDeniedError(msg.format(response_text))
            get_token_response_content = {'token': response_text}
        return GetTokenResponse(self, get_token_response_content).as_resto_object()


class CheckTokenRequest(BaseRequest):
    """
     Request to check a service token.
    """
    request_action = 'checking token'

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
            if self.debug:
                print('emulating unsupported CheckTokenRequest')
            emulated_response = RestoClientEmulatedResponse()
            emulated_dict = {'status': 'error', 'message': 'user not connected'}
            emulated_response.result = CheckTokenResponse(self, emulated_dict).as_resto_object()
            raise emulated_response

    def process_request_result(self) -> bool:
        return CheckTokenResponse(self, self._request_result.json()).as_resto_object()
