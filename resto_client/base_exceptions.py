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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from resto_client.requests.base_request import RestoRequestResult  # @UnusedImport
    from resto_client.responses.download_error_response import \
        DownloadErrorResponse  # @UnusedImport


class RestoClientError(Exception):
    """
    Base exception for all resto_client specific exceptions.
    """
    print_to_terminal = False


class RestoClientUserError(RestoClientError):
    """
    Base exception for all resto_client exceptions which correspond to a user mistake.
    """
    print_to_terminal = True


class RestoClientDesignError(RestoClientError):
    """
    Base exception for all resto_client exceptions which correspond to a design or coding error.
    """


class RestoClientServerError(RestoClientError):
    """
    Base exception for all resto_client exceptions which correspond to a server error.
    """


class RestoNetworkError(RestoClientServerError):
    """
    Base exception for all resto_client exceptions which correspond to network.
    """


class NetworkAccessDeniedError(RestoNetworkError):
    """
    Exception corresponding to HTTP Error 403
    """


# ++++++++++++++++++++ Exceptions raised when processing resto responses +++++++++++++++++++++++

class RestoResponseError(RestoClientServerError):
    """
    Exception raised when a Resto response cannot be understood
    """


class IncomprehensibleResponse(RestoResponseError):
    """
    Exception raised when response cannot be understood.
    """


class UnsupportedError(RestoResponseError):
    """
    Exception raised when error code is not supported
    """


class InconsistentResponse(RestoResponseError):
    """
    Exception raised when response is inconsistent with the request
    """


class AccessDeniedError(RestoResponseError):
    """
    Exception corresponding to forbiden access due to credential
    """

# ++++++++++++++++++++ Application events implemented as exceptions +++++++++++++++++++++++


class RestoClientEvent(RestoClientError):
    """
    Exception raised when a Resto response cannot be understood
    """


class RestoClientEmulatedResponse(RestoClientEvent):
    """
    Exception raised when an emulated response is to be processed.
    """
    result: 'RestoRequestResult'


class FeatureOnTape(RestoClientEvent):
    """
    Exception raised when a product requested is on tape
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        super(FeatureOnTape, self).__init__('Moving feature from tape to disk')


class LicenseSignatureRequested(RestoClientEvent):
    """
    Exception raised when a license signature is requested before proceeding with the download.
    """

    def __init__(self, error_response: 'DownloadErrorResponse') -> None:
        """
        Constructor.

        :param error_response: the error response as provided by resto, which contains the
                               identifier of the license to sign.
        """
        super(LicenseSignatureRequested, self).__init__('user needs to sign a license')
        self.error_response = error_response
