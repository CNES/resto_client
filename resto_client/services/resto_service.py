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
from pathlib import Path
import time
from typing import Optional, Dict, Type, Any, TYPE_CHECKING
from warnings import warn

from colorama import Fore, Style, colorama_text

from resto_client.base_exceptions import RestoClientDesignError
from resto_client.entities.resto_collection import RestoCollection
from resto_client.entities.resto_collections import RestoCollections
from resto_client.entities.resto_criteria import RestoCriteria, CriteriaDictType
from resto_client.entities.resto_feature import RestoFeature
from resto_client.entities.resto_feature_collection import RestoFeatureCollection
from resto_client.requests.collections_requests import (GetCollectionsRequest, GetCollectionRequest,
                                                        SearchCollectionRequest)
from resto_client.requests.features_requests import (DownloadAnnexesRequest,
                                                     DownloadProductRequest,
                                                     DownloadQuicklookRequest,
                                                     DownloadThumbnailRequest,
                                                     SignLicenseRequest,
                                                     LicenseSignatureRequested,
                                                     FeatureOnTape)
from resto_client.requests.features_requests import DownloadRequestBase  # @UnusedImport
from resto_client.requests.service_requests import DescribeRequest

from .authentication_service import AuthenticationService
from .base_service import BaseService
from .resto_collections_manager import RestoCollectionsManager
from .service_access import RestoServiceAccess

if TYPE_CHECKING:
    from .resto_server import RestoServer  # @UnusedImport


class RestoService(BaseService):
    """
        A Resto Service, i.e. a valid resto accessible server
    """

    def __init__(self,
                 resto_access: RestoServiceAccess,
                 auth_service: AuthenticationService,
                 parent_server: 'RestoServer') -> None:
        """
        Constructor

        :param resto_access: access to resto service.
        :param auth_service: Authentication service associated to this resto service.
        :param parent_server: Server which uses this service.
        """
        super(RestoService, self).__init__(resto_access, auth_service, parent_server)
        self.service_access.detected_protocol = None
        self._collections_mgr = RestoCollectionsManager()
        self._collections_mgr.collections_set = self.get_collections()

    def set_collection_mgr(self, collection_mgr: RestoCollectionsManager) -> None:
        """
        Set the collection manager to use

        :param collection_mgr: the collection manager
        """
        self._collections_mgr = collection_mgr

    @property
    def current_collection(self) -> Optional[str]:
        """
        :returns: The current collection
        """
        return self._collections_mgr.current_collection

    @current_collection.setter
    def current_collection(self, collection_name: str) -> None:
        """
        Set the current collection
        :param collection_name: collection to use
        :raises ValueError: when given collection not in server
        """
        self._collections_mgr.current_collection = collection_name

    def show(self, with_stats: bool=True) -> str:
        """
        :returns: The server description as a tabulated listing
        :param  with_stats: if True the collections statistics are shown.
        """
        out_fmt = 'Server URL: {}\n'
        out_str = out_fmt.format(self.service_access.base_url)
        out_str += str(self._collections_mgr)
        if with_stats:
            out_str += self._collections_mgr.str_statistics()
        return out_str

    def get_supported_criteria(self) -> CriteriaDictType:
        """
        :returns: the supported criteria definition
        """
        return RestoCriteria(self).supported_criteria

