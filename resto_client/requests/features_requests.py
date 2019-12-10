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
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple, Union, TYPE_CHECKING  # @NoMove
from warnings import warn
import tempfile

from resto_client.base_exceptions import RestoClientDesignError
from resto_client.entities.resto_feature import RestoFeature
from resto_client.responses.download_error_response import DownloadErrorResponse
from resto_client.responses.resto_response_error import RestoResponseError
from resto_client.responses.sign_license_response import SignLicenseResponse
from resto_client.functions.utils import get_file_properties

from .anonymous_request import AnonymousRequest
from .authentication_required_request import AuthenticationRequiredRequest
from .utils import RestrictedProductError, download_file, get_response

if TYPE_CHECKING:
    from resto_client.services.resto_service import RestoService  # @UnusedImport


class LicenseSignatureRequested(RestoResponseError):
    """
    Exception raised when a license signature is requested before proceeding with the download.
    """

    def __init__(self, error_response: DownloadErrorResponse) -> None:
        """
        Constructor.

        :param error_response: the error response as provided by resto, which contains the
                               identifier of the license to sign.
        """
        super(LicenseSignatureRequested, self).__init__('user needs to sign a license')
        self.error_response = error_response


class FeatureOnTape(RestoResponseError):
    """
    Exception raised when a product requested is on tape
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        super(FeatureOnTape, self).__init__('Moving feature from tape to disk')


class SignLicenseRequest(AuthenticationRequiredRequest):
    """
     Requests for signing a license
    """
    request_action = 'signing license'

    def __init__(self, service: 'RestoService', license_id: str) -> None:
        """
        Constructor

        :param service: resto service
        :param license_id: the license id which must be signed
        """
        self._license_id = license_id
        super(SignLicenseRequest, self).__init__(service,
                                                 user=service.auth_service.credentials.username_b64,
                                                 license_id=license_id)

    def run(self) -> bool:
        """
         Sign the license of a license_id product

         :returns: True if the license has been signed
         :raises RestoResponseError: when license signature was not accepted.
        """

        self.set_headers({'Accept': 'application/json'})
        result = self.post()
        response = SignLicenseResponse(self, result.json())

        if not response.is_signed:
            msg = 'Unable to sign license {}. Reason : {}'
            raise RestoResponseError(msg.format(self._license_id, response.validation_message))

        return response.as_resto_object()


class DownloadRequestBase(ABC):
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
                 download_directory: Path,
                 headers: dict) -> None:
        """
        Constructor

        :param service: resto service
        :param  feature: resto feature
        :param download_directory: an existing directory path where download will occur
        :param headers: dict for header to send in get_response
        """
        self._feature = feature
        self._service = service
        self._headers = headers

        # product specific initialization
        self._url_to_download = getattr(self._feature, 'download_{}_url'.format(self.file_type))
        self._download_directory = download_directory

    def get_filename(self, content_type: str) -> Tuple[str, Path, str, Union[str, None]]:
        """
        Returns filename and full filename according to the content type.

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

    def run(self) -> Optional[str]:
        """
         Download one of the different files available for a feature.

        :returns: the name of the downloaded file
        :raises RestoResponseError: when the response does not have one of the expected contents.
        :raises RestrictedProductError: when the product exists but cannot be downloaded.
        :raises LicenseSignatureRequested: when download is rejected because license must be signed
        """
        # If there is no file to download
        if self._url_to_download is None:
            msg = 'There is no {} to download for product {}.'
            warn(msg.format(self.file_type, self._feature.product_identifier))
            return None

        if self.file_type == 'product':
            if self._service.service_access.protocol == 'theia_version':
                self._url_to_download += "/?issuerId=theia"

        result = get_response(self._url_to_download, 'processing {} request'.format(self.file_type),
                              headers=self._headers, stream=True)
        content_type = result.headers.get('content-type')
        print(result.headers)

        if content_type == 'application/json':
            dict_json = result.json()
            try:
                error_response = DownloadErrorResponse(self, dict_json).as_resto_object()
            except RestoResponseError as excp:
                # Unexpected json content
                msg_fmt = 'Cannot process json when downloading {} feature\nJson content:\n{}'
                msg = msg_fmt.format(self._feature.product_identifier, dict_json)
                raise RestoResponseError(msg) from excp
            if error_response.download_need_license_signature:
                # user needs to sign a license for this product
                raise LicenseSignatureRequested(error_response)
            if error_response.download_forbidden:
                msg = 'User does not have permission to download {}'
                raise RestrictedProductError(msg.format(self._feature.product_identifier))

        if content_type is None:
            raise RestoResponseError('Cannot infer file extension with None content-type')

        file_name, full_file_path, file_mimetype, _ = self.get_filename(content_type)

        if file_mimetype in ('image/jpeg', 'text/html', 'image/png'):
            # If it's a product on tape
            if self.file_type == 'product' and self._feature.storage == 'tape':
                warn("Your product is on tape, launching request to trigger"
                     " its copy on disk on server side.")
                # Launch a download request for copying from tape to disk on server side.
                # However download will not happen.
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tmp_file_path = Path(tmp_dir) / file_name
                    download_file(result, tmp_file_path)
                raise FeatureOnTape()
            # If it's a product waiting to be on disk
            if self.file_type == 'product' and self._feature.storage == 'staging':
                warn("Your product is currently being copied to disk on server side."
                     "Try again later.")
                raise FeatureOnTape()
            # If it's a Quicklook, Thumbnail or annexes
            download_file(result, full_file_path)
        # If it's a product
        elif content_type == self._feature.product_mimetype:
            download_file(result, full_file_path, file_size=self._feature.product_size)
        else:
            msg = 'Unexpected content-type {} when downloading {}.'
            raise RestoResponseError(msg.format(content_type, self._feature.product_identifier))

        # Download finished. Return the filename where download has been made.
        return file_name


