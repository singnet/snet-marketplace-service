from dapp_user.constant import SourceDApp, CommunicationType, PreferenceType


class UserPreference:
    def __init__(self, preference_type, communication_type, source, status, opt_out_reason=None):
        self._communication_type = communication_type
        self._preference_type = preference_type
        self._source = source
        self._status = status
        self._opt_out_reason = opt_out_reason

    @property
    def communication_type(self):
        return self._communication_type

    @property
    def preference_type(self):
        return self._preference_type

    @property
    def source(self):
        return self._source

    @property
    def opt_out_reason(self):
        return self._opt_out_reason

    @property
    def status(self):
        return self._status

    def to_dict(self):
        return {
            "preference_type": self._preference_type,
            "communication_type": self.communication_type,
            "source": self.source,
            "opt_out_reason": self.opt_out_reason,
            "status": self.status
        }
