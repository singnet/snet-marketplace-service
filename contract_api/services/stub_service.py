from common.boto_utils import BotoUtils
from contract_api.config import PROTO_STUB_s3_URL


def get_proto_stubs(org_id, service_id):
    boto_utils = BotoUtils(region_name=None)
    bucket, key = boto_utils.get_bucket_and_key_from_url(PROTO_STUB_s3_URL.format(org_id, service_id))
    objects = boto_utils.get_objects_from_s3(bucket=bucket, key=key)
    proto_stubs = []
    for obj in objects:
        proto_stubs.append(f"https://{bucket}.s3.amazonaws.com/{obj['Key']}")
    return proto_stubs
