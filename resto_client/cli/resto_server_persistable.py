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
from .resto_client_settings import (USERNAME_KEY, SERVER_KEY, TOKEN_KEY, COLLECTION_KEY,
                                    PERSISTED_SERVER_PARAMETERS)


class RestoClientNoPersistedServer(RestoClientUserError):
    """ Exception raised when no persisted server found """


class RestoServerPersistable(RestoServer, PersistedAttributes):
    """
    A class for building a RestoServer whose parameters can be persisted
    """

    persisted_attributes = PERSISTED_SERVER_PARAMETERS

    @classmethod
    def build_from_dict(cls, server_parameters: dict) -> 'RestoServerPersistable':
        """
        Build an instance from a set of parameters defined in a dictionary.

        :param server_parameters: the set of parameters needed for building the server
        :raises KeyError: when no server name is found in the parameters
        :returns: a RestoServer built from server parameters
        """
        # Retrieve the server name in the dictionary
        server_name = server_parameters.get(SERVER_KEY)
        if server_name is None:
            msg = 'No server name defined in the server parameters.'
            raise KeyError(msg)

        # Retrieve other server parameters in the dictionary
        collection_name = server_parameters.get(COLLECTION_KEY)
        username = server_parameters.get(USERNAME_KEY)
        token = server_parameters.get(TOKEN_KEY)

        # Build a new_server with these parameters
        return cls.new_server(server_name, current_collection=collection_name,
                              username=username, token=token)
