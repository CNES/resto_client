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


class RestoResponseError(RestoClientServerError):
    """
    Exception raised when a Resto response cannot be understood
    """


class AccessDeniedError(RestoResponseError):
    """
    Exception corresponding to forbiden access due to credential
    """


class RestoClientEvent(RestoClientError):
    """
    Exception raised when a Resto response cannot be understood
    """
