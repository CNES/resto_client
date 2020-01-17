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
from typing import Optional

from resto_client.base_exceptions import RestoClientUserError
from resto_client.generic.property_decoration import managed_getter, managed_setter
from resto_client.services.authentication_credentials import AuthenticationCredentials
from resto_client.services.resto_server import RestoServer

from .resto_client_settings import RESTO_CLIENT_SETTINGS


class RestoClientNoPersistedServer(RestoClientUserError):
    """ Exception raised when no persisted server found """


class ServerParameters():
    """
    A class holding the persisted server parameters
    """

    properties_storage = RESTO_CLIENT_SETTINGS

    def __init__(self, server_name: str) -> None:
        """
        Constructor

        :param server_name: the name of the server.
        """

        self.resto_server = RestoServer(server_name)
        self.server_name = server_name  # type: ignore

        # Update authentication service persisted parameters
        authentication_service = self.resto_server.authentication_service
        persisted_credentials = AuthenticationCredentials.persisted(authentication_service)
        authentication_service.set_credentials(persisted_credentials)

    @classmethod
    def persisted(cls) -> 'ServerParameters':
        """
        Build an instance from the persisted server parameters.

        :raises RestoClientNoPersistedServer: when no server is found in the persisted parameters
        :returns: an instance of ServerParameters built from persisted parameters
        """
        # Retrieve persisted server name and build an empty server parameters instance
        persisted_server_name = ServerParameters.properties_storage.get('server_name')
        if persisted_server_name is None:
            msg = 'No server currently set in the persisted parameters.'
            raise RestoClientNoPersistedServer(msg)
        persisted_server_parameters = cls(persisted_server_name)

        # Retrieve persisted collection name
        persisted_collection_name = ServerParameters.properties_storage.get('current_collection')
        # Update server parameters instance to trigger RestoServer update.
        persisted_server_parameters.current_collection = persisted_collection_name  # type: ignore

        return persisted_server_parameters

    @property  # type: ignore
    @managed_getter()
    def server_name(self) -> Optional[str]:
        """
        :returns: the name of the server
        """

    @server_name.setter  # type: ignore
    @managed_setter()
    def server_name(self, server_name: str) -> None:
        """
        :param server_name: the name of the server in the servers database.
        """
        # This code is called only when this property has been changed from its previous value.
        # Thus we need to reset the server parameters.
        _ = server_name  # to get rid of pylint warning
        self.current_collection = None  # type: ignore

    @property  # type: ignore
    @managed_getter()
    def current_collection(self) -> Optional[str]:
        """
        :returns: the name of the current collection
        """

    @current_collection.setter  # type: ignore
    @managed_setter()
    def current_collection(self, collection_name: str) -> None:
        """
        :param collection_name: the name of the collection to set.
        """
        # This code is called only when this property has been changed from its previous value.
        # Update resto_server proxified current collection.
        self.resto_server.current_collection = collection_name
        # In order to update persisted current collection name with right case.
        self.current_collection = self.resto_server.current_collection  # type: ignore

    def update_persisted(self, persisted_params: dict) -> None:
        self._update_persisted_attr(persisted_params, 'server_name')
        self._update_persisted_attr(persisted_params, 'current_collection')

    def _update_persisted_attr(self, persisted_params: dict, attr_name: str) -> None:
        persisted_params[attr_name] = getattr(self, attr_name)
        if persisted_params[attr_name] is None:
            del persisted_params[attr_name]
