from enum import Enum


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