# ++++++++ From here we have the requests supported by the service ++++++++++++

    def describe(self) -> RestoCollections:
        """
        :returns: the service description
        """
        return DescribeRequest(self).run()

    def get_collections(self) -> RestoCollections:
        """
        :returns: all the service collections
        """
        return GetCollectionsRequest(self).run()

    def get_collection(self, collection: Optional[str]=None) -> RestoCollection:
        """
        Get a collection description from the resto service.

        :param collection: the name of the collection to retrieve
        :returns: the requested collection or the current one.
        :raises RestoClientUserError: if collection is None and no current collection defined.
        """
        collection_name = self._collections_mgr.ensure_collection(collection)
        return GetCollectionRequest(self, collection=collection_name).run()

    def search_by_criteria(self,
                           criteria: Dict[str, Any],
                           collection: Optional[str]=None) -> RestoFeatureCollection:
        """
        Search a collection using criteria.

        :param criteria: the criteria to use for the search
        :param collection: the name of the collection to search
        :returns: the result of the search
        :raises RestoClientUserError: if collection is None and no current collection defined.
        """
        collection_name = self._collections_mgr.ensure_collection(collection)
        resto_criteria = RestoCriteria(self, **criteria)
        return SearchCollectionRequest(self, collection_name, criteria=resto_criteria).run()

    def get_feature_by_id(self,
                          feature_id: str,
                          collection: Optional[str]=None) -> RestoFeature:
        """
        Get a feature from a collection using its identifier.

        :param feature_id: the feature id (not uuid) to search for
        :param collection: the name of the collection to search
        :returns: the requested feature
        :raises RestoClientUserError: if collection is None and no current collection defined.
        :raises IndexError: when the feature collection does not contain exactly one feature.
        :raises ValueError: when the retrieved feature has not the right id (case where uuid
                            incorrectly provided as argument)
        """
        collection_name = self._collections_mgr.ensure_collection(collection)
        criteria = RestoCriteria(self, identifier=feature_id)

        feature_collection = \
            SearchCollectionRequest(self, collection_name, criteria=criteria).run()

        if len(feature_collection['features']) > 1:
            raise IndexError('Several results found for id {}'.format(feature_id))
        if not feature_collection['features']:
            raise IndexError('No result found for id {}'.format(feature_id))

        feature = feature_collection['features'][0]
        if feature_id not in (feature['properties']['productIdentifier'], feature['id']):
            msg = 'Retrieved feature (id : {} / uuid : {}) inconsistent with requested one ({})'
            raise ValueError(msg.format(feature['properties']['productIdentifier'],
                                        feature['id'], feature_id))
        return feature

    def sign_license(self, license_id: str) -> bool:
        """
        Sign a license onto the resto server.

        :param license_id: the identifier of the licnese to be signed.
        :returns: True if the license signature was successful
        """
        signature = SignLicenseRequest(self, license_id).run()

        if signature:
            with colorama_text():
                print(Fore.BLUE + Style.BRIGHT +
                      'license {} signed successfully'.format(license_id) + Style.RESET_ALL)
        return signature

    DOWNLOAD_REQUEST_CLASSES: Dict[str, Type[DownloadRequestBase]]
    DOWNLOAD_REQUEST_CLASSES = {'product': DownloadProductRequest,
                                'quicklook': DownloadQuicklookRequest,
                                'thumbnail': DownloadThumbnailRequest,
                                'annexes': DownloadAnnexesRequest}

    def download_feature_file(self,
                              feature: RestoFeature,
                              file_type: str,
                              download_dir: Path) -> Optional[str]:
        """
        Download one of the files associated to a feature : product, quicklook, thumbnail, annexes.

        :param feature: the resto feature holding the file file to donwload.
        :param file_type: the type of the file to donwload. Can be one of  'product', 'quicklook',
                          'thumbnail', 'annexes'.
        :param download_dir: the directory where downloaded file must be recorded.
        :returns: the path to the download file.
        :raises RestoClientDesignError: when the file_type is not supported.
        """
        if file_type not in self.DOWNLOAD_REQUEST_CLASSES:
            msg = 'Unexpected file to download : {} can be {}'
            raise RestoClientDesignError(msg.format(file_type,
                                                    self.DOWNLOAD_REQUEST_CLASSES.keys()))

        download_req_cls = self.DOWNLOAD_REQUEST_CLASSES[file_type]
        download_req = download_req_cls(self, feature, download_directory=download_dir)
        # Do download
        try:
            downloaded_filename = download_req.run()
        except LicenseSignatureRequested as excp:
            # Launch request for signing license:
            self.sign_license(excp.error_response.license_to_sign)
            # Retry file download after license signature
            downloaded_filename = self.download_feature_file(feature, file_type, download_dir)
        except FeatureOnTape as excp:
            # Redo_feature to update the storage status
            redo_feature = self.get_feature_by_id(feature.product_identifier)
            warn('Waiting 60 seconds for product transfert...')
            # Wait 60 second
            time.sleep(60)
            # Retry file download after product staging
            downloaded_filename = self.download_feature_file(redo_feature, file_type, download_dir)
        return downloaded_filename
