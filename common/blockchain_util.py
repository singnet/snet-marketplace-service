import web3
from web3 import Web3


class BlockChainUtil(object):

    def __init__(self, ws_provider):
        self.ws_provider = ws_provider

    def get_current_block_no(self):
        w3Obj = Web3(web3.providers.WebsocketProvider(self.ws_provider))
        return w3Obj.eth.blockNumber
