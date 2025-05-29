import base64
import json

import web3
from eth_account.messages import defunct_hash_message

from common.blockchain_util import BlockChainUtil
from common.boto_utils import BotoUtils
from common.logger import get_logger
from signer.settings import settings

logger = get_logger(__name__)
class SignatureAuthenticator(object):
    BLOCK_LIMIT = 10

    def __init__(self, event, networks, net_id):
        self.event = event
        self.networks = networks
        self.net_id = net_id
        self.boto_utils=BotoUtils(settings.aws.REGION_NAME)


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
        message = web3.Web3.solidity_keccak(
            ["string", "string", "string", "string", "string", "uint256"],
            ['_usage', username, organization_id, service_id, group_id, int(block_number)]
        )
        return defunct_hash_message(message)


    def _get_daemon_addresses(self,org_id,service_id,group_id):
        lambda_payload = {
            "httpMethod": "GET",
            "queryStringParameters": {
                "org_id": org_id,
                "service_id": service_id
            },
        }
        response = self.boto_utils.invoke_lambda(
            lambda_function_arn=settings.lambda_arn.get_service_deatails_arn,
            invocation_type="RequestResponse",
            payload=json.dumps(lambda_payload),
        )

        response_body_raw = response["body"]
        get_service_response = json.loads(response_body_raw)
        if get_service_response["status"] == "success":
            groups_data = get_service_response["data"].get("groups", [])
            for group_data in groups_data:
                if group_data["group_id"] == group_id:
                    return group_data["daemon_addresses"]
        raise Exception(
            "Unable to fetch daemon Addresses information for service %s under organization %s for %s group.",
            service_id, org_id, group_id)


    def get_public_keys(self):
        organization_id = self.event['headers']['x-organizationid']
        group_id = self.event['headers']['x-groupid']
        service_id = self.event['headers']['x-serviceid']

        stored_public_keys = self._get_daemon_addresses(organization_id, service_id, group_id)
        logger.info(f"Got stored daemon addresses {stored_public_keys} for {organization_id} {service_id} {group_id}")
        return stored_public_keys

    def get_signature(self):
        base64_sign = self.event['headers']['x-signature']
        return base64.b64decode(base64_sign)

    def get_principal(self):
        return self.event['headers']['x-username']
