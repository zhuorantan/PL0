from enum import Enum


class ElementType(Enum):
    EXPRESSION = 1
    CONDITION = 2
    CONSTS = 3
    VARS = 4

    def name(self):
        return ElementType._names[self]


ElementType._names = {
    ElementType.EXPRESSION: 'expression',
    ElementType.CONDITION: 'condition',
    ElementType.CONSTS: 'consts',
    ElementType.VARS: 'vars'
}


class Element(object):

    def __init__(self, type, content):
        self.type = type
        self.content = content

    def __str__(self):
        return 'Element(%s, %s)' % (self.type.name(), self.content)

    def __repr__(self):
        return self.__str__()
