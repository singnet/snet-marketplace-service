import glob
import json
import os
import tarfile

import ipfsapi
import io

import logging

from common.constant import IPFS_URL
from common.s3_util import  S3Util


class IPFSUtil(object):


    def  __init__(self, ipfs_url, port):
        self.host=ipfs_url
        self.port=port



    def read_bytesio_from_ipfs(self, ipfs_hash):
        ipfs_conn = ipfsapi.connect(host=self.host , port=self.port)

        ipfs_data = ipfs_conn.cat(ipfs_hash)
        f = io.BytesIO(ipfs_data)
        return f

    def write_file_in_ipfs(self,filepath):
        """
            push a file to ipfs given its path
        """
        ipfs_conn = ipfsapi.connect(host=self.host, port=self.port)
        try:
            with open(filepath, 'r+b') as file:
                result = ipfs_conn.add(file,pin=True,wrap_with_directory=True)
                return  result[1]['Hash']+'/'+result[0]['Name']
        except Exception as err:
            logging.error("File error ", err)
        return ''

if __name__=='__main__':
    #IPFS_URL['url'], IPFS_URL['port'])
    #'QmbrFpYk2oLibQJz1JiR4VtHFsJGuvfgAWAVzbKkV41EiD'
    #'QmbFMke1KXqnYyBBWxB74N4c5SBnJMVAiMNRcGu6x1AwQH'

    # <
    #
    # class 'list'>: [{'Name': 'test2.jpeg', 'Hash': 'QmbFMke1KXqnYyBBWxB74N4c5SBnJMVAiMNRcGu6x1AwQH', 'Size': '6'},
    #                 {'Name': '', 'Hash': 'QmbrFpYk2oLibQJz1JiR4VtHFsJGuvfgAWAVzbKkV41EiD', 'Size': '62'}]
    #
    #QmbFMke1KXqnYyBBWxB74N4c5SBnJMVAiMNRcGu6x1AwQH
    reulst = IPFSUtil(IPFS_URL['url'], IPFS_URL['port']).write_file_in_ipfs('/home/sohit/Downloads/download.jpeg')
    print(reulst)
    # name=reulst
    # a=name.split('/')
    # file_name=a[1]
    #
    #
    # reulst= IPFSUtil(IPFS_URL['url'],IPFS_URL['port']).read_bytesio_from_ipfs(reulst)
    #
    # print(reulst)
    # object=S3Util().get_s3_resource_from_key().Object('enhanced-marketplace','test-folder/'+file_name)
    # object.upload_fileobj(reulst)
    # print(123)
    #
    # S3Util().delete_file_from_s3('https://enhanced-marketplace.s3.amazonaws.com/test-folder/download.jpeg')
    #