class DownloadProductRequest(AuthenticationRequiredRequest, DownloadRequestBase):
    """
     Request for downloading the product file
    """
    file_type = 'product'
    filename_suffix = ''
    request_action = 'downloading product'

    def __init__(self,
                 service: 'RestoService',
                 feature: RestoFeature,
                 download_directory: Path) -> None:
        """
        Constructor

        :param service: resto service
        :param  feature: resto feature
        :param download_directory: directory where to download the file
        """
        AuthenticationRequiredRequest.__init__(self, service)
        self.set_headers()
        DownloadRequestBase.__init__(self, service, feature, download_directory, self.headers)

    def run(self) -> Optional[str]:
        """
         Download the product file.

        :returns: the name of the downloaded file
        """
        return DownloadRequestBase.run(self)


class DownloadQuicklookRequest(AnonymousRequest, DownloadRequestBase):
    """
     Request for downloading the quicklook file
    """
    file_type = 'quicklook'
    filename_suffix = '_ql'
    request_action = 'downloading quicklook'

    def __init__(self,
                 service: 'RestoService',
                 feature: RestoFeature,
                 download_directory: Path) -> None:
        """
        Constructor

        :param service: resto service
        :param  feature: resto feature
        :param download_directory: directory where to download the file
        """
        AnonymousRequest.__init__(self, service)
        self.set_headers()
        DownloadRequestBase.__init__(self, service, feature, download_directory, self.headers)

    def run(self) -> Optional[str]:
        """
         Download the quicklook file.

        :returns: the name of the downloaded file
        """
        return DownloadRequestBase.run(self)


class DownloadThumbnailRequest(AnonymousRequest, DownloadRequestBase):
    """
     Request for downloading the thumbnail file
    """
    file_type = 'thumbnail'
    filename_suffix = '_th'
    request_action = 'downloading thumbnail'

    def __init__(self,
                 service: 'RestoService',
                 feature: RestoFeature,
                 download_directory: Path) -> None:
        """
        Constructor

        :param service: resto service
        :param  feature: resto feature
        :param download_directory: directory where to download the file
        """
        AnonymousRequest.__init__(self, service)
        self.set_headers()
        DownloadRequestBase.__init__(self, service, feature, download_directory, self.headers)

    def run(self) -> Optional[str]:
        """
         Download the thumbnail file.

        :returns: the name of the downloaded file
        """
        return DownloadRequestBase.run(self)


class DownloadAnnexesRequest(AnonymousRequest, DownloadRequestBase):
    """
     Request for downloading the annexes file
    """
    file_type = 'annexes'
    filename_suffix = '_ann'
    request_action = 'downloading annexes'

    def __init__(self,
                 service: 'RestoService',
                 feature: RestoFeature,
                 download_directory: Path) -> None:
        """
        Constructor

        :param service: resto service
        :param  feature: resto feature
        :param download_directory: directory where to download the file
        """
        AnonymousRequest.__init__(self, service)
        self.set_headers()
        DownloadRequestBase.__init__(self, service, feature, download_directory, self.headers)

    def run(self) -> Optional[str]:
        """
         Download the annexes file.

        :returns: the name of the downloaded file
        """
        return DownloadRequestBase.run(self)
