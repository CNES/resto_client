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
from resto_client.settings.resto_client_settings import RESTO_CLIENT_SETTINGS
from resto_client.settings.servers_database import DB_SERVERS

from .authentication_credentials import AuthenticationCredentials
from .authentication_service import AuthenticationService
from .resto_collections_manager import RestoCollectionsManager
from .resto_service import RestoService


class RestoClientNoPersistedServer(RestoClientUserError):
    """ Exception raised when no persisted server found """


class RestoServer():
    """
        A Resto Server, i.e. a valid resto accessible server
    """

    properties_storage = RESTO_CLIENT_SETTINGS

    def __init__(self, server_name: str,
                 username: Optional[str]= None, password: Optional[str]=None) -> None:
        """
        Constructor

        :param server_name: the name of the server to use in the database
        :param username: name of the account on the server
        :param password: user password
        """
        server_description = DB_SERVERS.get_server(server_name)
        self.auth_service = AuthenticationService(server_description.auth_access)
        self.auth_service.set_credentials(username=username, password=password)
        self.resto_service = RestoService(resto_access=server_description.resto_access,
                                          auth_service=self.auth_service)
        self.resto_service.update_after_url_change()
        self.server_name = server_name  # type: ignore

    @classmethod
    def persisted(cls) -> 'RestoServer':
        """
        :returns: a resto server from the persisted parameters.
        :raises RestoClientNoPersistedServer: when no server is found in the persisted parameters
        """
        # Retrieve persisted server name
        persisted_server_name = cls.properties_storage.get('server_name')
        if persisted_server_name is None:
            msg = 'No server currently set in the persisted parameters.'
            raise RestoClientNoPersistedServer(msg)
        instance = cls(persisted_server_name)

        # Update authentication service persisted parameters
        auth_service = instance.auth_service
        persisted_credentials = AuthenticationCredentials.persisted(auth_service)
        auth_service.set_credentials(persisted_credentials)

        # Retrieve persisted access to the resto service
        resto_service = instance.resto_service
        persisted_coll_manager = RestoCollectionsManager.persisted(resto_service)
        resto_service.set_collection_mgr(persisted_coll_manager)
        return instance

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
