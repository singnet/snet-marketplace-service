import glob
import json
import os
import tarfile

import ipfsapi
import io

import logging

from common.constant import IPFS_URL
from common.s3_util import S3Util


class IPFSUtil(object):

    def __init__(self, ipfs_url, port):
        self.host = ipfs_url
        self.port = port

    def read_bytesio_from_ipfs(self, ipfs_hash):
        ipfs_conn = ipfsapi.connect(host=self.host, port=self.port)

        ipfs_data = ipfs_conn.cat(ipfs_hash)
        f = io.BytesIO(ipfs_data)
        return f

    def write_file_in_ipfs(self, filepath):
        """
            push a file to ipfs given its path
        """
        ipfs_conn = ipfsapi.connect(host=self.host, port=self.port)
        try:
            with open(filepath, 'r+b') as file:
                result = ipfs_conn.add(
                    file, pin=True, wrap_with_directory=True)
                return result[1]['Hash']+'/'+result[0]['Name']
        except Exception as err:
            logging.error("File error ", err)
        return ''
