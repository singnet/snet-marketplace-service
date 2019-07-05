class ProxyAccount:
    def __init__(self, address, signer_address, signer_private_key):
        self.address = address
        self.signer_address = signer_address
        self.signer_private_key = signer_private_key


class ProxyChannelManagementStrategy:
    def __init__(self, sdk_context, block_offset=0, call_allowance=1):
        self.sdk_context = sdk_context
        self.block_offset = block_offset
        self.call_allowance = call_allowance
        self.starting_block_no = 5900638
        self.signer_private_key = self.sdk_context._config["signer_private_key"]
        self.signer_address = self.sdk_context._config["signer_address"]
        self.dapp_user_address = self.sdk_context._config["dapp_user_address"]

    def load_open_channels(self, service_client):

        account = ProxyAccount(self.dapp_user_address,
                               self.signer_address, self.signer_private_key)
        payment_channels = self.sdk_context.mpe_contract.get_past_open_channels(account, service_client,
                                                                                self.starting_block_no)
        return payment_channels

    def select_channel(self, service_client):
        payment_channels = self.load_open_channels(service_client)
        payment_channel = None
        for rec in payment_channels:
            if rec.account.address == self.dapp_user_address and rec.account.signer_address == self.signer_address:
                payment_channel = rec
        if payment_channel is not None:
            payment_channel.sync_state()
            return payment_channel
        raise Exception(
            "Unable to find Channel for given address %s.", self.dapp_user_address)
