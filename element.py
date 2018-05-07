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


class SentenceType(Enum):
    ASSIGN = 1
    CALL = 2
    CONDITION = 3
    LOOP = 4
    COMPOUND = 5
    READ = 6
    WRITE = 7

    def name(self):
        return SentenceType._names[self]


SentenceType._names = {
    SentenceType.ASSIGN: 'assign',
    SentenceType.CALL: 'call',
    SentenceType.CONDITION: 'condition',
    SentenceType.LOOP: 'loop',
    SentenceType.COMPOUND: 'compound',
    SentenceType.READ: 'read',
    SentenceType.WRITE: 'write'
}


class Sentence(object):

    def __init__(self, type, content):
        self.type = type
        self.content = content

    def __str__(self):
        return 'Sentence(%s, %s)' % (self.type.name(), self.content)

    def __repr__(self):
        return self.__str__()


class Program(object):

    def __init__(self, consts, variables, procedures, sentence):
        self.consts = consts
        self.variables = variables
        self.procedures = procedures
        self.sentence = sentence

    def __str__(self):
        return 'Program(%s, %s, %s, %s)' % (self.consts, self.variables, self.procedures, self.sentence)

    def __repr__(self):
        return self.__str__()


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
