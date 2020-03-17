class User:
    def __init__(self, username, name, email, email_verified, origin, preferences):
        self._username = username,
        self._name = name,
        self._email = email,
        self._email_verified = email_verified,
        self._email_alerts = 0,
        self._is_terms_accepted = 0
        self._preferences = preferences
        self._origin = origin

    def to_dict(self):
        return {
            "username": self._username,
            "name": self._name,
            "email": self._email,
            "email_verified": self._email_verified,
            "email_alerts": self._email_alerts,
            "origin": self._origin,
            "is_terms_accepted": self._is_terms_accepted,
            "preferences": []
        }

    @property
    def username(self):
        return self._username

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email

    @property
    def email_verified(self):
        return self._email_verified

    @property
    def origin(self):
        return self._origin

    @property
    def email_alerts(self):
        return self._email_alerts

    @property
    def is_terms_accepted(self):
        return self._is_terms_accepted

    @property
    def preferences(self):
        return self._preferences
