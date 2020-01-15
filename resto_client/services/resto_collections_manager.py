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

from resto_client.base_exceptions import RestoClientUserError, RestoClientDesignError
from resto_client.entities.resto_collections import RestoCollections


class RestoCollectionsManager():
    """
     Class managing the set of collections of a resto service.
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self._collections_set: Optional[RestoCollections] = None
        self._current_collection: Optional[str] = None

    @property
    def collections_set(self) -> Optional[RestoCollections]:
        """
        :returns: the set of collections associated to this collection manager.
        """
        return self._collections_set

    @collections_set.setter
    def collections_set(self, collections: Optional[RestoCollections] = None) -> None:
        if collections is None:
            # Caller wants to reset this collections manager to its creation state
            self._collections_set = None
            self.current_collection = None
        else:
            self._collections_set = collections
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

    @property
    def current_collection(self) -> Optional[str]:
        """
        :returns: the name of the current collection
        :raises RestoClientDesignError: when trying to set a current collection with no collections
                                        set defined.
        """
        return self._current_collection

    @current_collection.setter
    def current_collection(self, collection_name: Optional[str] = None) -> None:
        if collection_name is not None:
            if self.collections_set is None:
                msg = 'Cannot set a current collection when there is no collections set'
                raise RestoClientDesignError(msg)
            collection_name = self.collections_set.normalize_name(collection_name)
        self._current_collection = collection_name

    def ensure_collection(self, collection: Optional[str]=None) -> str:
        """
        Change the current_collection if a collection is specified

        :param collection: the collection name to record.
        :returns: the collection name to use
        :raises RestoClientUserError: when no current collection can be defined.
        """
        if collection is not None:
            self.current_collection = collection
        if self.current_collection is None:
            raise RestoClientUserError('No collection currently defined')
        return self.current_collection

    def __str__(self) -> str:
        if self.collections_set is None:
            return 'No collections recorded in this collections manager'
        return self.collections_set.str_collection_table(annotate=self.current_collection,
                                                         suffix=' [current]')

    def str_statistics(self) -> str:
        """
        :returns: a printout of the statistics of each collections and of the collections set
        """
        if self.collections_set is None:
            return 'No collections recorded in this collections manager'
        return self.collections_set.str_statistics()
