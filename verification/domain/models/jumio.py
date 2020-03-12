from verification.constants import JumioVerificationStatus, JumioTransactionStatus


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
            "transaction_status": self.transaction_status,
            "reject_reason": self.construct_reject_reason()
        }

    def has_reject_reason(self):
        if self.verification_status in [JumioVerificationStatus.DENIED_FRAUD.value,
                                        JumioVerificationStatus.ERROR_NOT_READABLE_ID.value]:
            return True
        return False

    def setup_transaction_status(self):
        if self.verification_status == JumioVerificationStatus.NO_ID_UPLOADED.value:
            self.transaction_status = JumioTransactionStatus.FAILED.value
        else:
            self.transaction_status = JumioTransactionStatus.DONE.value

    def construct_reject_reason(self):
        reason = self.verification_status
        if self.has_reject_reason():
            reason = f'{reason} {self.reject_reason["rejectReasonDescription"]}'
            for reject_reason_details in self.reject_reason["rejectReasonDetails"]:
                reason = f"{reason} {reject_reason_details['detailsDescription']}"
            return reason
        else:
            return reason
