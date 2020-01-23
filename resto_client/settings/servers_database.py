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
from pathlib import Path
from typing import Optional, Union

from resto_client.base_exceptions import RestoClientUserError, RestoClientDesignError
from resto_client.services.service_access import AuthenticationServiceAccess, RestoServiceAccess
from resto_client.settings.dict_settings import DictSettingsJson

from .resto_client_config import RESTO_CLIENT_CONFIG_DIR


RESTO_URL_KEY = 'resto_base_url'
RESTO_PROTOCOL_KEY = 'resto_protocol'
AUTH_URL_KEY = 'auth_base_url'
AUTH_PROTOCOL_KEY = 'auth_protocol'

WELL_KNOWN_SERVERS = {'kalideos': {RESTO_URL_KEY: 'https://www.kalideos.fr/resto2/',
                                   RESTO_PROTOCOL_KEY: 'dotcloud',
                                   AUTH_URL_KEY: 'https://www.kalideos.fr/drupal/api/resto'
                                   '/authenticate/',
                                   AUTH_PROTOCOL_KEY: 'sso_dotcloud'},
                      'ro': {RESTO_URL_KEY: 'https://www.recovery-observatory.org/resto2/',
                             RESTO_PROTOCOL_KEY: 'dotcloud',
                             AUTH_URL_KEY: 'https://www.recovery-observatory.org/drupal/api/resto'
                             '/authenticate/',
                             AUTH_PROTOCOL_KEY: 'sso_dotcloud'},
                      'pleiades': {RESTO_URL_KEY: 'https://www.pleiades-cnes.fr/resto2/',
                                   RESTO_PROTOCOL_KEY: 'dotcloud',
                                   AUTH_URL_KEY: 'https://www.pleiades-cnes.fr/drupal/api/resto'
                                   '/sso_cnes/authenticate/',
                                   AUTH_PROTOCOL_KEY: 'sso_dotcloud'},
                      'peps': {RESTO_URL_KEY: 'https://peps.cnes.fr/resto/',
                               RESTO_PROTOCOL_KEY: 'peps_version',
                               AUTH_URL_KEY: 'https://peps.cnes.fr/resto/',
                               AUTH_PROTOCOL_KEY: 'default'},
                      'theia': {RESTO_URL_KEY: 'https://theia.cnes.fr/atdistrib/resto2/',
                                RESTO_PROTOCOL_KEY: 'theia_version',
                                AUTH_URL_KEY: 'https://theia.cnes.fr/atdistrib/services'
                                '/authenticate/',
                                AUTH_PROTOCOL_KEY: 'sso_theia'},
                      'creodias': {RESTO_URL_KEY: 'https://finder.creodias.eu/resto/',
                                   RESTO_PROTOCOL_KEY: 'theia_version',
                                   AUTH_URL_KEY: 'https://finder.creodias.eu/resto/',
                                   AUTH_PROTOCOL_KEY: 'sso_theia'},
                      'cop_nci': {RESTO_URL_KEY: 'https://copernicus.nci.org.au/sara.server/1.0/',
                                  RESTO_PROTOCOL_KEY: 'theia_version',
                                  AUTH_URL_KEY: 'https://copernicus.nci.org.au/sara.server/1.0/',
                                  AUTH_PROTOCOL_KEY: 'default'},
                      'sent_hub': {RESTO_URL_KEY: 'http://opensearch.sentinel-hub.com/resto/',
                                   RESTO_PROTOCOL_KEY: 'theia_version',
                                   AUTH_URL_KEY: 'http://opensearch.sentinel-hub.com/resto/',
                                   AUTH_PROTOCOL_KEY: 'default'},
                      'rocket': {RESTO_URL_KEY: 'https://resto.mapshup.com/2.2/',
                                 RESTO_PROTOCOL_KEY: 'theia_version',
                                 AUTH_URL_KEY: 'https://resto.mapshup.com/2.2/',
                                 AUTH_PROTOCOL_KEY: 'default'}
                      }


class RestoClientUnexistingServer(RestoClientUserError):
    """
    Exception raised when requested server does not exist
    """


class ServerDescription():
    """
    Container class holding the description of a whole server:

     - the description of the resto service:

         - resto_base_url: its base url
         - resto_protocol: the supported protocol

     - the description of the authentication service (possibly identical to the resto service):

         - auth_base_url: its base url
         - auth_protocol: the supported protocol
    """

    def __init__(self,
                 resto_access: RestoServiceAccess,
                 auth_access: AuthenticationServiceAccess) -> None:
        """
        Constructor.

        :param resto_access: description of the resto service access
        :param auth_access: description of the authentication service access
        :raises RestoClientDesignError: when the arguments are not of the right types.
        """
        if not isinstance(resto_access, RestoServiceAccess):
            msg = 'resto_access must be of RestoServiceAccess type. Found {} instead.'
            raise RestoClientDesignError(msg.format(type(resto_access)))
        if not isinstance(auth_access, AuthenticationServiceAccess):
            msg = 'resto_access must be of AuthenticationServiceAccess type. Found {} instead.'
            raise RestoClientDesignError(msg.format(type(auth_access)))
        self.resto_access = resto_access
        self.auth_access = auth_access

    @classmethod
    def from_descr(cls, server_descr: dict) -> 'ServerDescription':
        """
        Initialize an instance from a dictionary containing all the entries needed for describing
        a server.

        :param server_descr: server description.
        :returns: an instance of this class.
        """
        resto_service_access = RestoServiceAccess(server_descr[RESTO_URL_KEY],
                                                  server_descr[RESTO_PROTOCOL_KEY])
        auth_service_access = AuthenticationServiceAccess(server_descr[AUTH_URL_KEY],
                                                          server_descr[AUTH_PROTOCOL_KEY])
        return cls(resto_service_access, auth_service_access)

    def as_descr(self) -> dict:
        """
        :returns: the definition of this server suitable for recording in the servers database.
        """
        return {RESTO_URL_KEY: self.resto_access.base_url,
                RESTO_PROTOCOL_KEY: self.resto_access.protocol,
                AUTH_URL_KEY: self.auth_access.base_url,
                AUTH_PROTOCOL_KEY: self.auth_access.protocol}


