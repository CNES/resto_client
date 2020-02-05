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
from typing import Optional, Union, TYPE_CHECKING  # @NoMove
import warnings

from requests import Response

from resto_client.responses.authentication_responses import GetTokenResponse, CheckTokenResponse

from .base_request import RestoRequestResult, BaseRequest
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

    def run_request(self) -> Response:
        return self.post()

    def process_request_result(self, request_result: Response) -> Response:
        return request_result


class GetTokenRequest(BaseRequest):
    """
     Request to retrieve the token associated to the user
    """
    request_action = 'getting token'
    authentication_type = 'ALWAYS'

    def finalize_request(self) -> None:
        # No call to update_headers(), in order to avoid recursive calls
        return None

    def run_request(self) -> Response:
        if self.service_access.protocol in ['sso_dotcloud', 'sso_theia']:
            response = self.post()
        else:
            response = self.get_response_as_json()
        return response

    def process_request_result(self, request_result: Response) -> str:
        # FIXME: check if text could be tested instead of protocol
        if self.service_access.protocol == 'sso_theia':
            response_text = request_result.text
            if response_text == 'Please set mail and password':
                msg = 'Connection Error : "{}", connection not allowed with ident/pass given'
                raise AccesDeniedError(msg.format(response_text))
            return GetTokenResponse(self, {'token': response_text}).as_resto_object()
        return GetTokenResponse(self, request_result.json()).as_resto_object()


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

    def finalize_request(self) -> Optional[dict]:
        simulated_response: Optional[dict]
        if not self.supported_by_service():
            # CheckTokenRequest not supported by the service
            if self.parent_service.parent_server.debug_server:
                msg = 'Launched a CheckTokenRequest whereas {} does not support it.'
                warnings.warn(msg.format(self.auth_service.parent_server.server_name))
            simulated_response = {'status': 'error', 'message': 'user not connected'}
        else:
            simulated_response = super(CheckTokenRequest, self).finalize_request()
        return simulated_response

    def run_request(self) -> Response:
        return self.get_response_as_json()

    def process_request_result(self, request_result: Response) -> bool:
        return CheckTokenResponse(self, request_result.json()).as_resto_object()

    def process_dict_result(self, request_result: dict) -> RestoRequestResult:
        return CheckTokenResponse(self, request_result).as_resto_object()
