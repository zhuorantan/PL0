from enum import Enum


class SentenceType(Enum):
    ASSIGN = 1
    CALL = 2

    def name(self):
        return SentenceType._names[self]


SentenceType._names = {
    SentenceType.ASSIGN: 'assign',
    SentenceType.CALL: 'call'
}


class Sentence(object):

    def __init__(self, type, content):
        self.type = type
        self.content = content

    def __str__(self):
        return 'Sentence(%s, %s)' % (self.type.name(), self.content)

    def __repr__(self):
        return self.__str__()
