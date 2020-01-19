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


class RestoClientNoPersistedServer(RestoClientUserError):
    """ Exception raised when no persisted server found """


class RestoServerParameters(RestoServer):
    """
    A class holding the persisted server parameters
    """

    @classmethod
    def persisted(cls, persisted_params: dict) -> 'RestoServerParameters':
        """
        Build an instance from the persisted server parameters.

        :raises RestoClientNoPersistedServer: when no server is found in the persisted parameters
        :returns: a RestoServer built from persisted parameters
        """
        # Retrieve persisted server name and build an empty server parameters instance
        persisted_server_name = persisted_params.get('server_name')
        if persisted_server_name is None:
            msg = 'No server currently set in the persisted parameters.'
            raise RestoClientNoPersistedServer(msg)
        persisted_server_parameters = cls(persisted_server_name)

        # Retrieve persisted collection name
        persisted_collection_name = persisted_params.get('current_collection')
        # Update server parameters instance to trigger RestoServer update.
        persisted_server_parameters.current_collection = persisted_collection_name

        # Retrieve persisted username
        persisted_username = persisted_params.get('username')
        # Retrieve persisted token
        persisted_token = persisted_params.get('token')
        # Update server parameters instance to trigger RestoServer update.
        persisted_server_parameters.set_credentials(username=persisted_username,
                                                    token_value=persisted_token)

        return persisted_server_parameters

    def update_persisted(self, persisted_params: dict) -> None:
        self._update_persisted_attr(persisted_params, 'server_name')
        self._update_persisted_attr(persisted_params, 'current_collection')
        self._update_persisted_attr(persisted_params, 'username')
        self._update_persisted_attr(persisted_params, 'token')

    def _update_persisted_attr(self, persisted_params: dict, attr_name: str) -> None:
        persisted_params[attr_name] = getattr(self, attr_name)
        if persisted_params[attr_name] is None:
            del persisted_params[attr_name]

    def __str__(self) -> str:
        msg_fmt = 'server_name: {}, current_collection: {}, username: {}'
        return msg_fmt.format(self.server_name, self.current_collection, self.username)
