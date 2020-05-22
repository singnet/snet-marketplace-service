import json

ORG_ADDRESS = {
    "mail_address_same_hq_address": True,
    "addresses": [
        {
            "address_type": "headquarters_address",
            "street_address": "F102",
            "apartment": "ABC Apartment",
            "city": "TestCity",
            "state": "state",
            "pincode": "123456",
            "country": "TestCountry"
        },
        {
            "address_type": "mailing_address",
            "street_address": "F102",
            "apartment": "ABC Apartment",
            "city": "TestCity",
            "state": "state",
            "pincode": "123456",
            "country": "TestCountry"
        }
    ]
}
ORIGIN = "PUBLISHER"
ORG_CONTACTS = [
    {
        "contact_type": "support",
        "email_id": "abcd@abcdef.com",
        "phone": "1234567890"
    },
    {
        "contact_type": "org",
        "email_id": "dummy@abcdef.com",
        "phone": "1234567890"
    }
]
ORG_GROUPS = json.dumps([
    {
        'name': 'my-group',
        'id': 'IN2fDELdv5zKzgKgFpXVBvNKBhbIc0zYoA750wJ/s60=',
        'payment_address': '0x123',
        'payment_config': {
            'payment_channel_storage_type': 'etcd',
            'payment_expiration_threshold': 40320,
            'payment_channel_storage_client': {
                'endpoints': ['http://127.0.0.1:2379'],
                'request_timeout': '3s',
                'connection_timeout': '5s'}
        }
    },
    {
        'name': 'group-123',
        'id': 'S2fjwWLCjHsoheHagBIQ6893ipA8AV97hdAdqnrT/Fk=',
        'payment_address': '0x123',
        'payment_config': {
            'payment_channel_storage_type': 'etcd',
            'payment_expiration_threshold': 40320,
            'payment_channel_storage_client': {
                'endpoints': ['http://127.0.0.1:2379'],
                'request_timeout': '3s',
                'connection_timeout': '5s'}
        }
    }
])

ORG_PAYLOAD_MODEL = json.dumps({
    "org_id": "",
    "org_uuid": "",
    "org_name": "test_org",
    "org_type": "individual",
    "metadata_ipfs_uri": "ipfs://Q12PWP",
    "duns_no": "123456789",
    "origin": ORIGIN,
    "description": "this is the dummy org for testcases",
    "short_description": "this is the short description",
    "url": "https://dummy.dummy",
    "contacts": ORG_CONTACTS,
    "assets": {
        "hero_image": {
            "url": "",
            "ipfs_hash": ""
        }
    },
    "org_address": {
        "mail_address_same_hq_address": False,
        "addresses": []
    },
    "groups": json.loads(ORG_GROUPS),
    "state": {}
})

ORG_RESPONSE_MODEL = json.dumps({
    "org_name": "test_org",
    "org_id": "",
    "org_uuid": "",
    "org_type": "individual",
    "description": "this is the dummy org for testcases",
    "short_description": "this is the short description",
    "url": "https://dummy.dummy",
    "duns_no": "123456789",
    "origin": ORIGIN,
    "contacts": [
        {
            "phone": "1234567890",
            "email_id": "abcd@abcdef.com",
            "contact_type": "support"
        },
        {
            "phone": "1234567890",
            "email_id": "dummy@abcdef.com",
            "contact_type": "org"
        }
    ],
    "assets": {
        "hero_image": {
            "url": "",
            "ipfs_hash": ""
        }
    },
    "metadata_ipfs_uri": "ipfs://Q12PWP",
    "groups": json.loads(ORG_GROUPS),
    "org_address": {
        "mail_address_same_hq_address": False,
        "addresses": []
    },
    "state": {}
})
