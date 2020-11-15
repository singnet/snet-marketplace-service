from unittest import TestCase
from unittest.mock import patch, Mock

from registry.application.services.file_service.file_service import FileService


class TestFileService(TestCase):

    @patch("boto3.resource", return_value=Mock(Bucket=Mock(return_value=Mock(objects=Mock(
        filter=Mock(return_value=Mock(delete=Mock(return_value=[
            {'Deleted': [{'Key': 'file_1'}, {'Key': 'file_2'}, {'Key': 'file_3'}, {'Key': 'file_4'}]}]))))))))
    def test_delete_all_success(self, mock_boto):
        org_uuid = "test_org_uuid"
        response = FileService().delete({"org_uuid": org_uuid, "type": "ORG_ASSETS"})
        self.assertDictEqual({'deleted': ['file_1', 'file_2', 'file_3', 'file_4'], 'errors': []}, response)

    def test_get_s3_bucket_and_prefix(self):
        org_uuid = "test_org_uuid"
        service_uuid = "test_service_uuid"
        bucket, prefix = FileService().get_s3_bucket_and_prefix({"org_uuid": org_uuid, "type": "ORG_ASSETS"})
        self.assertEqual("org_bucket", bucket)
        self.assertEqual("test_org_uuid/assets", prefix)

        bucket, prefix = FileService().get_s3_bucket_and_prefix({"org_uuid": org_uuid, "service_uuid": service_uuid,
                                                                 "type": "SERVICE_ASSETS"})
        self.assertEqual("org_bucket", bucket)
        self.assertEqual('test_org_uuid/services/test_service_uuid/assets', prefix)

        bucket, prefix = FileService().get_s3_bucket_and_prefix({"org_uuid": org_uuid, "service_uuid": service_uuid,
                                                                 "type": "SERVICE_PAGE_COMPONENTS"})
        self.assertEqual("org_bucket", bucket)
        self.assertEqual('test_org_uuid/services/test_service_uuid/component', prefix)

        bucket, prefix = FileService().get_s3_bucket_and_prefix({"org_uuid": org_uuid, "service_uuid": service_uuid,
                                                                 "type": "SERVICE_GALLERY_IMAGES"})
        self.assertEqual("org_bucket", bucket)
        self.assertEqual('test_org_uuid/services/test_service_uuid/assets', prefix)

        bucket, prefix = FileService().get_s3_bucket_and_prefix({"org_uuid": org_uuid, "service_uuid": service_uuid,
                                                                 "type": "SERVICE_PROTO_FILES"})
        self.assertEqual("org_bucket", bucket)
        self.assertEqual('test_org_uuid/services/test_service_uuid/proto', prefix)
