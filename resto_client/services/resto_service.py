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
import time
from warnings import warn
from pathlib import Path
from typing import Optional, Dict, Type

from colorama import Fore, Style, colorama_text

from resto_client.base_exceptions import RestoClientUserError, RestoClientDesignError
from resto_client.entities.resto_collection import RestoCollection
from resto_client.entities.resto_collections import RestoCollections
from resto_client.entities.resto_feature import RestoFeature
from resto_client.entities.resto_feature_collection import RestoFeatureCollection
from resto_client.functions.resto_criteria import RestoCriteria
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
from resto_client.settings.servers_database import DB_SERVERS

from .authentication_service import AuthenticationService
from .base_service import BaseService
from .resto_collections_manager import RestoCollectionsManager
from .service_access import RestoServiceAccess


class RestoService(BaseService):
    """
        A Resto Service, i.e. a valid resto accessible server
    """

    def __init__(self,
                 resto_access: RestoServiceAccess,
                 auth_service: AuthenticationService) -> None:
        """
        Constructor

        :param resto_access: access to resto service.
        :param auth_service: access to the Authentication service associated to this resto service.
        """
        super(RestoService, self).__init__(service_access=resto_access)
        # Collections manager and associated authentication service need to exist before
        # calling update_after_url_change
        self._collections_mgr = RestoCollectionsManager(self)
        self._auth_service = auth_service
        self.update_after_url_change()

    def reset(self) -> None:
        self.service_access.detected_protocol = None
        self._collections_mgr.reset()
        self.auth_service.reset()
        super(RestoService, self).reset()

    def set_collection_mgr(self, collection_mgr: RestoCollectionsManager) -> None:
        """
        Set the collection manager to use

        :param collection_mgr: the collection manager
        """
        self._collections_mgr = collection_mgr

    @property
    def auth_service(self) -> AuthenticationService:
        """
        :returns: the authentication service associated to this RestoService.
        """
        return self._auth_service

    @classmethod
    def from_name(cls,
                  server_name: str,
                  username: Optional[str]= None,
                  password: Optional[str]=None) -> 'RestoService':
        """
        Build a resto service from the database of servers

        :param server_name: the name of the server to use in the database
        :param username: name of the account on the server
        :param password: user password
        :returns: a resto service corresponding to the server_name
        """
        server_description = DB_SERVERS.get_server(server_name)
        auth_service = AuthenticationService.from_name(server_name,
                                                       username=username, password=password)
        resto_service = cls(resto_access=server_description.resto_access, auth_service=auth_service)
        return resto_service

    @classmethod
    def persisted(cls) -> 'RestoService':
        """
        :returns: a resto service from the persisted authentication access description.
        """
        # Retrieve persisted authentication service
        auth_service = AuthenticationService.persisted()
        # Retrieve persisted access to the resto service
        resto_service_access = RestoServiceAccess.get_persisted_access()
        resto_service = cls(resto_access=resto_service_access, auth_service=auth_service)
        persisted_coll_manager = RestoCollectionsManager.persisted(resto_service)
        resto_service.set_collection_mgr(persisted_coll_manager)
        return resto_service

    def update_after_url_change(self) -> None:
        """
        Callback method to update service after base URL was possibly changed.
        """
        # Recreate the collections manager
        self._collections_mgr = RestoCollectionsManager(self)
        if self.service_access.base_url is not None:
            self._collections_mgr.retrieve_collections()
        else:
            self._collections_mgr.current_collection = None  # type: ignore
        # Reset the detected server type
        self.service_access.detected_protocol = None

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
        self._collections_mgr.current_collection = collection_name  # type: ignore

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

# ++++++++ From here we have the supported request to the service ++++++++++++

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
        collection = self._ensure_collection(collection)
        return GetCollectionRequest(self, collection=collection).run()

    def search_collection(self,
                          criteria: RestoCriteria,
                          collection: Optional[str]=None) -> RestoFeatureCollection:
        """
        Search a collection using criteria.

        :param criteria: the criteria to use for the search
        :param collection: the name of the collection to search
        :returns: the result of the search
        :raises RestoClientUserError: if collection is None and no current collection defined.
        """
        collection = self._ensure_collection(collection)
        return SearchCollectionRequest(self, criteria, collection=collection).run()

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
        collection = self._ensure_collection(collection)
        criteria = RestoCriteria(self.service_access.protocol, identifier=feature_id)

        feature_collection = SearchCollectionRequest(self, criteria, collection=collection).run()

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
            # Recursive call to download file
            downloaded_filename = self.download_feature_file(feature, file_type, download_dir)
        except FeatureOnTape as excp:
            # Redo_feature to update the storage status
            redo_feature = self.get_feature_by_id(feature.product_identifier)
            warn('Waiting 60 seconds for product transfert...')
            # Wait 60 second
            time.sleep(60)
            # Recursive call to download file
            downloaded_filename = self.download_feature_file(redo_feature, file_type, download_dir)
        return downloaded_filename

    def _ensure_collection(self, collection: Optional[str]=None) -> str:
        """
        Change the current_collection if a collection is specified and returns the collection to
        use for the request.

        :param collection: the collection name to record.
        :returns: the collection name to use for the request.
        :raises RestoClientUserError: when no current collection can be defined.
        """
        if collection is not None:
            self.current_collection = collection
        if self.current_collection is None:
            raise RestoClientUserError('No collection name defined')
        return self.current_collection
