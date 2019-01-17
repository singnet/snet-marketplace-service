import datetime
import decimal

from common.repository import Repository

IGNORED_LIST = ['row_id', 'row_created', 'row_updated']


class Service:
    def __init__(self, net_id):
        self.netId = net_id
        self.repo = Repository(self.netId)

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

            self.__clean(status)
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
            self.__clean(votes)
            for rec in votes:
                org_id = rec['org_id']
                service_id = rec['service_id']
                user_vote_dict[org_id] = {}
                user_vote_dict[org_id][service_id] = {'user_address': rec['user_address'],
                                                      'org_id': rec['org_id'],
                                                      'service_id': service_id}
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
            for org_id in votes.keys():
                srvcs_data = votes[org_id]
                for service_id in srvcs_data.keys():
                    user = {}
                    user.update(votes[org_id][service_id])
                    user['up_vote_count'] = count_details[org_id].get(service_id).get(1, 0)
                    user['down_vote_count'] = count_details[org_id].get(service_id).get(0, 0)
                    vote_list.append(user)
        except Exception as e:
            print(repr(e))
            raise e
        return vote_list

    def set_user_vote(self, vote_info_dict):
        try:
            vote = -1
            if vote_info_dict['up_vote']:
                vote = 1
            elif vote_info_dict['down_vote']:
                vote = 0
            query = "Insert into user_service_vote (user_address, org_id, service_id, vote, row_created) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE VOTE = %s"
            q_params = [vote_info_dict['user_address'], vote_info_dict['org_id'], vote_info_dict['service_id'], vote,
                        datetime.datetime.utcnow(), vote]
            res = self.repo.execute(query, q_params)
            print(res)
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
                mpe_details.append(self.__clean_row(detail))
        except Exception as e:
            print(repr(e))
            raise e
        return mpe_details

    def __merge_service_data(self, services, groups, tags):
        tag_map = self.__map_to_service(tags)
        groups_map = self.__map_to_service(groups)
        for service in services:
            self.__clean_row(service)
            service_row_id = service['service_row_id']
            print(service_row_id, groups_map)
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

    def __clean(self, value_list):
        for value in value_list:
            self.__clean_row(value)

    def __clean_row(self, row):
        for item in IGNORED_LIST:
            del row[item]

        for key in row:
            if isinstance(row[key], decimal.Decimal) or isinstance(row[key], datetime.datetime):
                row[key] = str(row[key])
            elif isinstance(row[key], bytes):
                if row[key] == b'\x01':
                    row[key] = 1
                elif row[key] == b'\x00':
                    row[key] = 0
                else:
                    raise Exception("Unsupported bytes object. Key " + str(key) + " value " + str(row[key]))

        return row
