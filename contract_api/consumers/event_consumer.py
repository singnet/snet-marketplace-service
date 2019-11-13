
class EventConsumer(object):

    def _comapre_assets_and_push_to_s3(self, existing_assets_hash, new_assets_hash, existing_assets_url, org_id,
                                       service_id):
        """

        :param existing_assets_hash: contains asset_type and its has value stored in ipfs
        :param new_assets_hash:  contains asset type and its updated hash value in ipfs
        :param existing_assets_url:  contains asset type and s3_url value for given asset_type
        :param org_id:
        :param service_id:
        :return: dict of asset_type and new_s3_url
        """
        # this function compare assets and deletes and update the new assets

        assets_url_mapping = {}

        if not existing_assets_hash:
            existing_assets_hash = {}
        if not existing_assets_url:
            existing_assets_url = {}
        if not new_assets_hash:
            new_assets_hash = {}

        for new_asset_type, new_asset_hash in new_assets_hash.items():

            if isinstance(new_asset_hash, list):
                # if this asset_type contains list of assets than remove all existing assetes from s3 and add all new assets to s3
                #
                new_urls_list = []

                # remove all existing assets if exits
                if new_asset_type in existing_assets_url:
                    for url in existing_assets_url[new_asset_type]:
                        self.s3_util.delete_file_from_s3(url)

                # add new files to s3 and update the url
                for hash in new_assets_hash[new_asset_type]:
                    new_urls_list.append(
                        self._push_asset_to_s3_using_hash(hash, org_id, service_id))

                assets_url_mapping[new_asset_type] = new_urls_list

            elif isinstance(new_asset_hash, str):
                # if this asset_type has single value
                if new_asset_type in existing_assets_hash and existing_assets_hash[new_asset_type] == new_asset_hash:
                    # file is not updated , add existing url
                    assets_url_mapping[new_asset_type] = existing_assets_url[new_asset_type]

                else:
                    if new_asset_type in existing_assets_url:
                        url_of_file_to_be_removed = existing_assets_url[new_asset_type]
                        self.s3_util.delete_file_from_s3(
                            url_of_file_to_be_removed)

                    hash_of_file_to_be_pushed_to_s3 = new_assets_hash[new_asset_type]

                    assets_url_mapping[new_asset_type] = self._push_asset_to_s3_using_hash(
                        hash_of_file_to_be_pushed_to_s3, org_id, service_id)

            else:
                print(
                    "unknown type assets for org_id %s  service_id %s", org_id, service_id)

        return assets_url_mapping



    def on_event(self, event):
        pass
