



class ServiceService:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_utils = Utils()

    # is used in handler
    def get_filter_attribute(self, attribute):
        """ Method to fetch filter metadata based on attribute."""
        try:
            filter_attribute = {"attribute": attribute, "values": []}
            if attribute == "tag_name":
                filter_data = self.repo.execute(
                    "SELECT DISTINCT tag_name AS 'key', tag_name AS 'value' FROM service_tags T, service S "
                    "WHERE S.row_id = T.service_row_id AND S.is_curated = 1")
            elif attribute == "display_name":
                filter_data = self.repo.execute(
                    "SELECT DISTINCT S.service_id AS 'key',display_name AS 'value' FROM service_metadata M, service S "
                    "WHERE S.row_id = M.service_row_id AND S.is_curated = 1")
            elif attribute == "org_id":
                filter_data = self.repo.execute(
                    "SELECT DISTINCT O.org_id AS 'key' ,O.organization_name AS 'value' from organization O, service S "
                    "WHERE S.org_id = O.org_id AND S.is_curated = 1")
            else:
                return filter_attribute
            for rec in filter_data:
                filter_attribute["values"].append(rec)

            return filter_attribute
        except Exception as e:
            logger.exception(repr(e))
            raise e

    # is used in handler
    def get_services(self, qry_param):
        try:
            fields_mapping = {"display_name": "display_name",
                              "tag_name": "tag_name", "org_id": "org_id"}
            s = qry_param.get('s', 'all')
            q = qry_param.get('q', '')
            offset = qry_param.get('offset', GET_ALL_SERVICE_OFFSET_LIMIT)
            limit = qry_param.get('limit', GET_ALL_SERVICE_LIMIT)
            sort_by = fields_mapping.get(
                qry_param.get('sort_by', None), "ranking")
            order_by = qry_param.get('order_by', 'desc')
            if order_by.lower() != "desc":
                order_by = "asc"

            sub_qry = self._prepare_subquery(s = s, q = q, fm = fields_mapping)
            logger.info(f"get_all_srvcs::sub_qry: {sub_qry}")

            filter_query = ""
            values = []
            if qry_param.get("filters", None) is not None:
                filter_query, values = self._filters_to_query(
                    qry_param.get("filters"))
            logger.info(f"get_all_srvcs::filter_query: {filter_query}, values: {values}")
            total_count = self._get_total_count(
                sub_qry = sub_qry, filter_query = filter_query, values = values)
            if total_count == 0:
                return self._search_response_format(total_count, offset, limit, [])
            q_dta = self._search_query_data(sub_qry = sub_qry, sort_by = sort_by, order_by = order_by,
                                            offset = offset, limit = limit, filter_query = filter_query,
                                            values = values)
            return self._search_response_format(total_count, offset, limit, q_dta)
        except Exception as e:
            logger.exception(repr(e))
            raise e

    # is used in handler
    def get_service(self, org_id, service_id):
        try:
            """ Method to get all service data for given org_id and service_id"""
            tags = []
            org_groups_dict = {}
            basic_service_data = self.repo.execute(
                "SELECT M.row_id, M.service_row_id, M.org_id, M.service_id, M.display_name, M.description, M.url, M.json, M.model_hash, M.encoding, M.`type`,"
                " M.mpe_address,M.service_rating, M.ranking, M.contributors, M.short_description, M.demo_component_available,"
                " S.*, O.org_id, O.organization_name, O.owner_address, O.org_metadata_uri, O.org_email, "
                "O.org_assets_url, O.description as org_description, O.contacts "
                "FROM service_metadata M, service S, organization O "
                "WHERE O.org_id = S.org_id AND S.row_id = M.service_row_id AND S.org_id = %s "
                "AND S.service_id = %s AND S.is_curated = 1", [org_id, service_id])
            if len(basic_service_data) == 0:
                return []
            self.obj_utils.clean(basic_service_data)

            org_group_data = self.repo.execute(
                "SELECT * FROM org_group WHERE org_id = %s", [org_id])
            self.obj_utils.clean(org_group_data)

            service_group_data = self._get_group_info(
                org_id = org_id, service_id = service_id)

            tags = self.repo.execute("SELECT tag_name FROM service_tags WHERE org_id = %s AND service_id = %s",
                                     [org_id, service_id])

            service_media = service_media_repo.get_service_media(org_id = org_id, service_id = service_id)
            media = [media_data.to_dict() for media_data in service_media]
            result = basic_service_data[0]

            self._convert_service_metadata_str_to_json(result)

            offchain_service_configs = Registry._prepare_offchain_service_attributes(org_id, service_id)

            for rec in org_group_data:
                org_groups_dict[rec['group_id']] = {
                    "payment": json.loads(rec["payment"])}

            is_available = 0
            # Hard Coded Free calls in group data
            for rec in service_group_data:
                rec["free_calls"] = rec.get("free_calls", 0)
                if is_available == 0:
                    endpoints = rec['endpoints']
                    for endpoint in endpoints:
                        is_available = endpoint['is_available']
                        if is_available == 1:
                            break
                rec.update(org_groups_dict.get(rec['group_id'], {}))

            result.update(
                {"is_available": is_available, "groups": service_group_data, "tags": tags, "media": media})
            result.update(offchain_service_configs)
            return result
        except Exception as e:
            logger.exception(repr(e))
            raise e

    # is used in handler
    @staticmethod
    def save_offchain_service_attribute(org_id, service_id, new_offchain_attributes):
        updated_offchain_attributes = {}
        if "demo_component" in new_offchain_attributes:
            new_demo_component = ServiceFactory.create_demo_component_domain_model(
                new_offchain_attributes["demo_component"])
            # publish and update demo only on change_in_demo_component = 1 and required = 1
            if new_offchain_attributes["demo_component"].get("change_in_demo_component", 0) and \
                    new_demo_component.demo_component_required:
                new_demo_component.demo_component_url = ServiceService.publish_demo_component(
                    new_demo_component.demo_component_url
                )
                new_demo_component.demo_component_status = BuildStatus.PENDING
            # update and save new changes
            updated_offchain_attributes = OffchainServiceAttribute(
                org_id = org_id,
                service_id = service_id,
                attributes = new_demo_component.to_dict()
            )
            offchain_service_attribute = offchain_service_config_repo.save_offchain_service_attribute(
                updated_offchain_attributes)
            updated_offchain_attributes = offchain_service_attribute.to_dict()
        return updated_offchain_attributes

    @staticmethod
    def publish_demo_component(org_id, service_id, demo_file_url):
        # download zip component file
        root_directory = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        if not Path.exists(Path(root_directory)):
            os.mkdir(root_directory)
        component_name = download_file_from_url(demo_file_url, root_directory)

        # extract the zip file
        extracted_file = os.path.join(root_directory, component_name.split(".")[0].split("_")[1])
        extract_zip_file(os.path.join(root_directory, component_name), extracted_file)
        # prepare tar file
        output_path = os.path.join(root_directory, component_name.split(".")[0].split("_")[1] + '.tar.gz')
        make_tarfile(source_dir = extracted_file, output_filename = output_path)

        # upload demo file to s3 and demo attributes
        key = f"assets/{org_id}/{service_id}/component.tar.gz"
        boto_utils.s3_upload_file(filename = output_path, bucket = ASSETS_COMPONENT_BUCKET_NAME, key = key)
        new_demo_url = f"https://{ASSETS_COMPONENT_BUCKET_NAME}.s3.amazonaws.com/{key}"
        return new_demo_url

    # is used in handler
    def curate_service(self, org_id, service_id, curated):
        service_repo = ServiceRepository(self.repo)
        if str(curated).lower() == "true":
            service_repo.curate_service(org_id, service_id, 1)
        elif str(curated).lower() == "false":
            service_repo.curate_service(org_id, service_id, 0)
        else:
            Exception("Invalid curation flag")

    def _prepare_subquery(self, s, q, fm):
        try:
            sub_qry = ""
            if s == "all":
                for rec in fm:
                    sub_qry += fm[rec] + " LIKE '%" + str(q) + "%' OR "
                sub_qry = sub_qry[:-3] if sub_qry.endswith("OR ") else sub_qry
            else:
                sub_qry += fm[s] + " LIKE '%" + str(q) + "%' "
            return sub_qry.replace("org_id", "M.org_id")
        except Exception as err:
            raise err

    def _filters_to_query(self, filter_json):
        query = ""
        filters = []
        values = []
        for filter in filter_json:
            filters.append(Filter(filter))
        for filter in filters:
            query += "("
            for filter_condition in filter.get_filter().get("filter"):
                sub_query, value = self._filter_condition_to_query(
                    filter_condition)
                values += value
                query = query + "(" + sub_query + ") AND "
            if query.endswith(" AND "):
                query = query[:-5]
            query += ") OR "
        if query.endswith(" OR "):
            query = query[:-4]
        return query, values

    def _filter_condition_to_query(self, filter_condition):
        value = []
        if filter_condition.attr in ["org_id", "service_id"]:
            filter_condition.attr = "M." + filter_condition.attr
        if filter_condition.operator == "=":
            value = filter_condition.value
            return '%s %s"%s"' % (filter_condition.attr, filter_condition.operator, "%s"), value
        if filter_condition.operator == "IN":
            value = filter_condition.value
            return '%s %s %s' % (
                filter_condition.attr, filter_condition.operator, "(" + (("%s,") * len(value))[:-1] + ")"), value
        if filter_condition.operator == "BETWEEN":
            value = filter_condition.value
            return '%s %s %s AND %s' % (filter_condition.attr, filter_condition.operator, "%s", "%s"), value

    def _get_total_count(self, sub_qry, filter_query, values):
        try:
            if filter_query != "":
                filter_query = " AND " + filter_query
            search_count_query = "SELECT count(*) as search_count FROM service A, (SELECT DISTINCT M.org_id, M.service_id FROM " \
                                 "service_metadata M LEFT JOIN service_tags T ON M.service_row_id = T.service_row_id WHERE (" \
                                 + sub_qry.replace('%',
                                                   '%%') + ")" + filter_query + ") B WHERE A.service_id = B.service_id " \
                                                                                "AND A.org_id = B.org_id AND A.is_curated = 1 "

            res = self.repo.execute(search_count_query, values)
            return res[0].get("search_count", 0)
        except Exception as err:
            raise err

    def _search_response_format(self, tc, offset, limit, rslt):
        try:
            return {"total_count": tc, "offset": offset, "limit": limit, "result": rslt}
        except Exception as err:
            raise err

    def _search_query_data(self, sub_qry, sort_by, order_by, offset, limit, filter_query, values):
        try:
            if filter_query != "":
                filter_query = " AND " + filter_query
            srch_qry = "SELECT * FROM service A, (SELECT M.org_id, M.service_id, group_concat(T.tag_name) AS tags FROM " \
                       "service_metadata M LEFT JOIN service_tags T ON M.service_row_id = T.service_row_id " \
                       "LEFT JOIN service_endpoint E ON M.service_row_id = E.service_row_id WHERE (" \
                       + sub_qry.replace('%', '%%') + ")" + filter_query + \
                       " GROUP BY M.org_id, M.service_id ORDER BY E.is_available DESC, " + sort_by + " " + order_by + \
                       " ) B WHERE A.service_id = B.service_id AND A.org_id=B.org_id AND A.is_curated= 1 LIMIT %s , %s"

            qry_dta = self.repo.execute(
                srch_qry, values + [int(offset), int(limit)])
            org_srvc_tuple = ()
            rslt = {}
            for rec in qry_dta:
                org_id = rec['org_id']
                service_id = rec['service_id']
                tags = rec['tags']
                org_srvc_tuple = org_srvc_tuple + ((org_id, service_id),)
                if org_id not in rslt.keys():
                    rslt[org_id] = {}
                if service_id not in rslt[org_id].keys():
                    rslt[org_id][service_id] = {}
                rslt[org_id][service_id]["tags"] = tags
            qry_part = " AND (S.org_id, S.service_id) IN " + \
                       str(org_srvc_tuple).replace(',)', ')')
            qry_part_where = " AND (org_id, service_id) IN " + \
                             str(org_srvc_tuple).replace(',)', ')')
            logger.info(f"qry_part :: {qry_part}")
            sort_by = sort_by.replace("org_id", "M.org_id")
            if org_srvc_tuple:
                services = self.repo.execute(
                    "SELECT DISTINCT M.row_id, M.service_row_id, M.org_id, M.service_id, M.display_name, M.description, M.url, M.json, M.model_hash, M.encoding, M.`type`,"
                    " M.mpe_address,M.service_rating, M.ranking, M.contributors, M.short_description,"
                    "O.organization_name,O.org_assets_url FROM service_endpoint E, service_metadata M, service S "
                    ", organization O WHERE O.org_id = S.org_id AND S.row_id = M.service_row_id AND "
                    "S.row_id = E.service_row_id " + qry_part + "ORDER BY E.is_available DESC, " + sort_by + " " + order_by)
                services_media = self.repo.execute(
                    "select org_id ,service_id,file_type ,asset_type,url,alt_text ,`order`,row_id from service_media where asset_type = 'hero_image' " + qry_part_where)
            else:
                services = []
                services_media = []
            obj_utils = Utils()
            obj_utils.clean(services)
            available_service = self._get_is_available_service()
            for rec in services:
                self._convert_service_metadata_str_to_json(rec)

                org_id = rec["org_id"]
                service_id = rec["service_id"]
                tags = []
                is_available = 0
                if rslt.get(org_id, {}).get(service_id, {}).get("tags", None) is not None:
                    tags = rslt[org_id][service_id]["tags"].split(",")
                if (org_id, service_id) in available_service:
                    is_available = 1
                asset_media = []
                if len(services_media) > 0:
                    asset_media = [x for x in services_media if x['service_id'] == service_id]
                    if len(asset_media) > 0:
                        asset_media = asset_media[0]
                rec.update({"tags": tags})
                rec.update({"is_available": is_available})
                rec.update({"media": asset_media})

            return services
        except Exception as err:
            raise err

    def _convert_service_metadata_str_to_json(self, record):
        record["service_rating"] = json.loads(record["service_rating"])
        record["org_assets_url"] = json.loads(record["org_assets_url"])
        record["contributors"] = json.loads(record.get("contributors", "[]"))
        record["contacts"] = json.loads(record.get("contacts", "[]"))

        if record["contacts"] is None:
            record["contacts"] = []
        if record["contributors"] is None:
            record["contributors"] = []

    def _get_is_available_service(self):
        try:
            available_service = []
            srvc_st_dta = self.repo.execute(
                "SELECT DISTINCT org_id, service_id  FROM service_endpoint WHERE is_available = 1")
            for rec in srvc_st_dta:
                available_service.append((rec['org_id'], rec['service_id']), )
            return available_service
        except Exception as e:
            logger.exception(repr(e))
            raise e

    def _get_group_info(self, org_id, service_id):
        try:
            group_data = self.repo.execute(
                "SELECT G.*, E.* FROM service_group G INNER JOIN service_endpoint E ON G.group_id = E.group_id AND G.service_row_id = E.service_row_id WHERE "
                "G.org_id = %s AND G.service_id = %s ", [org_id, service_id])
            self.obj_utils.clean(group_data)
            groups = {}
            for rec in group_data:
                group_id = rec['group_id']
                if group_id not in groups.keys():
                    groups = {group_id: {"group_id": rec['group_id'],
                                         "group_name": rec['group_name'],
                                         "pricing": json.loads(rec['pricing']),
                                         "endpoints": [],
                                         "free_calls": rec.get("free_calls", 0),
                                         "free_call_signer_address": rec.get("free_call_signer_address", "")
                                         }
                              }
                groups[group_id]['endpoints'].append({"endpoint": rec['endpoint'], "is_available":
                    rec['is_available'], "last_check_timestamp": rec["last_check_timestamp"]})
            return list(groups.values())
        except Exception as e:
            logger.exception(repr(e))
            raise e

    @staticmethod
    def _prepare_offchain_service_attributes(org_id, service_id):
        offchain_attributes = {}
        offchain_service_config_repo = OffchainServiceConfigRepository()
        offchain_service_config = offchain_service_config_repo.get_offchain_service_config(
            org_id = org_id,
            service_id = service_id
        )
        offchain_attributes_db = offchain_service_config.attributes
        demo_component_required = offchain_attributes_db.get("demo_component_required", 0)
        demo_component = service_factory.create_demo_component_domain_model(offchain_service_config.attributes)
        demo_component = demo_component.to_dict()
        # prepare format
        demo_last_modified = offchain_attributes_db.get("demo_component_last_modified", "")
        demo_component.update({"demo_component_last_modified": demo_last_modified if demo_last_modified else ""})
        offchain_attributes.update({"demo_component_required": demo_component_required})
        offchain_attributes.update({"demo_component": demo_component})
        return offchain_attributes