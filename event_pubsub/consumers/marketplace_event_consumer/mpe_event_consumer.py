import web3
from web3 import Web3

from common.ipfs_util import IPFSUtil
from event_pubsub.consumers.event_consumer import EventConsumer
import json
import base64

from event_pubsub.consumers.marketplace_event_consumer.dao.mpe_repository import MPERepository
from event_pubsub.repository import Repository


class MPEEventConsumer(EventConsumer):
    connection = (Repository(NETWORKS={
        'db': {"HOST": "localhost",
               "USER": "root",
               "PASSWORD": "password",
               "NAME": "pub_sub",
               "PORT": 3306,
               }
    }))
    mpe_dao = MPERepository(connection)

    def __init__(self, ws_provider, ipfs_url=None):
        self.ipfs_client = IPFSUtil(ipfs_url, 80)
        self.web3 = Web3(web3.providers.WebsocketProvider(ws_provider))

    def get_contract_file_paths(self, base_path, contract_name):
        if contract_name == "REGISTRY":
            json_file = "Registry.json"
        elif contract_name == "MPE":
            json_file = "MultiPartyEscrow.json"
        else:
            raise Exception("Invalid contract Type {}".format(contract_name))

        contract_network_path = base_path + "{}/{}".format("networks", json_file)
        contract_abi_path = base_path + "{}/{}".format("abi", json_file)

        return contract_network_path, contract_abi_path

    def get_contract_details(self, contract_abi_path, contract_network_path, net_id):

        with open(contract_abi_path) as abi_file:
            abi_value = json.load(abi_file)
            contract_abi = abi_value

        with open(contract_network_path) as network_file:
            network_value = json.load(network_file)
            contract_address = network_value[str(net_id)]['address']

        return contract_abi, contract_address

    def on_event(self, event):
        net_id = 3
        network_path ,abi_pat= self.get_contract_file_paths("../../node_modules/singularitynet-platform-contracts/",
                                                             "MPE")
        contract_abi, contract_address = self.get_contract_details(abi_pat, network_path, net_id)
        mpe_contract = self.web3.eth.contract(address=self.web3.toChecksumAddress(contract_address),
                                                   abi=contract_abi)
        event_name = event["name"]
        event_data = event["data"]
        mpe_data = eval(event_data['json_str'])

        if event_name == 'ChannelOpen':
            self.mpe_dao.create_channel(mpe_data)
        else:
            channel_id = int(mpe_data['channelId'])
            channel_data = mpe_contract.functions.channels(
                channel_id).call()
            #<class 'list'>: [0, '0x400dA26771b53bDe34820FCAd96ffcF571AC612f', '0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F', '0xfA8a01E837c30a3DA3Ea862e6dB5C6232C9b800A', b"\x9b\x91JZ\xae![G\xe8\x19njI\xbc\xc6J8\x19F\xe2\xac\xec\rY\xc1\xb2+'\xd7\xbd\xea\xb7", 1391, 27614372]
            group_id = base64.b64encode(channel_data[4]).decode('utf8')
            self.mpe_dao.update_channel(
                channel_id=channel_id, group_id=group_id, channel_data=channel_data)
