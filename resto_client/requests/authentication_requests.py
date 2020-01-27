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
from typing import cast, TYPE_CHECKING  # @NoMove
import warnings

import requests

from resto_client.cli.resto_client_parameters import RestoClientParameters
from resto_client.responses.authentication_responses import GetTokenResponse, CheckTokenResponse

from .anonymous_request import AnonymousRequest
from .authentication_required_request import AuthenticationRequiredRequest


if TYPE_CHECKING:
    from resto_client.services.authentication_service import AuthenticationService  # @UnusedImport


class RevokeTokenRequest(AuthenticationRequiredRequest):
    """
     Request to revoke a token, and thus disconnecting the user.
    """

    request_action = 'revoking token'

    def run(self) -> requests.Response:
        """
        Close a user session with resto

        :returns: unknown result at the moment (not working)
        """
        # closing of user session impossible for now because of resto incapability
        self.set_headers()
        result = self.post()
        return result


class GetTokenRequest(AuthenticationRequiredRequest):
    """
     Request to retrieve the token associated to the user
    """
    request_action = 'getting token'

    def run(self) -> str:
        """
        :returns: the resto token associated to the user account
        """
        if self.service_access.protocol == 'sso_dotcloud':
            response_post = self.post().json()
            response_json = cast(dict, response_post)
        elif self.service_access.protocol == 'sso_theia':
            response_text = self.post_as_text()
            response_json = {'token': response_text}
        else:
            response_json = cast(dict, self.get_as_json())

        return GetTokenResponse(self, response_json).as_resto_object()


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

    def run(self) -> bool:
        """
        :returns: True if the token is still valid
        """
        if not self.supported_by_service():
            # CheckTokenRequest not supported by the service
            if RestoClientParameters.is_debug():
                msg = 'Launched a CheckTokenRequest whereas {} does not support it.'
                warnings.warn(msg.format(self.auth_service.parent_server.server_name))
            response_json = {'status': 'error', 'message': 'user not connected'}
        else:
            self.set_headers()
            response_json = cast(dict, self.get_as_json())
        return CheckTokenResponse(self, response_json).as_resto_object()
