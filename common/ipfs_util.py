import io
import json
import logging

import ipfshttpclient


class IPFSUtil(object):

    def __init__(self, ipfs_url, port):
        #
        # Please refer to the documentation given at  https://libraries.io/pypi/ipfsapi
        # The API deamon location is now described using MultiAddr,
        # hence rather than doing ipfshttpclient.connect(host, port) to pass the network address parameters,
        # use:ipfshttpclient.connect("/dns/<host>/tcp/<port>/http"),
        # Please note that https://ipfs.singularitynet.io/api/v0/version
        # {
        # "Version": "0.4.19",
        # "Commit": "",
        # "Repo": "7",
        # "System": "amd64/linux",
        # "Golang": "go1.11.5"
        # }
        self.ipfs_conn = ipfshttpclient.connect(f'/dns/{ipfs_url}/tcp/{port}/https', session=False)

    def read_bytesio_from_ipfs(self, ipfs_hash):

        ipfs_data = self.ipfs_conn.cat(ipfs_hash)
        f = io.BytesIO(ipfs_data)
        return f

    def write_file_in_ipfs(self, filepath, wrap_with_directory=True):
        """
            push a file to ipfs given its path
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

        ipfs_data = self.ipfs_conn.cat(ipfs_hash)
        return json.loads(ipfs_data.decode('utf8'))

    def close(self):  # Call this when you're done
        self.ipfs_conn.close()
