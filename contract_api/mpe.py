import decimal
import json
import boto3

from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from common.utils import Utils
from contract_api.config import NETWORKS, NETWORK_ID, SIGNER_SERVICE_ARN, REGION_NAME
from contract_api.dao.mpe_repository import MPERepository
from contract_api.dao.service_repository import ServiceRepository

logger = get_logger(__name__)


class MPE:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_util = Utils()
        self.blockchain_util = BlockChainUtil(provider_type="WS_PROVIDER", provider=NETWORKS[NETWORK_ID]["ws_provider"])

    def get_channels(self, user_address, org_id=None, service_id=None, group_id=None):
        if user_address and org_id and group_id:
            return self.get_channels_by_user_address_org_group(
                user_address=user_address,
                org_id=org_id,
                group_id=group_id
            )
        elif user_address is not None:
            return self.get_channels_by_user_address(user_address, service_id, org_id)

        else:
            raise Exception("Invalid Request")

    def get_channels_by_user_address_v2(self, user_address):
        last_block_no = self.blockchain_util.get_current_block_no()
        logger.info(f"got block number {last_block_no}")
        channel_details_query = "SELECT mc.channel_id, mc.sender, mc.recipient, mc.groupId as group_id, " \
                                "mc.balance_in_cogs, mc.pending, mc.nonce, mc.consumed_balance, mc.expiration, " \
                                "mc.signer, og.org_id, " \
                                "org.organization_name, IF(mc.expiration > %s, 'active','inactive') AS status, " \
                                "og.group_name, org.org_assets_url " \
                                "FROM mpe_channel AS mc JOIN org_group AS og ON mc.groupId = og.group_id " \
                                "JOIN organization AS org ON og.org_id = org.org_id WHERE mc.sender = %s "
        params = [last_block_no, user_address]
        channel_details = self.repo.execute(
            channel_details_query,
            params
        )
        self.obj_util.clean(channel_details)

        channel_details_response = {"wallet_address": user_address,
                                    "organizations": self.segregate_org_channel_details(channel_details)}

        return channel_details_response

    def segregate_org_channel_details(self, raw_channel_data):
        org_data = {}
        for channel_record in raw_channel_data:
            org_id = channel_record["org_id"]
            group_id = channel_record["group_id"]

            if org_id not in org_data:
                org_data[org_id] = {
                    "org_name": channel_record["organization_name"],
                    "org_id": org_id,
                    "hero_image": json.loads(channel_record["org_assets_url"]).get("hero_image", ""),
                    "groups": {}
                }
            if group_id not in org_data[org_id]["groups"]:
                org_data[org_id]["groups"][group_id] = {
                    "group_id": group_id,
                    "group_name": channel_record["group_name"],
                    "channels": []
                }

            channel = {
                "channel_id": channel_record["channel_id"],
                "recipient": channel_record["recipient"],
                'balance_in_cogs': channel_record['balance_in_cogs'],
                'consumed_balance': channel_record["consumed_balance"],
                'current_balance': str(decimal.Decimal(channel_record['balance_in_cogs']) - decimal.Decimal(
                    channel_record["consumed_balance"])),
                "pending": channel_record["pending"],
                "nonce": channel_record["nonce"],
                "expiration": channel_record["expiration"],
                "signer": channel_record["signer"],
                "status": channel_record["status"]
            }

            org_data[org_id]["groups"][group_id]["channels"].append(channel)

        for org_id in org_data:
            org_data[org_id]["groups"] = list(org_data[org_id]["groups"].values())

        return list(org_data.values())

    def get_channels_by_user_address(self, user_address, service_id, org_id):
        last_block_no = self.blockchain_util.get_current_block_no()
        params = [last_block_no]
        logger.info(f'Inside get_channel_info :: user_address={user_address}, org_id={org_id}, service_id={service_id}')
        sub_qry = ""
        if user_address is not None and service_id is not None and org_id is not None:
            sub_qry = " AND S.org_id = %s AND S.service_id = %s "
            params.append(org_id)
            params.append(service_id)
        params.append(user_address)
        raw_channel_dta = self.repo.execute(
            'SELECT  C.*, E.*, IF(C.expiration > %s, "active","inactive") AS status FROM '
            'service_group G, mpe_channel C, service_endpoint E, service S WHERE G.group_id = C.groupId AND '
            'G.group_id = E.group_id and S.row_id = E.service_row_id and E.service_row_id = G.service_row_id '
            'AND S.is_curated = 1  ' + sub_qry + ' AND C.sender = %s ORDER BY C.expiration DESC', params)
        self.obj_util.clean(raw_channel_dta)
        channel_dta = {}
        for rec in raw_channel_dta:
            group_id = rec['groupId']
            if group_id not in channel_dta.keys():
                channel_dta[group_id] = {'group_id': group_id,
                                         'org_id': rec['org_id'],
                                         'service_id': rec['service_id'],
                                         'group': {"endpoints": []},
                                         'channels': []
                                         }

            channel = {
                'channel_id': rec['channel_id'],
                'recipient': rec['recipient'],
                'balance_in_cogs': rec['balance_in_cogs'],
                'consumed_balance': rec["consumed_balance"],
                'current_balance': str(decimal.Decimal(rec['balance_in_cogs']) - decimal.Decimal(
                    rec["consumed_balance"])),
                'pending': rec['pending'],
                'nonce': rec['nonce'],
                'expiration': rec['expiration'],
                'signer': rec['signer'],
                'status': rec['status']
            }
            endpoint = {'endpoint': rec['endpoint'],
                        'is_available': rec['endpoint'],
                        'last_check_timestamp': rec['last_check_timestamp']
                        }
            channel_dta[group_id]['group']['endpoints'].append(endpoint)
            channel_dta[group_id]['channels'].append(channel)
        return list(channel_dta.values())

    def get_channels_by_user_address_org_group(self, user_address, org_id=None, group_id=None):
        last_block_no = self.blockchain_util.get_current_block_no()
        params = [last_block_no, org_id, group_id, user_address]
        raw_channel_data = self.repo.execute(
            "SELECT C.* , OG.payment, OG.org_id, IF(C.expiration > %s, 'active','inactive') AS status FROM "
            "mpe_channel C JOIN org_group OG ON C.groupId = OG.group_id "
            "where OG.org_id = %s and C.groupId = %s and C.sender = %s", params
        )
        self.obj_util.clean(raw_channel_data)
        channel_data = {
            'group_id': group_id,
            'org_id': org_id,
            'channels': []
        }
        for record in raw_channel_data:
            record["payment"] = json.loads(record["payment"])
            if record["recipient"] == record["payment"]["payment_address"]:
                channel = {'channel_id': record['channel_id'],
                           'recipient': record['recipient'],
                           'balance_in_cogs': record['balance_in_cogs'],
                           'consumed_balance': record["consumed_balance"],
                           'current_balance': str(decimal.Decimal(record['balance_in_cogs']) - decimal.Decimal(
                               record["consumed_balance"])),
                           'pending': record['pending'],
                           'nonce': record['nonce'],
                           'expiration': record['expiration'],
                           'signer': record['signer'],
                           'status': record['status']
                           }
                channel_data['channels'].append(channel)

        return channel_data

    def get_channel_data_by_group_id_and_channel_id(self, group_id, channel_id):
        try:
            result = self.repo.execute(
                "SELECT * FROM mpe_channel WHERE groupId = %s AND channel_id = %s", [group_id, channel_id])
            self.obj_util.clean(result)
            return result
        except Exception as e:
            logger.exception(repr(e))
            raise e

    def update_consumed_balance(self, channel_id, signed_amount=None, org_id=None, service_id=None, username=None):
        mpe_repo = MPERepository(self.repo)
        channel = mpe_repo.get_mpe_channels(channel_id)
        if len(channel) != 0:
            channel = channel[0]
        else:
            raise Exception(f"Channel with id {channel_id} not found!")

        if signed_amount is None:
            signed_amount = self._get_channel_state_from_daemon(channel, org_id, service_id, username)
        mpe_repo.update_consumed_balance(channel_id, signed_amount)

        return {}

    def _get_channel_state_from_daemon(self, channel, org_id, service_id, username):
        channel_id = channel["channel_id"]
        group_id = channel["groupId"]

        org_repo = ServiceRepository(self.repo)
        endpoint = org_repo.get_service_endpoints(org_id, service_id, group_id)
        if len(endpoint) != 0:
            endpoint = endpoint[0]
        else:
            raise Exception(f"Endpoint with org_id {org_id}, service_id {service_id} and group_id {group_id} not found!")
        endpoint = endpoint["endpoint"]

        channel_state_signature = self._get_channel_state_signature(channel_id)
        signature = channel_state_signature["signature"]
        current_block_number = channel_state_signature["snet-current-block-number"]




    def _get_channel_state_signature(self, channel_id):
        get_channel_state_signature_body = {
            'channel_id': channel_id
        }

        get_channel_state_signature_payload = {
            "path": "/signer/state-service",
            "body": json.dumps(get_channel_state_signature_body),
            "httpMethod": "POST"
        }

        lambda_client = boto3.client('lambda', region_name = REGION_NAME)
        signature_response = lambda_client.invoke(
            FunctionName = SIGNER_SERVICE_ARN,
            InvocationType = 'RequestResponse',
            Payload = json.dumps(get_channel_state_signature_payload)
        )

        signature_response = json.loads(signature_response.get("Payload").read())
        if signature_response["statusCode"] != 200:
            raise Exception(f"Failed to create signature for {get_channel_state_signature_body}")
        signature_details = json.loads(signature_response["body"])
        return signature_details["data"]


