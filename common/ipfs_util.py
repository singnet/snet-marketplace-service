import io
import json
import logging

import ipfshttpclient


class IPFSUtil(object):

    def __init__(self, ipfs_url, port):
        self.ipfs_conn = ipfshttpclient.connect(f"/dns/{ipfs_url}/tcp/{port}/http")

    def read_bytesio_from_ipfs(self, ipfs_hash):
        ipfs_data = self.ipfs_conn.cat(ipfs_hash)
        f = io.BytesIO(ipfs_data)
        return f

    def write_file_in_ipfs(self, filepath, wrap_with_directory=True):
        """
            Push a file to IPFS given its path.
        """
        try:
            with open(filepath, 'r+b') as file:
                result = self.ipfs_conn.add(
                    file, pin=True, wrap_with_directory=wrap_with_directory)
                if wrap_with_directory:
                    return result[1]['Hash'] + '/' + result[0]['Name']
                return result['Hash']
        except Exception as err:
            logging.error(f"File error {repr(err)}")
        return ''

    def read_file_from_ipfs(self, ipfs_hash):
        """
            1. Get data from ipfs with ipfs_hash.
            2. Deserialize data to python dict.
        """
        ipfs_data = self.ipfs_conn.cat(ipfs_hash)
        return json.loads(ipfs_data.decode('utf8'))
