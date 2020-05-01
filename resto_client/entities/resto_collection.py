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
import copy
from typing import List, Optional, Union  # @UnusedImport @NoMove

from prettytable import PrettyTable

from .resto_license import RestoCollectionLicense
from .resto_statistics import RestoStatistics


class RestoCollection():
    """
     Class representing a Resto collection
    """

    def __init__(self, collection_descr: dict) -> None:
        """
        Constructor

        :param collection_descr: description of the collection
        """
        self._collection_descr = copy.deepcopy(collection_descr)
        self.license = RestoCollectionLicense(self._collection_descr)
        if 'statistics' in self._collection_descr:
            stats_field: Union[dict, list] = self._collection_descr['statistics']
            if isinstance(stats_field, list):
                if not stats_field:
                    self.statistics = RestoStatistics(None, self.name)
            else:
                self.statistics = RestoStatistics(stats_field, self.name)
            del self._collection_descr['statistics']
        else:
            self.statistics = RestoStatistics(None, self.name)

    @property
    def name(self) -> Optional[str]:
        """
        :returns: the collection's name
        """
        if self._collection_descr.get('name') == '*':
            return 'all collections'
        return self._collection_descr.get('name')

    @property
    def status(self) -> Optional[str]:
        """
        :returns: the collection's status """
        return self._collection_descr.get('status')

    @property
    def model(self) -> Optional[str]:
        """
        :returns: the collection's model
        """
        return self._collection_descr.get('model')

    @property
    def open_search_description(self) -> Optional[dict]:
        """
        :returns: the open search collection's description
        """
        return self._collection_descr.get('osDescription')

    """
    {'osDescription': {'fr': {'ShortName': 'KALIDEOS CNES',
                             'LongName': 'Kalideos CNES',
                             'Description': 'Collection de Kalideos CNES',
                             'Tags': '',
                             'Developper': 'Jérôme Gasperi',
                             'Contact': 'arnaud.selle@cnes.fr',
                             'Query': 'Images de la base Kalideos CNES',
                             'Attribution': 'CNES. Copyright 2016, All Rights Reserved'},
                    'en': {'ShortName': 'KALIDEOS CNES',
                           'LongName': 'Kalideos CNES',
                           'Description': 'Kalideos CNES Collection',
                           'Tags': '',
                           'Developper': 'Jérôme Gasperi',
                           'Contact': 'arnaud.selle@cnes.fr',
                           'Query': 'Images of Kalideos CNES database',
                           'Attribution': 'CNES. Copyright 2016, All Rights Reserved'}
                           },
        }

    """

    table_field_names = ['Collection name', 'Status', 'Model', 'License Id', 'License name']

    def get_table_row(self) -> List[Optional[str]]:
        """
        :returns: attributes to be displayed in the tabulated dump of a collection
        """
        return [self.name, self.status, self.model,
                self.license.identifier, self.license.short_name]

    def __str__(self) -> str:
        collection_table = PrettyTable()
        collection_table.title = "Collection's Characteristics"
        collection_table.field_names = self.table_field_names
        collection_table.add_row(self.get_table_row())
        return collection_table.get_string()
