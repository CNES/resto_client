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

from resto_client.settings.servers_database import DB_SERVERS

from .authentication_service import AuthenticationService
from .resto_service import RestoService


class RestoServer():
    """
        A Resto Server, i.e. a valid resto accessible server
    """

    def __init__(self, server_name: str,
                 username: Optional[str]= None, password: Optional[str]=None) -> None:
        """
        Constructor

        :param server_name: the name of the server to use in the database
        :param username: name of the account on the server
        :param password: user password
        """
        server_description = DB_SERVERS.get_server(server_name)
        self.authentication_service = AuthenticationService(server_description.auth_access)
        self.authentication_service.set_credentials(username=username, password=password)
        self.resto_service = RestoService(resto_access=server_description.resto_access,
                                          auth_service=self.authentication_service)
        self.resto_service.update_after_url_change()
        self.server_name = server_name  # type: ignore

    @property
    def current_collection(self) -> Optional[str]:
        """
        :returns: the current collection
        """
        return self.resto_service.current_collection

    @current_collection.setter
    def current_collection(self, collection_name: Optional[str]) -> None:
        """
        :param collection_name: collection to use
        """
        self.resto_service.current_collection = collection_name
