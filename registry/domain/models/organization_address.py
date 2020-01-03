class OrganizationAddress:
    def __init__(self, address_type, street_address, pincode, city, country, state=None):
        self.__address_type = address_type
        self.__street_address = street_address
        self.__pincode = pincode
        self.__city = city
        self.__country = country
        self.__state = state

    def to_dict(self):
        return {"address_type": self.__address_type,
                "street_address": self.__street_address,
                "city": self.__city,
                "pincode": self.__pincode,
                "state": self.__state,
                "country": self.__country}
