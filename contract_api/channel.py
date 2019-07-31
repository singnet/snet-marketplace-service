import web3
from common.constant import NETWORKS
from common.utils import Utils
from contract_api.service import Service
from web3 import Web3


class Channel:
    def __init__(self, net_id, obj_repo):
        self.repo = obj_repo
        self.objSrvc = Service(obj_repo=obj_repo)
        self.ws_provider = NETWORKS[net_id]['ws_provider']
        self.obj_util = Utils()

    def get_channel_info(self, user_address, service_id, org_id):
        print('Inside get_channel_info::user_address', user_address, '|', service_id, '|', org_id)
        try:
            if user_address is not None and service_id is not None and org_id is not None:
                query = 'SELECT M.*, T.endpoint, T.is_available FROM service_group G, mpe_channel M, service_status T, service S ' \
                        'WHERE G.group_id = M.groupId AND G.group_id = T.group_id and S.row_id = T.service_row_id and T.service_row_id = G.service_row_id ' \
                        'AND T.is_available = 1 AND G.service_id = %s AND G.org_id = %s AND M.sender = %s ORDER BY M.expiration DESC '
                print('query: ', query)
                result = self.repo.execute(query, [service_id, org_id, user_address])
                return self._manage_channel_data(result=result, service_id=service_id, org_id=org_id)
        except Exception as err:
            print('Error in get_channel_info: ', err)

    def _manage_channel_data(self, result, service_id, org_id):
        channels_data = {}
        if result is not None and result != []:
            for rec in result:
                group_id = rec['groupId']
                if group_id not in channels_data.keys():
                    channels_data[group_id] = {}
                    channels_data[group_id]['endpoint'] = []
                    channels_data[group_id]['channels'] = {}

                channel_id = rec['channel_id']
                if channel_id not in channels_data[group_id]['channels'].keys():
                    channels_data[group_id]['channels'][channel_id] = {}

                channels_data[group_id]['channels'][channel_id].update({'channelId': channel_id,
                                                                        'balance_in_cogs': str(rec['balance_in_cogs']),
                                                                        'pending': str(rec['pending']),
                                                                        'nonce': rec['nonce'],
                                                                        'expiration': rec['expiration'],
                                                                        'signer': rec['signer']})
                channels_data[group_id].update({'groupId': group_id,
                                                'sender': rec['sender'],
                                                'recipient': rec['recipient']})
                channels_data[group_id]['endpoint'].append(rec['endpoint'])

            channels_data[group_id]['channels'] = [val for val in
                                                   channels_data[group_id]['channels'].values()]
            channels_data = [val for val in channels_data.values()]
            return channels_data
        else:
            query = ' SELECT T.group_id, T.endpoint, T.is_available, G.payment_address as recipient FROM service_group G, service_status T, service S ' \
                    'WHERE G.group_id = T.group_id AND S.row_id = T.service_row_id AND T.service_row_id = G.service_row_id ' \
                    'AND T.is_available = 1 AND G.service_id = %s AND G.org_id = %s '
            print('query: ', query)
            result = self.repo.execute(query, [service_id, org_id])
            if result is not None and result != []:
                for rec in result:
                    group_id = rec['group_id']
                    if group_id not in channels_data.keys():
                        channels_data[group_id] = {}
                        channels_data[group_id]['groupId'] = group_id
                        channels_data[group_id]['recipient'] = rec['recipient']
                        channels_data[group_id]['endpoint'] = []
                    channels_data[group_id]['channels'] = []
                    channels_data[group_id]['endpoint'].append(rec['endpoint'])
                channels_data = [val for val in channels_data.values()]
                return channels_data
        return []

    def get_latest_block_no(self):
        w3Obj = Web3(web3.providers.WebsocketProvider(self.ws_provider))
        return w3Obj.eth.blockNumber

    def get_expired_channel_info(self, user_address):
        print('Inside get_expired_channel_info::user_address', user_address)
        try:
            expired_chnl_data = list()
            last_block_no = self.get_latest_block_no()
            print("last_block_no: ", last_block_no)
            qry = "SELECT  G.org_id, D.display_name, M.* FROM mpe_channel M, service_group G ,service_metadata D, " \
                  "organization O WHERE M.groupId = G.group_id AND M.recipient = G.payment_address AND " \
                  "D.service_row_id =  G.service_row_id AND O.org_id = G.org_id AND balance_in_cogs > 0  AND " \
                  "expiration < %s AND sender = %s "
            print("qry: ", qry)
            channel_details = self.repo.execute(qry, [last_block_no, user_address])
            for detail in channel_details:
                expired_chnl_data.append(self.obj_util.clean_row(detail))
        except Exception as e:
            print(repr(e))
            raise e
        return expired_chnl_data
