from enum import Enum


class ExpressionType(Enum):
    NUMBER = 1
    IDENTIFIER = 2
    BINARY = 3

    def name(self):
        return ExpressionType._names[self]


ExpressionType._names = {
    ExpressionType.NUMBER: 'number',
    ExpressionType.IDENTIFIER: 'identifier',
    ExpressionType.BINARY: 'binary'
}


class Expression(object):

    def __init__(self, type, content):
        self.type = type
        self.content = content

    def __str__(self):
        return 'Expression(%s, %s)' % (self.type.name(), self.content)

    def __repr__(self):
        return self.__str__()
