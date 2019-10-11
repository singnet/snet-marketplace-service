import json
import uuid

import web3
from eth_account.messages import defunct_hash_message
from web3 import Web3



class BlockChainUtil(object):

    def __init__(self, provider_type, provider):
        if provider_type == "HTTP_PROVIDER":
            self.provider = Web3.HTTPProvider(provider)
        elif provider_type == "WS_PROVIDER":
            self.provider = web3.providers.WebsocketProvider(provider)
        else:
            raise Exception("Only HTTP_PROVIDER and WS_PROVIDER provider type are supported.")
        self.web3_object = Web3(self.provider)

    def load_contract(self, path):
        with open(path) as f:
            contract = json.load(f)
        return contract

    def read_contract_address(self, net_id, path, key):
        contract = self.load_contract(path)
        return Web3.toChecksumAddress(contract[str(net_id)][key])
        return nonce

    def contract_instance(self, contract, address):
        return self.web3_object.eth.contract(abi=contract, address=address)

    def generate_signature(self, data_types, values, signer_key):
        signer_key = "0x" + signer_key if not signer_key.startswith("0x") else signer_key
        message = web3.Web3.soliditySha3(data_types, values)
        signature = self.web3_object.eth.account.signHash(defunct_hash_message(message), signer_key)
        return signature.signature.hex()

    def get_nonce(self, address):
        """ transaction count includes pending transaction also. """
        nonce = self.web3_object.eth.getTransactionCount(address, 'pending')
        return nonce

    def sign_transaction_with_private_key(self, private_key, transaction_object):
        return self.web3_object.eth.account.signTransaction(transaction_object, private_key).rawTransaction

    def create_transaction_object(self, *positional_inputs, method_name, address, contract_path, contract_address_path,
                                  net_id):
        nonce = self.get_nonce(address=address)
        self.contract = self.load_contract(path=contract_path)
        self.contract_address = self.read_contract_address(net_id=net_id, path=contract_address_path, key='address')
        self.contract_instance = self.contract_instance(contract=self.contract, address=self.contract_address)
        print("gas_price == ", self.web3_object.eth.gasPrice)
        print("nonce == ", nonce)
        transaction_object = getattr(self.contract_instance.functions, method_name)(
            *positional_inputs).buildTransaction({
            "from": address,
            "nonce": nonce,
            "gasPrice": self.web3_object.eth.gasPrice,
            "chainId": 3
        })
        return transaction_object

    def process_raw_transaction(self, raw_transaction):
        return self.web3_object.eth.sendRawTransaction(raw_transaction).hex()

    def create_account(self):
        account = self.web3_object.eth.account.create(uuid.uuid4().hex)
        return account.address, account.privateKey.hex()

    def get_current_block_no(self):
        return self.web3_object.eth.blockNumber

    def get_transaction_receipt_from_blockchain(self, transaction_hash):
        return  self.web3_object.eth.getTransactionReceipt(transaction_hash)