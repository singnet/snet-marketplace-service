import json
from enum import EnumMeta, Enum
import os
import tarfile
import tempfile
from typing import List, Tuple, Union
from zipfile import ZipFile

from common.exceptions import BadRequestException
from contract_api.config import IPFS_URL
from contract_api.exceptions import LighthouseInternalException
from common.logger import get_logger

import ipfshttpclient
from lighthouseweb3 import Lighthouse

logger = get_logger(__name__)


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        return any(item == member.value for member in cls)


class StorageProviderType(Enum, metaclass=MetaEnum):
    IPFS = "ipfs"
    FILECOIN = "filecoin"


def get_storage_provider_by_uri(uri: str) -> str:
    if uri.startswith("ipfs://"):
        return StorageProviderType.IPFS.value
    elif uri.startswith("filecoin://"):
        return StorageProviderType.FILECOIN.value
    else:
        return StorageProviderType.IPFS.value


def validate_storage_provider(storage_provider: str) -> StorageProviderType:
    if storage_provider not in StorageProviderType:
        logger.error(f"Invalid storage provider: {storage_provider}")
        raise BadRequestException(f"Invalid storage provider: {storage_provider}")
    return StorageProviderType(storage_provider)


class StorageProvider:
    def __init__(self, lighthouse_token: Union[str, None] = "read_only_token"):
        if lighthouse_token is None or lighthouse_token == "":
            lighthouse_token = "read_only_token"
        self.__ipfs_util = IPFSUtil(IPFS_URL["url"], IPFS_URL["port"])
        self.__lighthouse_client = Lighthouse(lighthouse_token)

    def get(self, metadata_uri: str, to_decode: bool = True) -> Union[dict, bytes]:
        """
        Get metadata json from provider storage rely on metadata_uri prefix

        :param metadata_uri: str, provider storage prefix + hash
        :param to_decode: bool, whether to decode the data
        """
        provider_type, hash_uri = self.uri_to_hash(metadata_uri)
        logger.info(f"Get metadata from provider: {provider_type}, hash: {hash_uri}")

        if provider_type == StorageProviderType.IPFS:
            data_bytes = self.__ipfs_util.read_bytes_from_ipfs(hash_uri)
        elif provider_type == StorageProviderType.FILECOIN:
            data_bytes = self.__lighthouse_client.download(hash_uri)[0]

        if to_decode:
            logger.info(f"Resulting data: data bytes = {data_bytes}, dict = {json.loads(data_bytes.decode('utf-8'))}")
            return json.loads(data_bytes.decode("utf-8"))
        else:
            return data_bytes
 
    def __upload_to_provider(self, file_path: str, provider_type: StorageProviderType) -> str:
        """
        Upload file to the specified storage provider.

        :param file_path: str
        :param provider_type: StorageProviderType, the storage provider type
        :return: str, the URI of the uploaded file
        """
        if provider_type == StorageProviderType.IPFS:
            metadata_hash = self.__ipfs_util.write_file_in_ipfs(file_path)
        elif provider_type == StorageProviderType.FILECOIN:
            try:
                metadata_hash = self.__lighthouse_client.upload(file_path)["data"]["Hash"]
            except Exception as e:
                raise LighthouseInternalException()
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")
        return self.hash_to_uri(metadata_hash, provider_type)

    def publish(self, source: str, provider_type: StorageProviderType, zip_archive: bool = False, ignored_files: List[str] = None) -> str:
        """
        Publish metadata to a specific provider storage.

        :param source: str, file path to metadata JSON file or zip archive
        :param provider_type: StorageProviderType, type of the storage provider (e.g., IPFS, FILECOIN)
        :param zip_archive: bool, flag to indicate whether to publish a zip archive (default is False)
        :param ignored_files: list[str], list of file names to be ignored
        :return: str, the URI of the uploaded metadata
        """
        logger.info(
            f"Publishing file to storage: source = {source}, provider type = {provider_type}, zip_archive = {zip_archive}")
        if zip_archive:
            try:
                temp_tar_path = FileUtils.convert_zip_to_temp_tar(source, ignored_files)
                logger.info(f"temp_tar_path = {temp_tar_path}")
                hash_uri = self.__upload_to_provider(temp_tar_path, provider_type)
                logger.info(f"hash_uri = {hash_uri}")
                return hash_uri
            finally:
                if 'temp_tar_path' in locals() and os.path.exists(temp_tar_path):
                    os.remove(temp_tar_path)
        else:
            hash_uri = self.__upload_to_provider(source, provider_type)
            logger.info(f"hash_uri = {hash_uri}")
            return hash_uri

    def uri_to_hash(self, s: str) -> Tuple[StorageProviderType, str]:
        if s.startswith("ipfs://"):
            return StorageProviderType.IPFS, s[7:]
        elif s.startswith("filecoin://"):
            return StorageProviderType.FILECOIN, s[11:]
        else:
            return StorageProviderType.IPFS, s

    def hash_to_uri(self, metada_hash: str, provider_type: StorageProviderType) -> str:
        if provider_type == StorageProviderType.IPFS:
            metadata_uri = "ipfs://" + metada_hash
        elif provider_type == StorageProviderType.FILECOIN:
            metadata_uri = "filecoin://" + metada_hash

        return metadata_uri


