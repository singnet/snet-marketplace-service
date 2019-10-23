
class PaymentInitiateFailed(Exception):
    pass


class WalletCreationFailed(Exception):
    pass


class ChannelCreationFailed(Exception):
    def __init__(self, message, wallet_details=None):
        super().__init__(message)
        self.wallet_details = wallet_details

    def get_wallet_details(self):
        return self.wallet_details


class FundChannelFailed(Exception):
    pass
