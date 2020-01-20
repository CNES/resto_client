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


class RestoServerPersistable(RestoServer):
    """
    A class for building a RestoServer whose parameters can be persisted
    """

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
