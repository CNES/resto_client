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
from abc import abstractmethod
from pathlib import Path
import tempfile
from warnings import warn

from typing import Optional, Tuple, Union, TYPE_CHECKING, cast  # @NoMove
from tqdm import tqdm

from resto_client.base_exceptions import (RestoClientDesignError,
                                          RestoResponseError,
                                          FeatureOnTape, LicenseSignatureRequested,
                                          IncomprehensibleResponse,
                                          AccessDeniedError)
from resto_client.entities.resto_feature import RestoFeature
from resto_client.functions.utils import get_file_properties
from resto_client.responses.download_error_response import DownloadErrorResponse
from resto_client.responses.sign_license_response import SignLicenseResponse
from resto_client.services.service_access import RestoClientUnsupportedRequest
from resto_client.settings.resto_client_config import resto_client_print

from .base_request import BaseRequest
from .resto_json_request import RestoJsonRequest


if TYPE_CHECKING:
    from resto_client.services.resto_service import RestoService  # @UnusedImport


class RestrictedProductError(AccessDeniedError):
    """
    Exception used when a product exist but cannot be downloaded
    """


class SignLicenseRequest(RestoJsonRequest):
    """
     Requests for signing a license
    """
    request_action = 'signing license'
    resto_response_cls = SignLicenseResponse

    def __init__(self, service: 'RestoService', license_id: str) -> None:
        """
        Constructor

        :param service: resto service
        :param license_id: the license id which must be signed
        """
        super(SignLicenseRequest, self).__init__(service,
                                                 user=service.auth_service.username_b64,
                                                 license_id=license_id)

    def run(self) -> SignLicenseResponse:
        # overidding BaseRequest method, in order to specify the right type returned by this request
        return cast(SignLicenseResponse, super(SignLicenseRequest, self).run())


