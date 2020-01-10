import types


class OrganizationAccessControl(type):
    def __new__(cls, name, bases, attrs):

        for attr_name, attr_value in attrs.iteritems():
            if isinstance(attr_value, types.FunctionType):
                print("before")
                attrs[attr_name] = cls.deco(attr_value)
                print("after")

        return super(OrganizationAccessControl, cls).__new__(cls, name, bases, attrs)

    @classmethod
    def deco(cls, func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        return wrapper
