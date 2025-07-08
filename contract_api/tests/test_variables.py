TEST_ORG_ID = "test_org"
TEST_SERVICE_ID = "test_service"

GET_SERVICE_RESPONSE = {
    "BASE": {'service_row_id': 10,
             'org_id': TEST_ORG_ID,
             'service_id': TEST_SERVICE_ID,
             'display_name': 'test_display_name',
             'description': 'test_description',
             'url': 'test_url',
             'json': '{"name":"test_name", "age":31, "city":"test_city"}',
             'model_hash': 'test_hash',
             'encoding': 'proto',
             'type': 'grpc',
             'mpe_address': 'test_mpe_address',
             'service_rating': {'rating': 0.0, 'total_users_rated': 0},
             'ranking': 1,
             'contributors': [{'name': 'dummy dummy', 'email_id': 'dummy@dummy.io'}],
             'short_description': 'short description',
             'demo_component_available': 0,
             'service_path': 'service_path',
             'hash_uri': 'test_ipfs_hash',
             'is_curated': 1,
             'service_email': 'email',
             'organization_name': TEST_SERVICE_ID,
             'owner_address': 'owner_add',
             'org_metadata_uri': 'uri',
             'org_email': 'email',
             'org_assets_url': {'url': 'google.com'},
             'org_description': 'description',
             'contacts': {},
             'is_available': 0,
             'groups': [],
             'tags': [],
             'media': [],
             "demo_component": {
                 'demo_component_url': '',
                 'demo_component_required': '',
                 'demo_component_status': '',
                 'demo_component_last_modified': ''
             },
             "demo_component_required": 0
             },
    "MEDIA": {
        'media': [
            {'service_row_id': 10, 'org_id': TEST_ORG_ID, 'service_id': TEST_SERVICE_ID,
             'url': 'test_media_s3_url',
             'order': 0, 'file_type': 'grpc-stub/nodejs', 'asset_type': 'grpc-stub',
             'alt_text': ''},
            {'service_row_id': 10, 'org_id': TEST_ORG_ID, 'service_id': TEST_SERVICE_ID,
             'url': 'https://test-s3-push', 'order': 5, 'file_type': 'image',
             'asset_type': 'hero_image', 'alt_text': 'data is missing'}
        ]}
}
