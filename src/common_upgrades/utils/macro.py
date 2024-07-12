class Macro(object):
    """
    Macro Object

    Attributes:
        name: Macro name. E.g. GALILADDR.
        value: Value of the Macro. E.g. 1. Defaults to None.
    """

    def __init__(self, name, value=None):
        self.__name = name
        self.__value = value

    def __repr__(self):
        return "<Macro object with name {} and value {}>".format(self.__name, self.__value)

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value
