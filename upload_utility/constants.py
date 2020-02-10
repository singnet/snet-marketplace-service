UPLOAD_TYPE = {
    "ORG_ASSETS": {
        "required_query_params": ["org_id"],
        "bucket": "",
        "path": "{}/services/{}/assets/{}_asset.{}",
    },
    "SERVICE_ASSETS": {
        "required_query_params": ["service_id", "org_id"],
        "bucket": "",
        "path": "{}/services/{}/assets/{}_asset.{}",
    },
    "SERVICE_COMPONENTS": {
        "required_query_params": ["service_id", "org_id"],
        "bucket": "",
        "path": "{}/services/{}/assets/{}_component.{}",
    },
    "SERVICE_IMAGES": {
        "required_query_params": ["service_id", "org_id"],
        "bucket": "",
        "path": "{}/services/{}/assets/{}_asset.{}",
    }
}
