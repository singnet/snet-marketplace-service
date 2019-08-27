MPE_EVTS = ['ChannelOpen', 'ChannelClaim',
            'ChannelSenderClaim', 'ChannelExtend', 'ChannelAddFunds']
REG_EVTS = ['OrganizationCreated', 'OrganizationModified', 'OrganizationDeleted', 'ServiceCreated',
            'ServiceMetadataModified', 'ServiceTagsModified', 'ServiceDeleted']
COMMON_CNTRCT_PATH = './node_modules/singularitynet-platform-contracts'
REG_CNTRCT_PATH = COMMON_CNTRCT_PATH + '/abi/Registry.json'
MPE_CNTRCT_PATH = COMMON_CNTRCT_PATH + '/abi/MultiPartyEscrow.json'
REG_ADDR_PATH = COMMON_CNTRCT_PATH + '/networks/Registry.json'
MPE_ADDR_PATH = COMMON_CNTRCT_PATH + '/networks/MultiPartyEscrow.json'
EVNTS_LIMIT = "100"
