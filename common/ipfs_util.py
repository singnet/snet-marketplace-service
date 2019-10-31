import ipfsapi
import io
import logging
import json


class IPFSUtil(object):

    def __init__(self, ipfs_url, port):
        self.ipfs_conn = ipfsapi.connect(host=ipfs_url, port=port)

    def read_bytesio_from_ipfs(self, ipfs_hash):

        ipfs_data = self.ipfs_conn.cat(ipfs_hash)
        f = io.BytesIO(ipfs_data)
        return f

    def write_file_in_ipfs(self, filepath):
        """
            push a file to ipfs given its path
        """
        try:
            with open(filepath, 'r+b') as file:
                result = self.ipfs_conn.add(
                    file, pin=True, wrap_with_directory=True)
                return result[1]['Hash'] + '/' + result[0]['Name']
        except Exception as err:
            logging.error("File error ", err)
        return ''

    def read_file_from_ipfs(self, ipfs_hash):

        ipfs_data = self.ipfs_conn.cat(ipfs_hash)
        return json.loads(ipfs_data.decode('utf8'))
