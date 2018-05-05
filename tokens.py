from enum import Enum


class Word(Enum):
    BEGIN = 1
    CALL = 2
    CONST = 3
    DO = 4
    END = 5
    IF = 6
    ODD = 7
    PROCEDURE = 8
    READ = 9
    THEN = 10
    VAR = 11
    WHILE = 12
    WRITE = 13

    def name(self):
        return self.value() + 'sym'

    def value(self):
        return Word._values[self]

    def __str__(self):
        return 'Word(%s, %s)' % (self.name(), self.value())

    def __repr__(self):
        return self.__str__()


Word._values = {
    Word.BEGIN: 'begin',
    Word.CALL: 'call',
    Word.CONST: 'const',
    Word.DO: 'do',
    Word.END: 'end',
    Word.IF: 'if',
    Word.ODD: 'odd',
    Word.PROCEDURE: 'procedure',
    Word.READ: 'read',
    Word.THEN: 'then',
    Word.VAR: 'var',
    Word.WHILE: 'while',
    Word.WRITE: 'write'
}


class Sign(Enum):
    LEFTPAREN = 1
    RIGHTPAREN = 2
    COMMA = 3
    SEMICOLON = 4
    PERIOD = 5

    def name(self):
        return Sign._names[self]

    def value(self):
        return Sign._values[self]

    def __str__(self):
        return 'Sign(%s, %s)' % (self.name(), self.value())

    def __repr__(self):
        return self.__str__()


Sign._values = {
    Sign.LEFTPAREN: '(',
    Sign.RIGHTPAREN: ')',
    Sign.COMMA: ',',
    Sign.SEMICOLON: ';',
    Sign.PERIOD: '.'
}

Sign._names = {
    Sign.LEFTPAREN: 'lparen',
    Sign.RIGHTPAREN: 'rparen',
    Sign.COMMA: 'comma',
    Sign.SEMICOLON: 'semicolon',
    Sign.PERIOD: 'period'
}


class BinaryOperator(Enum):
    PLUS = 1
    MINUS = 2
    TIMES = 3
    SLASH = 4
    EQUAL = 5
    HASHTAG = 6
    LESS = 7
    LESSEQUAL = 8
    GREATER = 9
    GREATEREQUAL = 10
    ASSIGN = 11

    def name(self):
        return BinaryOperator._names[self]

    def value(self):
        return BinaryOperator._values[self]

    def __str__(self):
        return 'BinaryOperator(%s, %s)' % (self.name(), self.value())

    def __repr__(self):
        return self.__str__()


BinaryOperator._values = {
    BinaryOperator.PLUS: '+',
    BinaryOperator.MINUS: '-',
    BinaryOperator.TIMES: '*',
    BinaryOperator.SLASH: '/',
    BinaryOperator.EQUAL: '=',
    BinaryOperator.HASHTAG: '#',
    BinaryOperator.LESS: '<',
    BinaryOperator.LESSEQUAL: '<=',
    BinaryOperator.GREATER: '>',
    BinaryOperator.GREATEREQUAL: '>=',
    BinaryOperator.ASSIGN: ':='
}

BinaryOperator._names = {
    BinaryOperator.PLUS: 'plus',
    BinaryOperator.MINUS: 'minus',
    BinaryOperator.TIMES: 'times',
    BinaryOperator.SLASH: 'slash',
    BinaryOperator.EQUAL: 'equal',
    BinaryOperator.HASHTAG: 'hashtag',
    BinaryOperator.LESS: 'less',
    BinaryOperator.LESSEQUAL: 'less_equal',
    BinaryOperator.GREATER: 'greater',
    BinaryOperator.GREATEREQUAL: 'greater_equal',
    BinaryOperator.ASSIGN: 'assign'
}


class TokenType(Enum):
    WORD = 1
    SIGN = 2
    IDENTIFIER = 3
    NUMBER = 4
    OPERATOR = 5


class Token(object):

    def __init__(self, type, object):
        self.type = type
        self.object = object

    def name(self):
        if self.type == TokenType.IDENTIFIER:
            return 'identifier'
        elif self.type == TokenType.NUMBER:
            return 'number'
        else:
            return self.object.name()

    def value(self):
        if self.type == TokenType.IDENTIFIER:
            return self.object
        elif self.type == TokenType.NUMBER:
            return self.object
        else:
            return self.object.value()

    def __str__(self):
        return 'Token(%s, %s)' % (self.name(), self.value())

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.type == other.type and self.object == other.object


Token._single_tokens = list(Sign) + [operator for operator in BinaryOperator if len(operator.value()) == 1]
Token._double_tokens = [operator for operator in BinaryOperator if len(operator.value()) == 2]

Token.words = dict([(word.value(), Token(TokenType.WORD, word)) for word in Word])
Token.singles = dict([(sign_or_operator.value(), Token(TokenType.SIGN if type(sign_or_operator) is Sign else TokenType.OPERATOR, sign_or_operator)) for sign_or_operator in Token._single_tokens])
Token.doubles = dict([(operator.value(), Token(TokenType.OPERATOR, operator)) for operator in Token._double_tokens])
