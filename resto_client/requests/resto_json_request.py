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
from abc import abstractmethod
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Type, Optional

from resto_client.responses.collections_description import RestoResponseError
from resto_client.responses.resto_json_response import RestoJsonResponse
from resto_client.settings.resto_client_config import RESTO_CLIENT_CONFIG_DIR

from .base_request import BaseRequest, RestoRequestResult


class RestoJsonRequest(BaseRequest):
    """
     Base class for requests able to provide a RestoJsonResponse with associated as_resto_object()
     method. Response caching can be enable client by client class, by specifying a positive number
     of caching seconds.
    """
    @property  # type:ignore
    @abstractmethod
    def resto_response_cls(self) -> Type[RestoJsonResponse]:
        """
        :returns: the action performed by this request.
        """

    # TODO: parameterize duration into request description.
    caching_max_seconds = 0

    @property
    def cache_file_name(self) -> Path:
        """
        :returns: the path to a file containing the cached json response.
        """
        cache_dir = self.parent_service.parent_server.ensure_server_directory(
            RESTO_CLIENT_CONFIG_DIR)
        return cache_dir / f'{self.__class__.__name__}_result.json'

    def get_cached_response(self) -> Optional[dict]:
        """
        :returns: the cached response as a dictionary if the cached response has not expired, None
                  otherwise.
        """
        cached_response = None
        # if caching is enabled for this request and cached file exists
        if self.caching_max_seconds > 0 and self.cache_file_name.exists():
            # Using file modification time to avoid file "tunneling" management on some OS.
            cache_file_modif_time = datetime.fromtimestamp(self.cache_file_name.stat().st_mtime)
            cache_file_age = datetime.now() - cache_file_modif_time
            if cache_file_age < timedelta(seconds=self.caching_max_seconds):
                if self.debug:
                    print(f'Using cached response for {self.__class__.__name__}')
                with open(self.cache_file_name) as json_file:
                    cached_response = json.load(json_file)
            else:
                if self.debug:
                    print('removing too old cached file')
                self.cache_file_name.unlink()
        return cached_response

    def set_cached_response(self) -> None:
        """
        When cache is enabled, records the current request response json content in the cache file.
        """
        if self.caching_max_seconds > 0:  # if caching is enabled for this request
            json_response = self._request_result.json()
            with open(self.cache_file_name, 'w') as json_file:
                json.dump(json_response, json_file)

    def run(self) -> RestoRequestResult:
        cached_response = self.get_cached_response()
        if cached_response is not None:
            resto_object = self.process_json_result(cached_response)
        else:
            resto_object = super(RestoJsonRequest, self).run()
            self.set_cached_response()
        return resto_object

    def process_request_result(self) -> RestoRequestResult:
        return self.process_json_result(self._request_result.json())

    # TOSO: think about putting this method into RestoRequest, to be available to all subclasses
    def process_json_result(self, json_result: dict) -> RestoRequestResult:
        """
        Method processing the json content of a request, and returning a valid RestoRequestResult.

        :param json_result: response content interpreted as json and represented as a dictionary.
        :returns: a Resto object
        :raises ValueError: when the json response cannot be processed.
        """
        try:
            resto_response = self.resto_response_cls(self, json_result)
        except RestoResponseError:
            msg = 'Response to {} from {} resto server cannot be understood.'
            # TOOD: change exception type and move elsewhere ?
            raise ValueError(msg.format(self.get_server_name()))

        return resto_response.as_resto_object()
