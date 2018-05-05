from enum import Enum


class ElementType(Enum):
    CONSTS = 1
    VARS = 2
    PROCEDURE = 3
    SUBPROGRAM = 4
    PROGRAM = 5

    def name(self):
        return ElementType._names[self]


ElementType._names = {
    ElementType.CONSTS: 'consts',
    ElementType.VARS: 'vars',
    ElementType.PROCEDURE: 'procedure',
    ElementType.SUBPROGRAM: 'subprogram',
    ElementType.PROGRAM: 'program'
}


class Element(object):

    def __init__(self, type, content):
        self.type = type
        self.content = content

    def __str__(self):
        return 'Element(%s, %s)' % (self.type.name(), self.content)

    def __repr__(self):
        return self.__str__()
