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
from resto_client.base_exceptions import RestoClientUserError
from resto_client.services.resto_server import RestoServer

from .persistence import PersistedAttributes
from .resto_client_settings import PERSISTED_SERVER_PARAMETERS


class RestoClientNoPersistedServer(RestoClientUserError):
    """ Exception raised when no persisted server found """


class RestoServerPersistable(RestoServer, PersistedAttributes):
    """
    A class for building a RestoServer whose parameters can be persisted
    """

    persisted_attributes = PERSISTED_SERVER_PARAMETERS