class IPFSUtil:
    def __init__(self, ipfs_url: str, port: str):
        self.ipfs_conn = ipfshttpclient.connect(f"/dns/{ipfs_url}/tcp/{port}/")

    def read_bytes_from_ipfs(self, ipfs_hash: str) -> bytes:
        return self.ipfs_conn.cat(ipfs_hash)

    def write_file_in_ipfs(self, filepath: str, wrap_with_directory: bool=False) -> str:
        """
        Push a file to IPFS given its path.
        """
        try:
            with open(filepath, "r+b") as file:
                result = self.ipfs_conn.add(
                    file, pin=True, wrap_with_directory=wrap_with_directory)
                if wrap_with_directory:
                    return result[1]["Hash"] + "/" + result[0]["Name"]
                return result["Hash"]
        except Exception as err:
            logger.error(f"File error {repr(err)}")
        return ""

    def read_file_from_ipfs(self, ipfs_hash):
        """
        1. Get data from ipfs with ipfs_hash.
        2. Deserialize data to python dict.
        """
        ipfs_data = self.ipfs_conn.cat(ipfs_hash)
        return json.loads(ipfs_data.decode("utf8"))


class FileUtils:
    @staticmethod
    def convert_zip_to_temp_tar(
        zip_path: str,
        exclude_files: List[str] = None,
        include_files: List[str] = None,
    ) -> str:
        """
        Convert a zip archive into a tar file and save it as a temporary file.

        :param zip_path: str, full path to the zip file
        :param exclude_files: list, files to ignore during tar creation (default is None)
        :return: str, path to the temporary tar file
        """

        # Validate the zip file
        if exclude_files is None:
            exclude_files = []
        if include_files is None:
            include_files = []

        if not os.path.isfile(zip_path):
            raise FileNotFoundError(f"Zip file '{zip_path}' does not exist.")

        # Create a temporary tar file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz") as temp_tar:
            tar_path = temp_tar.name

        try:
            # Extract the zip archive to a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                logger.debug(f"Extracting zip file: {zip_path}")
                with ZipFile(zip_path, 'r') as zip_obj:
                    zip_obj.extractall(temp_dir)

                # Create the tar file and write to the temporary tar path
                with tarfile.open(tar_path, mode="w:gz") as tar:
                    for file_path in os.scandir(temp_dir):
                        logger.info(f"Adding file to tar: {file_path}")
                        tar.add(file_path.path, arcname=os.path.basename(file_path), filter=FileUtils.reset)

            return tar_path  # Return the path to the temporary tar file
        except Exception as e:
            # Clean up the temporary tar file if something goes wrong
            if os.path.exists(tar_path):
                os.remove(tar_path)
            raise e

    @staticmethod
    def reset(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo:
        """
        Reset metadata of tarinfo to ensure deterministic output.

        :param tarinfo: tarfile.TarInfo, metadata of a file being added to the tar
        :return: tarfile.TarInfo, updated metadata
        """
        tarinfo.mtime = 123456781234
        return tarinfo

    @staticmethod
    def create_temp_json_file(data: dict) -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(data, temp_file)
            temp_file_name = temp_file.name 
        return temp_file_name