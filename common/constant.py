import os
IPFS_URL = {
    'url': 'ipfs.singularitynet.io',
    'port': '80',
    'protocol': 'http'
}
NETWORKS = {
    1: {
        'name': 'mainnet',
        'ws_provider': 'wss://mainnet.infura.io/ws',
        'http_provider': 'https://mainnet.infura.io',
        'db':{}
    },
    3: {
        'name': 'Ropsten',
        'ws_provider': 'wss://ropsten.infura.io/ws',
        'http_provider': 'https://ropsten.infura.io',
        'db':{}
    },
    42: {
        'name': 'Kovan',
        'ws_provider': 'wss://kovan.infura.io/ws',
        'http_provider': 'https://kovan.infura.io',
        'db': {'DB_HOST': os.environ['DB_HOST'],
               'DB_USER': os.environ['DB_USER'],
               'DB_PASSWORD': os.environ['DB_PASSWORD'],
               'DB_NAME': os.environ['DB_NAME'],
               'DB_PORT': int(os.environ['DB_PORT'])
               }
    }
}
MPE_EVTS = ['ChannelOpen', 'ChannelClaim', 'ChannelSenderClaim', 'ChannelExtend', 'ChannelAddFunds']
REG_EVTS = ['OrganizationCreated', 'OrganizationModified', 'OrganizationDeleted', 'ServiceCreated',
            'ServiceMetadataModified', 'ServiceTagsModified', 'ServiceDeleted']
REG_CNTRCT_PATH = './singularitynet-platform-contracts/abi/Registry.json'
MPE_CNTRCT_PATH = './singularitynet-platform-contracts/abi/MultiPartyEscrow.json'
REG_ADDR_PATH = './singularitynet-platform-contracts/networks/Registry.json'
MPE_ADDR_PATH = './singularitynet-platform-contracts/networks/MultiPartyEscrow.json'

ERROR_MSG = {
    1001: "Error Code: {} Network Id is Invalid !!",
    1002: "Error Code: {} Unable to process _init_w3.",
    9001: "Missing error code {} ",
    "default": "Unable to process error."
}

EVNTS_LIMIT = "100"
