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
import json
from pathlib import Path
from typing import Optional  # @NoMove

from prettytable import PrettyTable


class DictSettingsJson(dict):
    """
    A dictionary holding settings which can be read and written as json.
    """

    def __init__(self, filepath: Path, defaults: Optional[dict]=None) -> None:
        """
        :param filepath: path to the json file where the settings are stored.
        :param defaults: a dictionary of entries to store in the settings if no file found.
        """
        super(DictSettingsJson, self).__init__()
        self.filepath = filepath
        # Read the settings from the associated json file.
        try:
            with open(self.filepath, 'r') as file_desc:
                new_dict = json.load(file_desc)
        except FileNotFoundError:
            new_dict = defaults if defaults is not None else {}
        self.update(new_dict)

    def __str__(self) -> str:
        settings_table = PrettyTable()
        settings_table.title = 'Settings from : {}'.format(self.filepath.name)
        settings_table.field_names = ['Entry', 'Value']
        settings_table.add_row(['Settings saved in', self.filepath.parent])
        for params, value in self.items():
            if params == 'token':
                value = value[:10] + '[...]' + value[-10:]
            settings_table.add_row([params, value])
        return settings_table.get_string()

    def save(self) -> None:
        """
        Save the settings in the associated json file.
        """
        with open(self.filepath, 'w') as file_desc:
            json.dump(self, file_desc)
