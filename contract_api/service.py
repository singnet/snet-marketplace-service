import datetime

import web3
from common.repository import NETWORKS
from common.utils import Utils
from eth_account.messages import defunct_hash_message


class Service:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_utils = Utils()

    def get_group_info(self, org_id=None, srvc_id=None):
        print('Inside grp info')
        service_status_dict = {}
        try:
            if org_id is None:
                status = self.repo.execute(
                    "SELECT G.*, S.endpoint, S.is_available, S.last_check_timestamp FROM service_group G, " \
                    "service_status S WHERE G.service_row_id = S.service_row_id AND G.group_id = S.group_id " \
                    "AND G.service_row_id IN (SELECT row_id FROM service WHERE is_curated = 1)")
            elif org_id is not None and srvc_id is None:
                query = "SELECT G.*, S.endpoint, S.is_available, S.last_check_timestamp FROM service_group G, " \
                        "service_status S WHERE G.service_row_id = S.service_row_id AND G.group_id = S.group_id " \
                        "AND G.service_row_id IN (SELECT row_id FROM service WHERE is_curated = 1 and org_id = %s)"
                status = self.repo.execute(query, org_id)
            else:
                query = "SELECT G.*, S.endpoint, S.is_available, S.last_check_timestamp FROM service_group G, " \
                        "service_status S WHERE G.service_row_id = S.service_row_id AND G.group_id = S.group_id " \
                        "AND G.service_row_id IN (SELECT row_id FROM service WHERE is_curated = 1 and org_id = %s " \
                        "AND service_id = %s ) "
                status = self.repo.execute(query, [org_id, srvc_id])

            self.obj_utils.clean(status)
            for rec in status:
                srvc_rw_id = rec['service_row_id']
                grp_id = rec['group_id']
                endpoint_value = {'is_available': rec['is_available'],
                                  'last_check_timestamp': rec['last_check_timestamp']}
                endpoint = rec['endpoint']
                if srvc_rw_id not in service_status_dict.keys():
                    service_status_dict[srvc_rw_id] = {'service_id': rec['service_id'], 'org_id': rec['org_id']}
                    service_status_dict[srvc_rw_id]['grp'] = {}
                if grp_id not in service_status_dict.get(srvc_rw_id).keys():
                    service_status_dict[srvc_rw_id]['grp'][grp_id] = {}
                    service_status_dict[srvc_rw_id]['grp'][grp_id]['payment_address'] = rec['payment_address']
                    service_status_dict[srvc_rw_id]['grp'][grp_id]['endpoint'] = {}
                service_status_dict[srvc_rw_id]['grp'][grp_id]['endpoint'].update(
                    {endpoint: endpoint_value})
            service_status = self.process_service_status(service_status_dict)
        except Exception as e:
            print(repr(e))
            raise e
        return service_status

    def process_service_status(self, service_status_dict):
        service_status = []
        for srvc_rw_id in service_status_dict.keys():
            is_available = 0
            grps_dict = service_status_dict.get(srvc_rw_id, {})
            grps = []
            for grp_id in grps_dict['grp'].keys():
                grp_available = 0
                endpts_dict = grps_dict['grp'].get(grp_id, {})
                endpts = []
                for endpt in endpts_dict['endpoint'].keys():
                    endpt_available = endpts_dict['endpoint'][endpt].get('is_available', None)
                    last_check_timestamp = endpts_dict['endpoint'][endpt].get('last_check_timestamp', None)
                    endpts.append({'endpoint': endpt,
                                   'is_available': endpt_available,
                                   'last_check_timestamp': last_check_timestamp
                                   })
                    grp_available = grp_available or endpt_available
                is_available = is_available or grp_available
                grps.append({'group_id': grp_id,
                             'endpoints': endpts,
                             'is_available': grp_available,
                             'payment_address': endpts_dict.get('payment_address', '')})
            service_status.append({
                'service_row_id': srvc_rw_id,
                'service_id': grps_dict['service_id'],
                'org_id': grps_dict['org_id'],
                'groups': grps,
                'is_available': is_available
            })
        return service_status

    def fetch_total_count(self):
        user_vote_count_dict = {}
        try:
            count_details = self.repo.execute(
                "SELECT org_id, service_id, vote, Count(*) AS count FROM user_service_vote GROUP BY vote, service_id, org_id")
            for rec in count_details:
                org_id = rec.get('org_id', '')
                service_id = rec.get('service_id', '')
                vote = rec.get('vote', '')
                count = rec.get('count', '')
                if not org_id in user_vote_count_dict.keys():
                    user_vote_count_dict[org_id] = {}
                if not service_id in user_vote_count_dict[org_id].keys():
                    user_vote_count_dict[org_id][service_id] = {}
                user_vote_count_dict[org_id][service_id][vote] = count
        except Exception as e:
            print(repr(e))
            raise e
        return user_vote_count_dict

    def vote_mapping(self, vote):
        return {'up_vote': (vote == 1),
                'down_vote': (vote == 0)}

    def fetch_user_vote(self, user_address):
        user_vote_dict = {}
        try:
            votes = self.repo.execute(
                "select * from user_service_vote where user_address = %s", (user_address))
            self.obj_utils.clean(votes)
            for rec in votes:
                org_id = rec['org_id']
                service_id = rec['service_id']
                comment = rec.get('comment', None)
                if org_id not in user_vote_dict.keys():
                    user_vote_dict[org_id] = {}
                user_vote_dict[org_id][service_id] = {'user_address': rec['user_address'],
                                                      'org_id': rec['org_id'],
                                                      'service_id': service_id,
                                                      'comment': comment}
                user_vote_dict[org_id][service_id].update(self.vote_mapping(rec['vote']))

        except Exception as e:
            print(repr(e))
            raise e
        return user_vote_dict

    def get_user_vote(self, user_address):
        vote_list = []
        try:
            count_details = self.fetch_total_count()
            votes = self.fetch_user_vote(user_address)
            print(votes)
            for org_id in count_details.keys():
                srvcs_data = count_details[org_id]
                for service_id in srvcs_data.keys():
                    rec = {
                        'org_id': org_id,
                        'service_id': service_id,
                        'up_vote_count': srvcs_data.get(service_id).get(1, 0),
                        'down_vote_count': srvcs_data.get(service_id).get(0, 0),
                        "up_vote": votes.get(org_id, {}).get(service_id, {}).get('up_vote', False),
                        "down_vote": votes.get(org_id, {}).get(service_id, {}).get('down_vote', False)
                    }
                    vote_list.append(rec)
        except Exception as e:
            print(repr(e))
            raise e
        return vote_list

    def get_usr_feedbk(self, user_address):
        vote_list = []
        try:
            count_details = self.fetch_total_count()
            votes = self.fetch_user_vote(user_address)
            print(votes)
            for org_id in count_details.keys():
                srvcs_data = count_details[org_id]
                for service_id in srvcs_data.keys():
                    rec = {
                        'org_id': org_id,
                        'service_id': service_id,
                        'up_vote_count': srvcs_data.get(service_id).get(1, 0),
                        'down_vote_count': srvcs_data.get(service_id).get(0, 0),
                        "up_vote": votes.get(org_id, {}).get(service_id, {}).get('up_vote', False),
                        "down_vote": votes.get(org_id, {}).get(service_id, {}).get('down_vote', False),
                        "comment": votes.get(org_id, {}).get(service_id, {}).get('comment', None)
                    }
                    vote_list.append(rec)
        except Exception as e:
            print(repr(e))
            raise e
        return vote_list

    def is_valid_vote(self, net_id, vote_info_dict):
        try:
            provider = web3.HTTPProvider(NETWORKS[net_id]['http_provider'])
            w3 = web3.Web3(provider)

            message_text = str(vote_info_dict['user_address']) + str(vote_info_dict['org_id']) + \
                           str(vote_info_dict['up_vote']).lower() + str(vote_info_dict['service_id']) + \
                           str(vote_info_dict['down_vote']).lower()
            message = w3.sha3(text=message_text)
            message_hash = defunct_hash_message(primitive=message)
            recovered = str(w3.eth.account.recoverHash(message_hash, signature=vote_info_dict['signature']))
            return str(vote_info_dict['user_address']).lower() == recovered.lower()
        except Exception as e:
            print(repr(e))
            raise e

        return False

    def set_user_vote(self, vote_info_dict, net_id):
        try:
            vote = -1
            if vote_info_dict['up_vote']:
                vote = 1
            elif vote_info_dict['down_vote']:
                vote = 0
            if self.is_valid_vote(net_id=net_id, vote_info_dict=vote_info_dict):
                query = "Insert into user_service_vote (user_address, org_id, service_id, vote, row_created) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE VOTE = %s"
                q_params = [vote_info_dict['user_address'], vote_info_dict['org_id'], vote_info_dict['service_id'],
                            vote, datetime.datetime.utcnow(), vote]
                res = self.repo.execute(query, q_params)
                print(res)
            else:
                raise Exception("Signature of the vote is not valid.")
        except Exception as e:
            print(repr(e))
            raise e
        return True

    def is_valid_feedbk(self, net_id, usr_addr, msg_txt, sign):
        try:
            provider = web3.HTTPProvider(NETWORKS[net_id]['http_provider'])
            w3 = web3.Web3(provider)
            message = w3.sha3(text=msg_txt)
            message_hash = defunct_hash_message(primitive=message)
            recovered = str(w3.eth.account.recoverHash(message_hash, signature=sign))
            return str(usr_addr).lower() == recovered.lower()
        except Exception as e:
            print(repr(e))
            raise e
        return False

    def set_usr_feedbk(self, feedbk_info, net_id):
        try:
            vote = -1
            if feedbk_info['up_vote']:
                vote = 1
            elif feedbk_info['down_vote']:
                vote = 0
            curr_dt = datetime.datetime.utcnow()
            usr_addr = feedbk_info['user_address']
            org_id = feedbk_info['org_id']
            srvc_id = feedbk_info['service_id']
            comment = feedbk_info['comment']
            msg_txt = str(usr_addr) + str(org_id) + str(feedbk_info['up_vote']).lower() + str(srvc_id) + \
                      str(feedbk_info['down_vote']).lower() + str(comment).lower()
            print(msg_txt)
            if self.is_valid_feedbk(net_id=net_id, usr_addr=usr_addr, msg_txt=msg_txt, sign=feedbk_info['signature']):
                query = "INSERT INTO user_service_vote (user_address, org_id, service_id, vote, comment, row_updated, row_created) " \
                        "VALUES (%s, %s, %s, %s, %s, %s, %s) " \
                        "ON DUPLICATE KEY UPDATE vote = %s, comment = %s, row_updated = %s"
                q_params = [usr_addr, org_id, srvc_id, vote, comment, curr_dt, curr_dt, vote, comment, curr_dt]
                res = self.repo.execute(query, q_params)
                print(res)
            else:
                raise Exception("signature of the vote is not valid.")
        except Exception as e:
            print(repr(e))
            raise e
        return True

    def get_curated_services(self):
        try:
            services = self.repo.execute(
                "SELECT * FROM service S, service_metadata M WHERE S.row_id = M.service_row_id AND S.is_curated = 1")
            groups = self.repo.execute("SELECT G.*, E.* FROM service S, service_group G, service_endpoint E WHERE " \
                                       "G.group_id = E.group_id AND G.service_row_id = S.row_id AND " \
                                       "E.service_row_id = S.row_id AND S.is_curated = 1")
            tags = self.repo.execute(
                "SELECT T.* FROM service S, service_tags T WHERE T.service_row_id = S.row_id AND S.is_curated = 1")
            grouped_services = self.__merge_service_data(services, groups, tags)
        except Exception as e:
            print(repr(e))
            raise e
        return grouped_services

    def get_profile_details(self, user_address):
        try:
            mpe_details = list()
            qry = "SELECT  G.org_id, D.display_name, M.* FROM mpe_channel M, service_group G ,service_metadata D, " \
                  "organization O WHERE M.groupId = G.group_id AND M.recipient = G.payment_address AND " \
                  "D.service_row_id =  G.service_row_id AND O.org_id = G.org_id AND sender = %s "
            channel_details = self.repo.execute(qry, (user_address))
            for detail in channel_details:
                mpe_details.append(self.obj_utils.clean_row(detail))
        except Exception as e:
            print(repr(e))
            raise e
        return mpe_details

    def __merge_service_data(self, services, groups, tags):
        tag_map = self.__map_to_service(tags)
        groups_map = self.__map_to_service(groups)
        for service in services:
            self.obj_utils.clean_row(service)
            service_row_id = service['service_row_id']
            service['groups'] = self.__get_group_with_endpoints(groups_map[service_row_id])
            if service_row_id in tag_map:
                service['tags'] = [tag['tag_name'] for tag in tag_map[service_row_id]]
            else:
                service['tags'] = []

        return services

    def __map_to_service(self, rows):
        map = dict()
        for row in rows:
            service_id = row['service_row_id']
            if service_id not in map:
                map[service_id] = list()
            map[service_id].append(row)
        return map

    def __get_group_with_endpoints(self, groups):
        segregated_groups = dict()
        for group in groups:
            group_name = group['group_name']
            if group_name not in segregated_groups:
                group_details = dict()
                group_details['endpoints'] = list()
                segregated_groups[group_name] = group_details
            else:
                group_details = segregated_groups[group_name]

            group_details['payment_address'] = group['payment_address']
            group_details['group_id'] = group['group_id']
            group_details['endpoints'].append(group['endpoint'])
        return segregated_groups
