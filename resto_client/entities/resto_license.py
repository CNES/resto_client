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
from prettytable import PrettyTable


class RestoLicense(dict):
    """
     Class representing a license as given by Resto, either on a collection or on a feature
    """

    def __init__(self, item_description: dict) -> None:
        """
        Constructor.

        :param item_description: feature properties or collection item into which license
                                 information can be found.
        """
        super(RestoLicense, self).__init__()
        license_entry = item_description.get('license')
        license_info = item_description.get('license_info')
        self._license_infos: dict
        if license_entry is None or license_info is not None:
            self._license_infos = {'description': {'shortName': 'No license'},
                                   'grantedCountries': None,
                                   'grantedFlags': None,
                                   'grantedOrganizationCountries': None,
                                   'hasToBeSigned': 'never',
                                   'licenseId': 'unlicensed',
                                   'signatureQuota': -1,
                                   'viewService': 'public'}
            if license_info is not None:
                for key, value in license_info.items():
                    self._license_infos['description'][key] = value
                if 'en' in license_info:
                    self._license_infos['description']['shortName'] = \
                        license_info['en']['short_name']
                elif 'fr' in license_info:
                    self._license_infos['description']['shortName'] = \
                        license_info['fr']['short_name']
                else:
                    self._license_infos['description']['shortName'] = 'Undefined'
                self._license_infos['licenseId'] = license_entry
        else:
            self._license_infos = license_entry

        # Remove license information from item_description
        RestoLicense._clean_license_in_item(item_description)
        self.update(self._license_infos)

    @staticmethod
    def _clean_license_in_item(item_description: dict) -> None:
        """
        Remove license information from item_description

        :param item_description: feature properties or collection item into which license
                                 information is stored.
        """
        if 'license' in item_description:
            del item_description['license']
        if 'license_info' in item_description:
            del item_description['license_info']

    @property
    def short_name(self) -> str:
        """
        :returns: the license short name, in english
        """
        return self._license_infos['description']['shortName']

    @property
    def identifier(self) -> str:
        """
        :returns: the license identifier
        """
        return self._license_infos['licenseId']
    
    def __str__(self) -> str:
        license_table = PrettyTable()
        if isinstance(self, RestoCollectionLicense):
            license_table.title = 'Collection license'
        else:
            license_table.title = 'Feature license'
        license_table.field_names = ['License field', 'Value']
        license_table.align['Value'] = 'l'
        license_table.align['License field'] = 'l'
        for key1, value1 in self._license_infos.items():
            property_field1 = str(key1)
            if isinstance(value1, dict):
                for key2, value2 in value1.items():
                    property_field2 = (property_field1 + ' : {}').format(key2)
                    if isinstance(value2, dict):
                        for key3, value3 in value2.items():
                            property_field3 = (property_field2 + ' : {}').format(key3)
                            license_table.add_row([property_field3, value3])
                    else:
                        license_table.add_row([property_field2, value2])
            else:
                license_table.add_row([property_field1, value1])
        return license_table.get_string()


class RestoCollectionLicense(RestoLicense):
    """
     Class representing a license associated to a collection.
    """


class RestoFeatureLicense(RestoLicense):
    """
     Class representing a license associated to a feature
    """
