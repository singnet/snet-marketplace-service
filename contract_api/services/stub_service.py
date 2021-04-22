from common.s3_util import S3Util
from contract_api.config import PROTO_STUB_DOWNLOAD_DETAILS


def get_proto_stubs(org_id, service_id):
    key = PROTO_STUB_DOWNLOAD_DETAILS["key"].format(org_id, service_id)
    objects = S3Util(
        aws_access_key=PROTO_STUB_DOWNLOAD_DETAILS["access_key"],
        aws_secrete_key=PROTO_STUB_DOWNLOAD_DETAILS["secret_key"]
        ).\
        get_objects_from_s3(bucket=PROTO_STUB_DOWNLOAD_DETAILS["bucket"], key=key)
    proto_stubs = []
    for obj in objects:
        proto_stubs.append(PROTO_STUB_DOWNLOAD_DETAILS["download_url"].format(obj["Key"]))
    return proto_stubs
