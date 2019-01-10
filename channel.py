from repository import Repository
from service import Service


class Channel:
    def __init__(self, netId):
        self.repo = Repository(netId)
        self.objSrvc = Service(netId)

    def get_channel_info(self, user_address, service_id, org_id):
        print('Inside get_channel_info::user_address', user_address, '|', service_id, '|', org_id)
        try:
            if user_address is not None and service_id is not None and org_id is not None:
                query = 'SELECT M.*, T.endpoint, T.is_available FROM service_group G, mpe_channel M, service_status T, service S ' \
                        'WHERE G.group_id = M.groupId AND G.group_id = T.group_id and S.row_id = T.service_row_id and T.service_row_id = G.service_row_id ' \
                        'AND T.is_available = 1 AND G.service_id = %s AND G.org_id = %s AND M.sender = %s ORDER BY M.expiration DESC '
                print('query: ', query)
                result = self.repo.execute(query, [service_id, org_id, user_address])
                channels_data = {}
                if result is not None and result != []:
                    for rec in result:
                        group_id = rec['groupId']
                        if group_id not in channels_data.keys():
                            channels_data[group_id] = {}
                            channels_data[group_id]['endpoint'] = []
                            channels_data[group_id]['channelId'] = {}

                        channel_id = rec['channel_id']
                        if channel_id not in channels_data[group_id]['channelId'].keys():
                            channels_data[group_id]['channelId'][channel_id] = {}

                        channels_data[group_id]['channelId'][channel_id].update({'channelId': channel_id,
                                                                                 'balance': str(rec['balance']),
                                                                                 'pending': str(rec['pending']),
                                                                                 'nonce': rec['nonce'],
                                                                                 'expiration': rec['expiration'],
                                                                                 'signer': rec['signer']})
                        channels_data[group_id].update({'groupId': group_id,
                                                        'sender': rec['sender'],
                                                        'recipient': rec['recipient']})
                        channels_data[group_id]['endpoint'].append(rec['endpoint'])

                    channels_data[group_id]['channelId'] = [val for val in
                                                            channels_data[group_id]['channelId'].values()]
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
                        channels_data[group_id]['channelId'] = []
                        channels_data[group_id]['endpoint'].append(rec['endpoint'])
                        channels_data = [val for val in channels_data.values()]
                        return channels_data
            return []
        except Exception as err:
            print('Error in get_channel_info: ', err)

