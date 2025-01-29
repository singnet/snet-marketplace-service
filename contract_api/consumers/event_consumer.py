from common.logger import get_logger


logger = get_logger(__name__)


class EventConsumer:
    def __init__(self, s3_util):
        self._s3_util = s3_util

    def _compare_assets_and_push_to_s3(
        self, existing_assets_hash, new_assets_hash, existing_assets_url, org_id, service_id
    ):
        """
        Compare existing and new assets, push updated assets to S3, and remove outdated assets.

        :param existing_assets_hash: dict containing asset_type and its hash value stored in IPFS.
        :param new_assets_hash: dict containing asset_type and its updated hash value in IPFS.
        :param existing_assets_url: dict containing asset_type and S3 URL for the asset type.
        :param org_id: Organization ID.
        :param service_id: Service ID.
        :return: dict of asset_type and new S3 URLs.
        """
        assets_url_mapping = {}

        # Ensure input dictionaries are not None
        existing_assets_hash = existing_assets_hash or {}
        existing_assets_url = existing_assets_url or {}
        new_assets_hash = new_assets_hash or {}

        for new_asset_type, new_asset_hash in new_assets_hash.items():
            if isinstance(new_asset_hash, list):
                # Handle asset types with a list of assets
                new_urls_list = []

                # Remove all existing assets from S3 for this asset type
                if new_asset_type in existing_assets_url:
                    for url in existing_assets_url[new_asset_type]:
                        self._s3_util.delete_file_from_s3(url)

                # Upload all new assets to S3 and store their URLs
                for asset_hash in new_asset_hash:
                    new_urls_list.append(
                        self._push_asset_to_s3_using_hash(asset_hash, org_id, service_id)
                    )

                assets_url_mapping[new_asset_type] = new_urls_list

            elif isinstance(new_asset_hash, str):
                # Handle asset types with a single value
                if (
                    new_asset_type in existing_assets_hash
                    and existing_assets_hash[new_asset_type] == new_asset_hash
                ):
                    # Asset is unchanged; retain the existing S3 URL
                    assets_url_mapping[new_asset_type] = existing_assets_url[new_asset_type]
                else:
                    # Asset is updated; remove the existing file from S3 (if it exists)
                    if new_asset_type in existing_assets_url:
                        self._s3_util.delete_file_from_s3(existing_assets_url[new_asset_type])

                    # Push the updated asset to S3 and store its new URL
                    assets_url_mapping[new_asset_type] = self._push_asset_to_s3_using_hash(
                        new_asset_hash, org_id, service_id
                    )

            else:
                logger.error(
                    "Unknown asset type for org_id %s, service_id %s", org_id, service_id
                )

        return assets_url_mapping

    def on_event(self, event):
        pass
