from repository import Repository
from service import Service


class Channel:
    def __init__(self):
        self.repo = Repository()
        self.objSrvc = Service()

    def get_channel_info(self, user_address, service_id, org_name=None):
        try:
            if user_address is not None and service_id is not None:
                query = 'SELECT M.*, T.endpoint, T.is_available FROM service_group G, mpe_channel M, service_status T, service S ' \
                        'WHERE G.group_id = M.groupid AND G.group_id = T.group_id and S.row_id = T.service_id and T.service_id = G.service_id ' \
                        'AND T.is_available = 1 AND G.service_id = %s AND M.sender = %s ORDER BY M.expiration DESC '
                result = self.repo.execute(query, [service_id, user_address])
                if result is not None and result != []:
                    channels_data = {}
                    for rec in result:
                        group_id = rec['groupId']
                        if group_id not in channels_data.keys():
                            channels_data[group_id] = {}
                            channels_data[group_id]['endpoint'] = []
                        channels_data[group_id].update({'groupId': group_id,
                                                        'channelID': rec['channel_id'],
                                                        'sender': rec['sender'],
                                                        'recipient': rec['recipient'],
                                                        'balance': rec['balance'],
                                                        'pending': rec['pending'],
                                                        'nonce': rec['nonce'],
                                                        'expiration': rec['expiration'],
                                                        'signer': rec['signer']})
                        channels_data[group_id]['endpoint'].append(rec['endpoint'])
                        format_channel_data = [val for val in channels_data.values()]
                    return format_channel_data
                else:
                    query = ' SELECT T.group_id, T.endpoint, T.is_available FROM service_group G, service_status T, service S ' \
                            'WHERE G.group_id = T.group_id AND S.row_id = T.service_id AND T.service_id = G.service_id ' \
                            'AND T.is_available = 1 AND G.service_id = %s '
                    result = self.repo.execute(query, service_id)
                    if result is not None and result != []:
                        channels_data = {}
                        for rec in result:
                            group_id = rec['group_id']
                        if group_id not in channels_data.keys():
                            channels_data[group_id] = {}
                            channels_data[group_id]['groupId'] = group_id
                            channels_data[group_id]['endpoint'] = []
                        channels_data[group_id]['endpoint'].append(rec['endpoint'])
                        format_channel_data = [val for val in channels_data.values()]
                        return format_channel_data
            return []
        except Exception as err:
            print('Error in get_channel_info: ', err)

