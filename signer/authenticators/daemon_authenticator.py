import web3
import base64
from eth_account.messages import defunct_hash_message

from common.blockchain_util import BlockChainUtil
from common.repository import Repository
from signer.config import NETWORKS, NET_ID


class SignatureAuthenticator(object):
    BLOCK_LIMIT = 10

    def __init__(self, event, networks, net_id):
        self.event = event
        self.networks = networks
        self.net_id = net_id

    def get_signature_message(self):
        pass

    def get_public_keys(self):
        pass

    def get_signature(self):
        pass

    def get_principal(self):
        pass

    def verify_current_block_number(self):
        signed_block_number = int(
            self.event['headers']['x-currentblocknumber'])
        blockchain_util = BlockChainUtil(provider_type="WS_PROVIDER", provider=self.networks[self.net_id]['ws_provider'])
        current_block_number = blockchain_util.get_current_block_no()
        print(f"current block {current_block_number}\n"
              f"signed clock number {signed_block_number}")
        if current_block_number > signed_block_number + self.BLOCK_LIMIT or current_block_number < signed_block_number - self.BLOCK_LIMIT:
            print("current_block_number is more than signed block limit %s",
                  current_block_number)
            return False
        return True


class DaemonAuthenticator(SignatureAuthenticator):

    def __init__(self, events, networks, net_id):
        super().__init__(events, networks, net_id)

    def get_signature_message(self):
        username = self.event['headers']['x-username']
        organization_id = self.event['headers']['x-organizationid']
        group_id = self.event['headers']['x-groupid']
        service_id = self.event['headers']['x-serviceid']
        block_number = self.event['headers']['x-currentblocknumber']
        message = web3.Web3.soliditySha3(["string", "string", "string", "string", "string", "uint256"],
                                         ['_usage', username, organization_id, service_id, group_id, int(block_number)])
        return defunct_hash_message(message)

    def get_public_keys(self):
        organization_id = self.event['headers']['x-organizationid']
        group_id = self.event['headers']['x-groupid']
        service_id = self.event['headers']['x-serviceid']

        query = 'SELECT public_key FROM demon_auth_keys WHERE org_id = %s AND service_id = %s AND group_id = %s '
        stored_public_keys = Repository(net_id=NET_ID, NETWORKS=NETWORKS).execute(
            query, [organization_id, service_id, group_id])
        public_keys = []
        if stored_public_keys:
            for stored_public_key in stored_public_keys:
                public_keys.append(stored_public_key['public_key'])
        return public_keys

    def get_signature(self):
        base64_sign = self.event['headers']['x-signature']
        return base64.b64decode(base64_sign)

    def get_principal(self):
        return self.event['headers']['x-username']
