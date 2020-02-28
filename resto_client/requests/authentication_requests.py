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
from typing import cast, Optional  # @NoMove


from resto_client.base_exceptions import RestoResponseError
from resto_client.responses.authentication_responses import (GetTokenResponse, CheckTokenResponse,
                                                             RevokeTokenResponse)
from resto_client.services.service_access import RestoClientUnsupportedRequest

from .base_request import BaseRequest, RestoClientEmulatedResponse
from .resto_json_request import RestoJsonRequest


class RevokeTokenRequest(BaseRequest):
    """
     Request to revoke a token, and thus disconnecting the user.
    """

    request_action = 'revoking token'

    def run(self) -> RevokeTokenResponse:
        # overidding BaseRequest method, in order to specify the right type returned by this request
        return cast(RevokeTokenResponse, super(RevokeTokenRequest, self).run())

    def process_request_result(self) -> RevokeTokenResponse:
        content_type = self._request_result.headers['content-type']
        if 'application/json' in content_type:
            get_token_response_content = self._request_result.json()
        else:
            msg_fmt = 'Unable to process RevokeToken response: headers : {} \n content: {}'
            raise RestoResponseError(msg_fmt.format(self._request_result.headers,
                                                    self._request_result.content))
        return RevokeTokenResponse(self, get_token_response_content).as_resto_object()


class GetTokenRequest(BaseRequest):
    """
     Request to retrieve the token associated to the user
    """
    request_action = 'getting token'

    def run(self) -> GetTokenResponse:
        # overidding BaseRequest method, in order to specify the right type returned by this request
        return cast(GetTokenResponse, super(GetTokenRequest, self).run())

    def update_headers(self, dict_input: Optional[dict]=None) -> None:
        if dict_input is not None:
            self._request_headers.update(dict_input)

    def process_request_result(self) -> GetTokenResponse:
        content_type = self._request_result.headers['content-type']
        if 'application/json' in content_type:
            get_token_response_content = self._request_result.json()
        elif 'text/html' in content_type:
            response_text = self._request_result.text
            if response_text in ['Please set mail and password', '']:
                get_token_response_content = {'success': False}
                if response_text != '':
                    get_token_response_content['message'] = response_text
            else:
                get_token_response_content = {'success': True, 'token': response_text}
        else:
            msg_fmt = 'Unable to process GetToken response: headers : {} \n content: {}'
            raise RestoResponseError(msg_fmt.format(self._request_result.headers,
                                                    self._request_result.content))
        return GetTokenResponse(self, get_token_response_content).as_resto_object()


class CheckTokenRequest(RestoJsonRequest):
    """
     Request to check a service token.
    """
    request_action = 'checking token'
    resto_response_cls = CheckTokenResponse

    def run(self) -> CheckTokenResponse:
        # overidding BaseRequest method, in order to specify the right type returned by this request
        return cast(CheckTokenResponse, super(CheckTokenRequest, self).run())

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
