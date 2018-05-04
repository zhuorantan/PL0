from enum import Enum


class ConditionType(Enum):
    UNARY = 1
    BINARY = 2

    def name(self):
        return ConditionType._names[self]


ConditionType._names = {
    ConditionType.UNARY: 'unary',
    ConditionType.BINARY: 'binary'
}


class Condition(object):

    def __init__(self, type, content):
        self.type = type
        self.content = content

    def __str__(self):
        return 'Condition(%s, %s)' % (self.type.name(), self.content)

    def __repr__(self):
        return self.__str__()