class DownloadRequestBase(BaseRequest):
    """
     Base class for all file download requests downloading in the client download directory
    """

    @property
    @abstractmethod
    def filename_suffix(self) -> str:
        """
        :returns: a file type specific suffix to add before the extension in the filename.
        """

    @property
    @abstractmethod
    def file_type(self) -> str:
        """
        :returns: file type: one of 'product', 'quicklook', 'thumbnail' or 'annexes'
        """

    def __init__(self,
                 service: 'RestoService',
                 feature: RestoFeature,
                 download_directory: Path) -> None:
        """
        Constructor

        :param service: resto service
        :param  feature: resto feature
        :param download_directory: an existing directory path where download will occur
        """
        self._feature = feature

        super(DownloadRequestBase, self).__init__(service=service)
        # product specific initialization
        self._url_to_download = self._feature.get_download_url(self.file_type)

        if self.file_type == 'product':
            if self.parent_service.get_protocol() == 'theia_version':
                self._url_to_download += "/?issuerId=theia"
        self._download_directory = download_directory

    def run(self) -> RestoFeature:
        # overidding BaseRequest method, in order to specify the right type returned by this request
        return cast(RestoFeature, super(DownloadRequestBase, self).run())

    def get_file_infos(self, content_type: str) -> Tuple[str, Path, str, Union[str, None]]:
        """
        Returns filename, full filename, mimetype and encoding according to the content type.

        :param content_type: mimetype of the file to download
        :returns: filename and full file path of the file to record
        :returns: mimetype of the file to record
        :returns: encoding of the file to record if given else None
        :raises RestoClientDesignError: when extension cannot be guessed from mimetype.
        """
        extension, mimetype, encoding = get_file_properties(content_type.strip())
        if extension is None:
            msg_excp = 'cannot guess the file extension from mimetype: {}'
            raise RestoClientDesignError(msg_excp.format(mimetype))
        if extension.lower() == '.jpe':
            extension = '.jpg'

        # TODO: isolate this part in a generic function
        filename = '{}{}{}'.format(self._feature.product_identifier,
                                   self.filename_suffix, extension)
        full_file_path = self._download_directory / filename

        if full_file_path.is_file():
            count = 1
            while full_file_path.is_file():
                filename = '{}{}[{}]{}'.format(self._feature.product_identifier,
                                               self.filename_suffix, count, extension)
                full_file_path = self._download_directory / filename
                count += 1

        return filename, full_file_path, mimetype, encoding

    def finalize_request(self) -> None:
        try:
            super(DownloadRequestBase, self).finalize_request()
        except RestoClientUnsupportedRequest:
            # Nominal case as url for download is contained in the feature
            pass

    def get_url(self) -> str:
        """
        :returns: full url for this feature file download request
        """
        return self._url_to_download

    def process_request_result(self) -> RestoFeature:
        """
         Download one of the different files available for a feature.

        :returns: the downloaded RestoFeature updated with the downloaded_files_paths
        :raises IncomprehensibleResponse: the response does not have one of the expected contents.
        :raises RestrictedProductError: when the product exists but cannot be downloaded.
        :raises LicenseSignatureRequested: when download is rejected because license must be signed
        :raises FeatureOnTape: when the feature file is on tape and not available for download
        """
        content_type = self._request_result.headers.get('content-type')

        if content_type == 'application/json':
            dict_json = self._request_result.json()
            try:
                error_response = DownloadErrorResponse(self, dict_json).as_resto_object()
            except RestoResponseError as excp:
                # Unexpected json content
                msg_fmt = 'Cannot process json when downloading {} feature\nJson content:\n{}'
                msg = msg_fmt.format(self._feature.product_identifier, dict_json)
                raise IncomprehensibleResponse(msg) from excp
            if error_response.download_need_license_signature:
                # user needs to sign a license for this product
                raise LicenseSignatureRequested(error_response)
            if error_response.download_forbidden:
                msg = 'User does not have permission to download {}'
                raise RestrictedProductError(msg.format(self._feature.product_identifier))

        if content_type is None:
            raise IncomprehensibleResponse('Cannot infer file extension with None content-type')

        file_name, full_file_path, file_mimetype, _ = self.get_file_infos(content_type)

        if file_mimetype in ('image/jpeg', 'text/html', 'image/png'):
            # If it's a product on tape
            if self.file_type == 'product' and self._feature.storage == 'tape':
                warn("Your product is on tape, launching request to trigger"
                     " its copy on disk on server side.")
                # Launch a download request for copying from tape to disk on server side.
                # However download will not happen.
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tmp_file_path = Path(tmp_dir) / file_name
                    self.download_file(tmp_file_path)
                raise FeatureOnTape()
            # If it's a product waiting to be on disk
            if self.file_type == 'product' and self._feature.storage == 'staging':
                warn("Your product is currently being copied to disk on server side."
                     "Try again later.")
                raise FeatureOnTape()
            # If it's a Quicklook, Thumbnail or annexes
            self.download_file(full_file_path)
        # If it's a product
        elif content_type == self._feature.product_mimetype:
            self.download_file(full_file_path, file_size=self._feature.product_size)
        else:
            msg = 'Unexpected content-type {} when downloading {}.'
            raise IncomprehensibleResponse(msg.format(content_type,
                                                      self._feature.product_identifier))

        # Download finished. Write the file path where download has been made and
        # return updated feature
        self._feature.downloaded_files_paths[self.file_type] = full_file_path
        return self._feature

    def download_file(self, file_path: Path, file_size: Optional[int]=None) -> None:
        """
        method called when we know that we have a file to download
        iterate a result created with GET with stream option and write it directly in a file
        """
        resto_client_print('downloading file: {}'.format(file_path))
        # Get and Save the result's size if not given
        if file_size is None:
            file_size = int(self._request_result.headers.get('content-length', 0))

        block_size = 1024

        with open(file_path, 'wb') as file_desc:
            # do iteration with progress bar using tqdm
            progress_bar = tqdm(unit="B", total=file_size, unit_scale=True, desc='Downloading')
            for block in self._request_result.iter_content(block_size):
                progress_bar.update(len(block))
                file_desc.write(block)


class DownloadProductRequest(DownloadRequestBase):
    """
     Request for downloading the product file
    """
    file_type = 'product'
    filename_suffix = ''
    request_action = 'downloading product'


class DownloadQuicklookRequest(DownloadRequestBase):
    """
     Request for downloading the quicklook file
    """
    file_type = 'quicklook'
    filename_suffix = '_ql'
    request_action = 'downloading quicklook'


class DownloadThumbnailRequest(DownloadRequestBase):
    """
     Request for downloading the thumbnail file
    """
    file_type = 'thumbnail'
    filename_suffix = '_th'
    request_action = 'downloading thumbnail'


class DownloadAnnexesRequest(DownloadRequestBase):
    """
     Request for downloading the annexes file
    """
    file_type = 'annexes'
    filename_suffix = '_ann'
    request_action = 'downloading annexes'
