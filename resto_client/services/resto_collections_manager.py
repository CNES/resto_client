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
from typing import Optional, TYPE_CHECKING

from resto_client.base_exceptions import RestoClientUserError
from resto_client.entities.resto_collections import RestoCollections
from resto_client.generic.property_decoration import managed_getter, managed_setter

from resto_client.settings.resto_client_settings import RESTO_CLIENT_SETTINGS

if TYPE_CHECKING:
    from resto_client.services.resto_service import RestoService  # @UnusedImport


class RestoCollectionsManager():
    """
     Class managing the set of collections of a resto service.
    """

    properties_storage = RESTO_CLIENT_SETTINGS

    def __init__(self, resto_service: 'RestoService') -> None:
        """
        Constructor

        :param resto_service: resto_service onto which these collections are valid
        """
        self._resto_service = resto_service
        self._collections_set = RestoCollections()

    def reset(self) -> None:
        """
        Reset the collections manager to its creation state, and force current collection to None.
        """
        self._collections_set = RestoCollections()
        self.current_collection = None  # type: ignore

    @classmethod
    def persisted(cls, resto_service: 'RestoService') -> 'RestoCollectionsManager':
        """
        Build an instance of a collections manager from persisted attributes (current_collection).

        :param resto_service: resto_service onto which this collections manager applies.
        :returns: the persisted collection manager
        :raises TypeError: if resto_service is not of :class:`RestoService` type.
        """
        instance = cls(resto_service)
        instance.retrieve_collections()
        return instance

    def retrieve_collections(self) -> None:
        """
        Retrieve the collections from the service and set the current collection if possible.
        """
        self._collections_set = self._resto_service.get_collections()
        self._initialize_current_collection()

    def _initialize_current_collection(self) -> None:
        """
        Update the current collection, following a collections update.
        """
        # Retrieve the stored current collection name and check if it is still valid
        previous_current_collection = self.current_collection
        # Retrieve candidate current collection.
        candidate_current_collection = self._collections_set.default_collection
        if candidate_current_collection is None:
            # There is not exactly one collection in the collections.
            try:
                # Try to reuse previous current collection
                self.current_collection = previous_current_collection  # type: ignore
            except RestoClientUserError:
                # Previous current collection is not in the collections. Set current to None.
                self.current_collection = None  # type: ignore
        else:
            # There is exactly 1 collection. Use it as the current.
            self.current_collection = candidate_current_collection  # type: ignore

    def ensure_collection(self, collection: Optional[str]=None) -> None:
        """
        Change the current_collection if a collection is specified

        :param collection: the collection name to record.
        :raises RestoClientUserError: when no current collection can be defined.
        """
        if collection is not None:
            self.current_collection = collection  # type: ignore
        if self.current_collection is None:
            raise RestoClientUserError('No collection currently defined')

    @property  # type: ignore
    @managed_getter()
    def current_collection(self) -> Optional[str]:
        """
        :returns: the name of the current collection
        """

    @current_collection.setter  # type: ignore
    @managed_setter(pre_set_func='_check_current')
    def current_collection(self, collection_name: str) -> None:
        """
        :param collection_name: the name of the collection to set as current.
        """

    def _check_current(self, collection_name: str) -> str:
        """
        Check function used by current collection setter as a callback.

        :param collection_name: the name of the collection to select as current.
        :raises IndexError: if the collection is not found in the set of collections.
        :returns: the collection name translated with the right case to fit an existing collection.
        """
        return self._collections_set.normalize_name(collection_name)

    def __str__(self) -> str:
        return self._collections_set.str_collection_table(annotate=self.current_collection,
                                                          suffix=' [current]')

    def str_statistics(self) -> str:
        """
        :returns: a printout of the statistics of each collections and of the collections set
        """
        return self._collections_set.str_statistics()
