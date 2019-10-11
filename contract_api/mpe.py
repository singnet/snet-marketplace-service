import json

import web3
from web3 import Web3

from common.utils import Utils
from contract_api.config import NETWORKS
from contract_api.registry import Registry


class MPE:
    def __init__(self, net_id, obj_repo):
        self.repo = obj_repo
        self.objSrvc = Registry(obj_repo=obj_repo)
        self.ws_provider = NETWORKS[net_id]["ws_provider"]
        self.obj_util = Utils()

    def get_latest_block_no(self):
        w3 = Web3(web3.providers.WebsocketProvider(self.ws_provider))
        return w3.eth.blockNumber

    def get_channels(self, user_address, org_id=None, service_id=None, group_id=None):
        if user_address and org_id and group_id:
            return self.get_channels_by_user_address_org_group(
                user_address=user_address, org_id=org_id, group_id=group_id
            )
        elif user_address is not None:
            return self.get_channels_by_user_address(user_address, service_id, org_id)

        else:
            raise Exception("Invalid Request")

    def get_channels_by_user_address(self, user_address, service_id, org_id):
        last_block_no = self.get_latest_block_no()
        params = [last_block_no]
        print(
            "Inside get_channel_info::user_address",
            user_address,
            "|",
            org_id,
            "|",
            service_id,
        )
        sub_qry = ""
        if user_address is not None and service_id is not None and org_id is not None:
            sub_qry = " AND S.org_id = %s AND S.service_id = %s "
            params.append(org_id)
            params.append(service_id)
        params.append(user_address)
        raw_channel_dta = self.repo.execute(
            'SELECT  C.*, E.*, IF(C.expiration > %s, "active","inactive") AS status FROM '
            "service_group G, mpe_channel C, service_endpoint E, service S WHERE G.group_id = C.groupId AND "
            "G.group_id = E.group_id and S.row_id = E.service_row_id and E.service_row_id = G.service_row_id "
            "AND S.is_curated = 1  "
            + sub_qry
            + " AND C.sender = %s ORDER BY C.expiration DESC",
            params,
        )
        self.obj_util.clean(raw_channel_dta)
        channel_dta = {}
        for rec in raw_channel_dta:
            group_id = rec["groupId"]
            if group_id not in channel_dta.keys():
                channel_dta[group_id] = {
                    "group_id": group_id,
                    "org_id": rec["org_id"],
                    "service_id": rec["service_id"],
                    "group": {"endpoints": []},
                    "channels": [],
                }

            channel = {
                "channel_id": rec["channel_id"],
                "recipient": rec["recipient"],
                "balance_in_cogs": rec["balance_in_cogs"],
                "pending": rec["pending"],
                "nonce": rec["nonce"],
                "expiration": rec["expiration"],
                "signer": rec["signer"],
                "status": rec["status"],
            }
            endpoint = {
                "endpoint": rec["endpoint"],
                "is_available": rec["endpoint"],
                "last_check_timestamp": rec["last_check_timestamp"],
            }
            channel_dta[group_id]["group"]["endpoints"].append(endpoint)
            channel_dta[group_id]["channels"].append(channel)
        return list(channel_dta.values())

    def get_channels_by_user_address_org_group(
        self, user_address, org_id=None, group_id=None
    ):
        last_block_no = self.get_latest_block_no()
        params = [last_block_no, org_id, group_id, user_address]
        raw_channel_data = self.repo.execute(
            "SELECT C.* , OG.payment, OG.org_id, IF(C.expiration > %s, 'active','inactive') AS status FROM "
            "mpe_channel C JOIN org_group OG ON C.groupId = OG.group_id "
            "where OG.org_id = %s and C.groupId = %s and C.sender = %s",
            params,
        )
        self.obj_util.clean(raw_channel_data)
        channel_data = {"group_id": group_id, "org_id": org_id, "channels": []}
        for record in raw_channel_data:
            record["payment"] = json.loads(record["payment"])
            if record["recipient"] == record["payment"]["payment_address"]:
                if group_id not in channel_data.keys():
                    channel = {
                        "channel_id": record["channel_id"],
                        "recipient": record["recipient"],
                        "balance_in_cogs": record["balance_in_cogs"],
                        "pending": record["pending"],
                        "nonce": record["nonce"],
                        "expiration": record["expiration"],
                        "signer": record["signer"],
                        "status": record["status"],
                    }
                    channel_data["channels"].append(channel)

        return channel_data

    def get_channel_data_by_group_id_and_channel_id(self, group_id, channel_id):
        try:
            result = self.repo.execute(
                "SELECT * FROM mpe_channel WHERE groupId = %s AND channel_id = %s",
                [group_id, channel_id],
            )
            self.obj_util.clean(result)
            return result
        except Exception as e:
            print(repr(e))
            raise e
