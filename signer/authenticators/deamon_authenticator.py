import web3
from eth_account.messages import defunct_hash_message

from common.repository import Repository


class SignatureAuthenticator(object):

    def get_signature_message(self):
        pass

    def get_public_key(self):
        pass

    def get_signature(self):
        pass

    def get_principal(self):
        pass


class DeamonAuthenticator(SignatureAuthenticator):

    def __init__(self, event):
        self.event = event

    def get_signature_message(self):
        username = self.event['headers']['x-username']
        organization_id = self.event['headers']['x-organizationid']
        group_id = self.event['headers']['x-groupid']
        service_id = self.event['headers']['x-serviceid']
        block_number = self.event['headers']['x-currentblocknumber']

        message = web3.Web3.soliditySha3(["string", "string", "string", "string", "uint256"],
                                         [username, organization_id, service_id, group_id, block_number])
        return defunct_hash_message(message)

    def get_public_key(self):
        organization_id = self.event['headers']['x-organizationid']
        group_id = self.event['headers']['x-groupid']
        service_id = self.event['headers']['x-serviceid']

        query = 'SELECT public_key FROM demon_auth_keys WHERE org_id = %s AND service_id = %s AND group_id = %s '
        public_key = Repository().execute(
            query, [organization_id, service_id, group_id])
        return public_key[0]

    def get_signature(self):
        return self.event['headers']['x-signature']

    def get_principal(self):
        return self.event['headers']['x-username']
