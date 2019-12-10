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
import json
from typing import Optional  # @NoMove


import geojson
from prettytable import PrettyTable

from .resto_license import RestoFeatureLicense


class RestoFeature(geojson.Feature):
    """
     Class representing a Resto feature.
    """

    def __init__(self, feature_descr: dict) -> None:
        """
        Constructor.

        :param feature_descr: Feature description
        :raises ValueError: When Feature type in descriptor is different from 'Feature'
        """
        if feature_descr['type'] != 'Feature':
            raise ValueError('Cannot create a feature whose type is not Feature')
        super(RestoFeature, self).__init__(id=feature_descr['id'],
                                           geometry=feature_descr['geometry'],
                                           properties=feature_descr['properties'])
        self.license = RestoFeatureLicense(feature_descr['properties'])

    @property
    def download_quicklook_url(self) -> str:
        """
        :returns: the quicklook URL
        """
        return self.properties['quicklook']

    @property
    def download_thumbnail_url(self) -> str:
        """
        :returns: the thumbnail url
        """
        return self.properties['thumbnail']

    @property
    def download_annexes_service(self) -> dict:
        """
        :returns: the entire annexes service which was stored in json
        """
        annexes_existence = self.properties.get('annexes') is not None
        return json.loads(self.properties['annexes'])[0] if annexes_existence else None

    @property
    def download_annexes_name(self) -> Optional[str]:
        """
        :returns: the annexes service name
        """
        if self.download_annexes_service is not None:
            return self.download_annexes_service['name']
        return None

    @property
    def download_annexes_url(self) -> Optional[str]:
        """
        :returns: the annexes URL.
        """
        if self.download_annexes_service is not None:
            return self.download_annexes_service['url']
        return None

    @property
    def product_crs(self) -> Optional[str]:
        """
        :returns: the prudct_crs without dictionary
        """
        if self.properties['productCrs'] is not None:
            return json.loads(self.properties['productCrs'])['crs']['properties']['name']
        return None

    @property
    def download_product_service(self) -> dict:
        """
        :returns: the entire download service
        """
        return self.properties['services']['download']

    @property
    def download_product_url(self) -> str:
        """
        :returns: the product URL.
        """
        return self.download_product_service['url']

    @property
    def product_mimetype(self) -> Optional[str]:
        """
        :returns: the product mimetype.
        """
        return self.download_product_service.get('mimeType')

    @property
    def product_size(self) -> Optional[int]:
        """
        :returns: the product size in bytes or None if unavailable.
        """
        prod_size = self.download_product_service.get('size')
        if prod_size is not None:
            prod_size = int(prod_size)
        return prod_size

    @property
    def product_checksum(self) -> Optional[str]:
        """
        :returns: the product checksum.
        """
        return self.download_product_service.get('checksum')

    @property
    def product_identifier(self) -> str:
        """
        :returns: the feature productIdentifier.
        """
        return self.properties['productIdentifier']

    @property
    def storage(self) -> Optional[str]:
        """
        :returns: the product storage.
        """
        if self.properties.get('storage') is not None:
            return self.properties.get('storage').get('mode')
        return None

    def __str__(self) -> str:

        if self.properties is not None:
            result = '\nMetadata available for product {}\n'.format(self.product_identifier)
            exclude_entities = ['links', 'keywords', 'annexes']
            second_entities = ['services']

            feat_table = PrettyTable()
            feat_table.field_names = ['Property', 'Value']
            feat_table.align['Value'] = 'l'
            feat_table.align['Property'] = 'l'

            # Print global property directly seen
            for product_property in self.properties:
                if product_property not in exclude_entities + second_entities:
                    show_param: Optional[str] = str(self.properties[product_property])
                    if product_property == 'description':
                        show_param = str(show_param)[:40] + '[...]'
                    if product_property == 'productCrs':
                        show_param = self.product_crs
                    feat_table.add_row([product_property, show_param])
            result += feat_table.get_string()
            result += '\n'

            # Print additional property englobed in a dictionnary
            for product_property in second_entities:
                result += self._build_second_table(product_property)
                result += '\n'

            # Print annexes property because annexes are stocked in an str
            if self.download_annexes_service is not None:
                annexe_table = PrettyTable()
                annexe_table.field_names = ['Annexes', 'Value']
                annexe_table.add_row(['name', self.download_annexes_name])
                annexe_table.add_row(['url', self.download_annexes_url])
                annexe_table.align['Value'] = 'l'
                annexe_table.align['Annexes'] = 'l'
                result += annexe_table.get_string()
                result += '\n'
            result += str(self.license)
        else:
            result = 'No metadata available for {}'.format(self.product_identifier)

        return result

    def _build_second_table(self, product_property: str) -> str:
        """
        Print the service of the feature
        """
        second_table = PrettyTable()
        second_table.field_names = [product_property, 'Value']
        second_table.align['Value'] = 'l'
        second_table.align[product_property] = 'l'
        for key_head in self.properties[product_property].keys():
            for key, value in self.properties[product_property][key_head].items():
                property_field = '{} : {}'.format(key_head, key)
                if isinstance(value, dict):
                    for key_int, value_int in value.items():
                        property_field = '{} : {} : {}'.format(key_head, key, key_int)
                        second_table.add_row([property_field, value_int])
                else:
                    second_table.add_row([property_field, value])
        return second_table.get_string()
