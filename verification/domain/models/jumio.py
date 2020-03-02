
class JumioVerification:
    def __init__(self, verification_id, username, user_reference_id, verification_status, created_at, updated_at,
                 redirect_url=None, jumio_reference_id=None, callback_type=None, id_scan_status=None,
                 id_scan_source=None, transaction_date=None, callback_date=None, identity_verification=None):
        self.verification_id = verification_id
        self.username = username
        self.user_reference_id = user_reference_id
        self.verification_status = verification_status
        self.updated_at = updated_at
        self.created_at = created_at
        self.redirect_url = redirect_url
        self.jumio_reference_id = jumio_reference_id
        self.callback_type = callback_type
        self.id_scan_status = id_scan_status
        self.id_scan_source = id_scan_source
        self.transaction_date = transaction_date
        self.callback_date = callback_date
        self.identity_verification = identity_verification
