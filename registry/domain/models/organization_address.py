class OrganizationAddress:
    def __init__(self, address_type, street_address, apartment, pincode, city, country, state=None):
        self.__address_type = address_type
        self.__street_address = street_address
        self.__apartment = apartment
        self.__pincode = pincode
        self.__city = city
        self.__country = country
        self.__state = state

    def to_response(self):
        return {"address_type": self.__address_type,
                "street_address": self.__street_address,
                "apartment": self.__apartment,
                "city": self.__city,
                "pincode": self.__pincode,
                "state": self.__state,
                "country": self.__country}

    @property
    def address_type(self):
        return self.__address_type

    @property
    def street_address(self):
        return self.__street_address

    @property
    def apartment(self):
        return self.__apartment

    @property
    def pincode(self):
        return self.__pincode

    @property
    def city(self):
        return self.__city

    @property
    def country(self):
        return self.__country

    @property
    def state(self):
        return self.__state

    def __eq__(self, other):
        if not isinstance(other, OrganizationAddress):
            return NotImplemented
        return self.apartment == other.apartment and self.street_address == other.street_address \
               and self.city == other.city and self.state == other.state and self.pincode == other.pincode \
               and self.country == other.country
