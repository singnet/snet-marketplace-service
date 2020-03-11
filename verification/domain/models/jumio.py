
class JumioVerification:
    def __init__(self, verification_id, username, user_reference_id, verification_status, transaction_status,
                 created_at, redirect_url=None, jumio_reference_id=None, transaction_date=None, callback_date=None,
                 reject_reason=None):
        self.verification_id = verification_id
        self.username = username
        self.user_reference_id = user_reference_id
        self.verification_status = verification_status
        self.transaction_status = transaction_status
        self.created_at = created_at
        if reject_reason is None:
            self.reject_reason = {}
        else:
            self.reject_reason = reject_reason
        self.redirect_url = redirect_url
        self.jumio_reference_id = jumio_reference_id
        self.transaction_date = transaction_date
        self.callback_date = callback_date

    def to_dict(self):
        return {
            "username": self.username,
            "verification_status": self.verification_status,
            "transaction_status": self.transaction_status
        }
