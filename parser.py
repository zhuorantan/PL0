from token import Token, TokenType, Sign, BinaryOperator, Word
from expression import Expression, ExpressionType


class TokenError(Exception):

    def __init__(self, token, expected_type=None, expected_object=None):
        self.token = token
        self.expected_type = expected_type
        self.expected_object = expected_object


class Parser(object):

    @staticmethod
    def parse_word(token, word):
        if token.type != TokenType.WORD:
            raise TokenError(token, TokenType.WORD)
        if token.object != word:
            raise TokenError(token, expected_object=word)

    @staticmethod
    def parse_sign(token, sign):
        if token.type != TokenType.SIGN:
            raise TokenError(token, TokenType.SIGN)
        if token.object != sign:
            raise TokenError(token, expected_object=sign)

    @staticmethod
    def parse_identifier(token):
        if token.type != TokenType.IDENTIFIER:
            raise TokenError(token, TokenType.IDENTIFIER)

        return token.object

    @staticmethod
    def parse_number(token):
        if token.type != TokenType.NUMBER:
            raise TokenError(token, TokenType.NUMBER)

        return token.object

    @staticmethod
    def parse_consts(tokens):
        if len(tokens) == 0:
            return

        Parser.parse_word(tokens[0], Word.CONST)
        Parser.parse_sign(tokens[-1], Sign.SEMICOLON)

        def parse_function(tokens):
            if len(tokens) == 0:
                raise EOFError
            if len(tokens) != 3:
                raise TokenError(tokens[-1])
            if tokens[1] != Token(TokenType.OPERATOR, BinaryOperator.EQUAL):
                raise TokenError(tokens[1], TokenType.OPERATOR, BinaryOperator.EQUAL)

            identifier = Parser.parse_identifier(tokens[0])
            number = Parser.parse_number(tokens[2])

            return identifier, number

        consts = Parser.parse_comma_separated(tokens[1:-1], parse_function)

        return Expression(ExpressionType.CONSTDEFINITION, consts)

    @staticmethod
    def parse_variables(tokens):
        if len(tokens) == 0:
            return

        Parser.parse_word(tokens[0], Word.VAR)
        Parser.parse_sign(tokens[-1], Sign.SEMICOLON)

        def parse_function(tokens):
            if len(tokens) == 0:
                raise EOFError
            if len(tokens) != 1:
                raise TokenError(tokens[-1])

            return Parser.parse_identifier(tokens[0])

        variables = Parser.parse_comma_separated(tokens[1:-1], parse_function)

        return Expression(ExpressionType.VARIABLE, variables)

    @staticmethod
    def parse_comma_separated(tokens, parse_handler):
        return list(map(parse_handler, Parser.split_list(tokens, Token(TokenType.SIGN, Sign.COMMA))))

    @staticmethod
    def parse_expression(tokens):
        if len(tokens) == 0:
            return

        expression = Parser.parse_operators([BinaryOperator.PLUS, BinaryOperator.MINUS], tokens)
        if not expression:
            expression = Parser.parse_operators([BinaryOperator.TIMES, BinaryOperator.SLASH], tokens)

        if expression:
            return expression

        if tokens[0].type is TokenType.SIGN and tokens[0].object is Sign.LEFTPAREN and tokens[-1].type is TokenType.SIGN and tokens[-1].object is Sign.RIGHTPAREN:
            return Parser.parse_expression(tokens[1:-1])

        if len(tokens) == 1:
            token = tokens[0]

            if token.type is TokenType.NUMBER:
                return Expression(ExpressionType.NUMBER, token.object)
            elif token.type is TokenType.IDENTIFIER:
                return Expression(ExpressionType.VARIABLE, token.object)

        raise TokenError(tokens[0])

    @staticmethod
    def parse_operators(operators, tokens):
        try:
            op_index = next(index for index, token in enumerate(tokens) if token.type is TokenType.OPERATOR and token.object in operators)
        except StopIteration:
            return

        previous_tokens = tokens[:op_index]
        after_tokens = tokens[op_index + 1:]

        if not Parser.is_parans_match(previous_tokens):
            return
        if not Parser.is_parans_match(after_tokens):
            return

        previous = Parser.parse_expression(previous_tokens)
        after = Parser.parse_expression(after_tokens)

        if not previous or not after:
            raise TokenError(tokens[op_index])

        return Expression(ExpressionType.BINARY, (previous, tokens[op_index].object, after))

    @staticmethod
    def is_parans_match(tokens):
        count = 0

        for token in tokens:
            if token.type == TokenType.SIGN:
                if token.object == Sign.LEFTPAREN:
                    count += 1
                elif token.object == Sign.RIGHTPAREN:
                    count -= 1

            if count < 0:
                return False

        return count == 0

    @staticmethod
    def split_list(l, sep):
        current = []
        for x in l:
            if x == sep:
                yield current
                current = []
            else:
                current.append(x)
        yield current
