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
from typing import Optional, Union  # @NoMove

from prettytable import PrettyTable


class RestoStatistics():  # pylint: disable=too-few-public-methods
    """
     Class representing statistics on a Resto collection or on a set of collections
    """

    def __init__(self,
                 statistics_descr: Union[dict, None],
                 parent: Optional[str]='unknown collection(s)') -> None:
        """
        Constructor

        :param statistics_descr: description of the statistics
        :param parent: name of the collection or set of collections for these statistics. Default:
                       `'unknown collection(s)'`
        """
        self._statistics_descr = statistics_descr
        if self._statistics_descr is not None and 'facets' in self._statistics_descr:
            self._statistics_descr = self._statistics_descr['facets']
        self._parent = parent

    def __str__(self) -> str:
        if self._statistics_descr is not None:
            result = '\nSTATISTICS for {}\n'.format(self._parent)
            for stat_group in self._statistics_descr:
                stat_table = PrettyTable()
                stat_table.field_names = [stat_group, 'Nb products']
                stat_table.align[stat_group] = 'l'
                stat_table.align['Nb products'] = 'r'
                group_count = 0
                for stat_item, count in self._statistics_descr[stat_group].items():
                    stat_table.add_row([stat_item, count])
                    group_count += count
                stat_table.add_row(['Total', group_count])
                result += stat_table.get_string()
                result += '\n'
        else:
            result = 'No statistics available for {}'.format(self._parent)
        return result
