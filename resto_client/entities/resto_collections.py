# -*- coding: utf-8 -*-
"""
.. admonition:: License

   Copyright 2019 CNES

   Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
   in compliance with the License. You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software distributed under the License
   is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
   or implied. See the License for the specific language governing permissions and
   limitations under the License.
"""
from typing import Dict, List, Optional  # @NoMove

from prettytable import PrettyTable

from resto_client.base_exceptions import RestoClientUserError

from .resto_collection import RestoCollection, COLLECTION_FIELDS_NAMES


class RestoCollections():
    """
     Class containing the description of a set of collections as well as their synthesis.

     This class has no knowledge of the current collection concept.
     See :class:`~resto_client.services.resto_collections_manager.RestoCollectionsManager`
     for this topic.
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self._synthesis: Optional[RestoCollection] = None
        self._collections: Dict[str, RestoCollection] = {}

    def add(self, collection: RestoCollection) -> None:
        """
        Add a new collection in this collections set.

        :param collection: a collection to add in this set of collections.
        :raises TypeError: if collection is not of the right type.
        :raises IndexError: if a collection with same name already exists in the set of collections.
        :raises NotImplementedError: when a collection already exists with same lowercased name.
        """
        if not isinstance(collection, RestoCollection):
            msg_err = 'collection argument must be of RestoCollection type. Found {} instead.'
            raise TypeError(msg_err.format(type(collection)))
        # FIXME: use self.normalize_name
        if collection.name in self._collections:
            raise IndexError('A collection with name {} already exists.'.format(collection.name))
        if collection.name is None:
            raise IndexError('Cannot add a collection without knowing its name.')
        if collection.name.lower() in self._lowercase_names:
            msg_err = 'Cannot add a collection {} with already existing name when lowercased!! : {}'
            raise NotImplementedError(msg_err.format(collection.name, self.names))
        self._collections[collection.name] = collection

    def get_collections(self) -> Dict[str, RestoCollection]:
        """
        :returns: the collections defined in this set of collections.
        """
        return self._collections

    @property
    def synthesis(self) -> Optional[RestoCollection]:
        """
        :returns: the synthesis of this set of collections.
        """
        return self._synthesis

    @synthesis.setter
    def synthesis(self, synthesis: Optional[RestoCollection]) -> None:
        """
        :param synthesis: the synthesis of this set of collections.
        :raises TypeError: if synthesis is not of the right type.
        """
        if not isinstance(synthesis, (RestoCollection, type(None))):
            msg_err = 'synthesis must be None or of RestoCollection type. Found {} instead.'
            raise TypeError(msg_err.format(type(synthesis)))
        self._synthesis = synthesis

    @property
    def names(self) -> List[str]:
        """
        :returns: the names of the collections available in this collections set.
        """
        return list(self._collections.keys())

    @property
    def _lowercase_names(self) -> List[str]:
        """
        :returns: the lowercase names of the collections available in this collections set.
        """
        return [name.lower() for name in self.names]

    def normalize_name(self, collection_name: str) -> str:
        """
        Returns the collection name with case adapted to fit an existing collection.

        :param collection_name: the name of the collection whose name must be normalized.
        :raises RestoClientUserError: if the collection is not found in the set of collections.
        :returns: the collection name translated with the right case to fit an existing collection.
        """
        lowercase_collection_name = collection_name.lower()
        if lowercase_collection_name not in self._lowercase_names:
            raise RestoClientUserError('No collection found with name {}'.format(collection_name))
        normalized_name_index = self._lowercase_names.index(lowercase_collection_name)
        return self.names[normalized_name_index]

    @property
    def default_collection(self) -> Optional[str]:
        """
        :returns: the name of the default collection (None if not exactly 1 collection)
        """
        return None if len(self.names) != 1 else self.names[0]

    def str_statistics(self) -> str:
        """
        :returns: the statistics of each collections and of the collections set.
        """
        out_str = ''
        for collection in self._collections.values():
            out_str += '\n' + str(collection.statistics)
        if self.synthesis is not None:
            out_str += str(self.synthesis.statistics)
        else:
            out_str += 'No synthesis statistics./n'
        return out_str

    def str_collection_table(self, annotate: Optional[str]=None, suffix: str='') -> str:
        """
        :param annotate: name of a collection which must be annotated with the provided suffix.
        :param suffix: suffix to put at the end of the specified annotated collection name.
        :returns: a table listing all the collections with one of them possibly annotated
        :raises ValueError: when annotate does not correspond to a known collection name.
        """
        if annotate is not None and annotate not in self.names:
            msg_err = 'Unknown collection to annotate: {}. Known collections: {}'
            raise ValueError(msg_err.format(annotate, self.names))
        collections_table = PrettyTable()
        collections_table.field_names = COLLECTION_FIELDS_NAMES
        for collection in self._collections.values():
            collection_fields = collection.get_table_row()
            if collection_fields[0] == annotate:
                if collection_fields[0] is not None:
                    collection_fields[0] += suffix
            collections_table.add_row(collection_fields)
        return collections_table.get_string()
