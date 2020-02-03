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

from .anonymous_request import AnonymousRequest
from .authentication_optional_request import AuthenticationOptionalRequest
from .base_request import RestoRequestResult


if TYPE_CHECKING:
    from resto_client.services.resto_service import RestoService  # @UnusedImport
    from resto_client.services.authentication_service import AuthenticationService  # @UnusedImport


class RevokeTokenRequest(AuthenticationOptionalRequest):
    """
     Request to revoke a token, and thus disconnecting the user.
    """

    request_action = 'revoking token'
    authentication_required = True

    def finalize_request(self) -> None:
        self.update_headers()
        return None

    def run_request(self) -> Response:
        return self.post()

    def process_request_result(self, request_result: Response) -> Response:
        return request_result


class GetTokenRequest(AuthenticationOptionalRequest):
    """
     Request to retrieve the token associated to the user
    """
    request_action = 'getting token'
    authentication_required = True

    def finalize_request(self) -> None:
        # No call to update_headers(), in order to avoid recursive calls
        return None

    def run_request(self) -> Union[Response, dict]:
        response: Union[Response, dict]
        if self.service_access.protocol == 'sso_dotcloud':
            response = self.post()
        elif self.service_access.protocol == 'sso_theia':
            response_text = self.post_as_text()
            response = {'token': response_text}
        else:
            response = self.get_response_as_json()
        return response

    def process_request_result(self, request_result: Response) -> str:
        return GetTokenResponse(self, request_result.json()).as_resto_object()

    def process_dict_result(self, request_result: dict) -> RestoRequestResult:
        return GetTokenResponse(self, request_result).as_resto_object()


class CheckTokenRequest(AnonymousRequest):
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
