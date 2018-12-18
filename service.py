import datetime
import decimal
import json

from repository import Repository

IGNORED_LIST = ['row_id', 'row_created', 'row_updated']


class Service:
    repo = Repository()

    def get_group_info(self):
        service_status_dict = {}
        try:
            status = self.repo.execute(
                " select g.*, s.endpoint, s.is_available, s.last_check_timestamp "
                " from service_group g, service_status s "
                " where g.service_id = s.service_id and g.group_id = s.group_id and g.service_id in (select row_id from service where is_curated = 1)")

            self.__clean(status)
            for rec in status:
                srvc_id = rec['service_id']
                grp_id = rec['group_id']
                endpoint_value = {'is_available': rec['is_available'],
                                  'last_check_timestamp': rec['last_check_timestamp']}
                endpoint = rec['endpoint']
                if srvc_id not in service_status_dict.keys():
                    service_status_dict[srvc_id] = {}
                if grp_id not in service_status_dict.get(srvc_id).keys():
                    service_status_dict[srvc_id][grp_id] = {}
                    service_status_dict[srvc_id][grp_id]['payment_address'] = rec['payment_address']
                    service_status_dict[srvc_id][grp_id]['endpoint'] =  {}
                service_status_dict[srvc_id][grp_id]['endpoint'].update(
                    {endpoint: endpoint_value})
            service_status = self.process_service_status(service_status_dict)
        except Exception as e:
            print(repr(e))
            raise e
        return service_status

    def process_service_status(self, service_status_dict):
        service_status = []
        for service_id in service_status_dict.keys():
            is_available = 0
            grps_dict = service_status_dict.get(service_id, {})
            grps = []
            for grp_id in grps_dict.keys():
                grp_available = 0
                endpts_dict = grps_dict.get(grp_id, {})
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
                             'payment_address':endpts_dict.get('payment_address', '')})
            service_status.append({
                'service_id': service_id,
                'groups': grps,
                'is_available': is_available
            })
        return service_status

    def fetch_total_count(self):
        user_vote_count_dict = {}
        try:
            count_details = self.repo.execute(
                "SELECT service_name, vote, Count(*) AS count FROM user_service_vote GROUP BY vote, service_name")
            for rec in count_details:
                service_name = rec.get('service_name', '')
                vote = rec.get('vote', '')
                count = rec.get('count', '')
                if not service_name in user_vote_count_dict.keys():
                    user_vote_count_dict[service_name] = {}
                user_vote_count_dict[service_name][vote] = count
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
                service_name = rec['service_name']
                user_vote_dict[service_name] = {'user_address': rec['user_address'],
                                                'service_name': service_name}
                user_vote_dict[service_name].update(self.vote_mapping(rec['vote']))

        except Exception as e:
            print(repr(e))
            raise e
        return user_vote_dict

    def get_user_vote(self, user_address):
        vote_list = []
        try:
            count_details = self.fetch_total_count()
            votes = self.fetch_user_vote(user_address)
            for service_name in votes.keys():
                user = {}
                user.update(votes[service_name])
                user['up_vote_count'] = count_details.get(service_name).get(1, 0)
                user['down_vote_count'] = count_details.get(service_name).get(0, 0)
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
            query = "Insert into user_service_vote (user_address, organization_name, service_name, vote) VALUES ('{}','{}','{}',{}) ON DUPLICATE KEY UPDATE VOTE = {}"
            query = query.format(
                vote_info_dict['user_address'],
                vote_info_dict['organization_name'],
                vote_info_dict['service_name'],
                vote,
                vote)
            res = self.repo.execute(query)
            print(res)
        except Exception as e:
            print(repr(e))
            raise e
        return True

    def get_curated_services(self):
        try:
            services = self.repo.execute(
                "select * from service s, service_metadata m where s.row_id = m.service_id and s.is_curated = 1")
            groups = self.repo.execute("select g.*, e.* from service s, service_group g, service_endpoint e "
                                       "where g.group_name = e.group_name and g.service_id = s.row_id "
                                       "and e.service_id = s.row_id and s.is_curated = 1")
            tags = self.repo.execute(
                "select t.* from service s, service_tags t where t.service_id = s.row_id and s.is_curated = 1")
            grouped_services = self.__merge_service_data(services, groups, tags)
        except Exception as e:
            print(repr(e))
            raise e
        return grouped_services

    def get_profile_details(self, user_address):
        try:
            mpe_details = list()

            channel_details = self.repo.execute("select * from mpe_channel where sender = %s", (user_address))
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
            service_id = service['service_id']
            service['groups'] = self.__get_group_with_endpoints(groups_map[service_id])
            if service_id in tag_map:
                service['tags'] = [tag['tag_name'] for tag in tag_map[service_id]]
            else:
                service['tags'] = []

        return services

    def __map_to_service(self, rows):
        map = dict()
        for row in rows:
            service_id = row['service_id']
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