class ServersDatabase():
    """
    Class representing the whole servers definition database.
    """

    def __init__(self, db_path: Path) -> None:
        """
        Constructor.

        :param db_path: the path to the database where servers definitions are stored.
        """
        self.db_servers = DictSettingsJson(db_path, defaults=WELL_KNOWN_SERVERS)

    def get_server(self, server_name: str) -> ServerDescription:
        """
        Returns the server definition corresponding to the specified name.

        :param server_name: name of the server to retrieve in the database
        :returns: the full definition of the server composed of its 2 services.
        :raises RestoClientUnexistingServer: when the server is unknown in the database.
        """
        requested_server_name = ServersDatabase.get_canonical_name(server_name)
        try:
            return ServerDescription.from_descr(self.db_servers[requested_server_name])
        except KeyError:
            msg = 'Server {} does not exist in the servers database'
            raise RestoClientUnexistingServer(msg.format(requested_server_name))

    def exist_server(self, server_name: Union[str, None]) -> Optional[str]:
        """
        Check that the server exists in the servers database and returns its canonical name.

        :param server_name: name of the server to retrieve in the database
        :returns: the canonical name of the server or None if it does not exist.
        """
        server_name = ServersDatabase.get_canonical_name(server_name)
        try:
            _ = self.db_servers[server_name]
        except KeyError:
            server_name = None
        return server_name

    @staticmethod
    def get_canonical_name(server_name: Union[str, None]) -> Optional[str]:
        """
        Returns the normalized name of the server without looking for it in the database

        :param server_name: name of the server or None
        :returns: the canonical name of the server or None if server_name is None.
        """
        if server_name is not None:
            server_name = server_name.lower()
        return server_name

    def get_resto_service_protocol(self, server_name: str) -> str:
        """
        Returns the protocol associated to the resto service of a server.

        :param server_name: name of the server
        :returns: the resto protocol of the server.
        """
        return self.get_server(server_name).resto_access.protocol

    def delete(self, server_name: str) -> None:
        """
        Delete a server definition corresponding to the specified name.

        :param server_name: name of the server to delete in the database
        :raises RestoClientUnexistingServer: when the server is unknown in the database.
        """
        canonical_server_name = self.exist_server(server_name)
        if canonical_server_name is not None:
            del self.db_servers[canonical_server_name]
            self.db_servers.save()

    def create_server(self,
                      server_name: Union[str, None],
                      resto_access: RestoServiceAccess,
                      auth_access: AuthenticationServiceAccess) -> None:
        """
        Creates a new server definition.

        :param server_name: name of the server to create in the database. A None value is rejected.
        :param resto_access: Access parameters to the resto service
        :param auth_access: Access parameters to the authentication service
        :raises RestoClientUserError: raised in several circumstances:
                                      - when a server already exist with this name
                                      - when the server name is not a valid str
        :raises RestoClientDesignError: when resto_access or auth_access are not ServiceAccess
                                        instances.
        """
        if not isinstance(resto_access, RestoServiceAccess):
            msg = 'resto_access must be of RestoServiceAccess type. Found {} instead.'
            raise RestoClientDesignError(msg.format(type(resto_access)))
        if not isinstance(auth_access, AuthenticationServiceAccess):
            msg = 'auth_access must be of AuthenticationServiceAccess type. Found {} instead.'
            raise RestoClientDesignError(msg.format(type(auth_access)))
        server_name = ServersDatabase.get_canonical_name(server_name)
        if not isinstance(server_name, str):
            msg = 'Invalid server name type. Found {} instead of str'
            raise RestoClientUserError(msg.format(type(server_name)))

        if self.exist_server(server_name) is not None:
            # Server already exist
            msg = 'Server {} already exists in the server database.'
            raise RestoClientUserError(msg.format(server_name))

        self.db_servers[server_name] = ServerDescription(resto_access, auth_access).as_descr()
        self.db_servers.save()

    def __str__(self) -> str:
        return str(self.db_servers)


RESTO_CLIENT_SERVER_FILENAME = RESTO_CLIENT_CONFIG_DIR / 'resto_client_server_settings.json'
DB_SERVERS = ServersDatabase(RESTO_CLIENT_SERVER_FILENAME)
