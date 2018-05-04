from token import Token, TokenType, Sign, BinaryOperator, Word
from expression import Expression, ExpressionType
from element import Element, ElementType
from condition import Condition, ConditionType
from sentence import Sentence, SentenceType


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
    def parse_operator(token, operator):
        if token.type != TokenType.OPERATOR:
            raise TokenError(token, TokenType.OPERATOR)
        if token.object != operator:
            raise TokenError(token, expected_object=operator)

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

        return Element(ElementType.CONSTS, consts)

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

        return Element(ElementType.VARS, variables)

    @staticmethod
    def parse_comma_separated(tokens, parse_handler):
        return list(map(parse_handler, Parser.split_list(tokens, Token(TokenType.SIGN, Sign.COMMA))))

    @staticmethod
    def parse_expression(tokens):
        if len(tokens) == 0:
            return

        separated_tokens = Parser.separate_tokens_with_operators([BinaryOperator.PLUS, BinaryOperator.MINUS], tokens)
        if not separated_tokens:
            separated_tokens = Parser.separate_tokens_with_operators([BinaryOperator.TIMES, BinaryOperator.SLASH], tokens)

        if separated_tokens:
            previous_tokens, operator, after_tokens = separated_tokens

            previous = Parser.parse_expression(previous_tokens)
            after = Parser.parse_expression(after_tokens)

            if not previous or not after:
                raise TokenError(Token(TokenType.OPERATOR, operator))

            return Expression(ExpressionType.BINARY, (previous, operator, after))

        if tokens[0].type is TokenType.SIGN and tokens[0].object is Sign.LEFTPAREN and tokens[-1].type is TokenType.SIGN and tokens[-1].object is Sign.RIGHTPAREN:
            return Parser.parse_expression(tokens[1:-1])

        if len(tokens) == 1:
            token = tokens[0]

            if token.type is TokenType.NUMBER:
                return Expression(ExpressionType.NUMBER, token.object)
            elif token.type is TokenType.IDENTIFIER:
                return Expression(ExpressionType.IDENTIFIER, token.object)

        raise TokenError(tokens[0])

    @staticmethod
    def parse_condition(tokens):
        if len(tokens) == 0:
            return

        if tokens[0].type is TokenType.WORD and tokens[0].object is Word.ODD:
            expression = Parser.parse_expression(tokens[1:])
            if not expression:
                raise TokenError(tokens.get(1, None))

            return Condition(ConditionType.UNARY, (Word.ODD, expression))

        condition_operators = [
            BinaryOperator.EQUAL,
            BinaryOperator.HASHTAG,
            BinaryOperator.LESS,
            BinaryOperator.LESSEQUAL,
            BinaryOperator.GREATER,
            BinaryOperator.GREATEREQUAL
        ]

        separated_tokens = Parser.separate_tokens_with_operators(condition_operators, tokens)
        if separated_tokens:
            previous_tokens, operator, after_tokens = separated_tokens

            previous = Parser.parse_expression(previous_tokens)
            after = Parser.parse_expression(after_tokens)

            if not previous or not after:
                raise TokenError(Token(TokenType.OPERATOR, operator))

            return Condition(ConditionType.BINARY, (previous, operator, after))

        raise TokenError(tokens[0])

    @staticmethod
    def parse_assign(tokens):
        if len(tokens) == 0:
            return

        if len(tokens) < 3:
            raise TokenError(tokens[-1])

        identifier = Parser.parse_identifier(tokens[0])
        Parser.parse_operator(tokens[1], BinaryOperator.ASSIGN)
        expression = Parser.parse_expression(tokens[2:-1])
        Parser.parse_sign(tokens[-1], Sign.SEMICOLON)

        return Sentence(SentenceType.ASSIGN, (identifier, expression))

    @staticmethod
    def parse_call(tokens):
        if len(tokens) == 0:
            return

        if len(tokens) != 3:
            raise TokenError(tokens[-1])

        Parser.parse_word(tokens[0], Word.CALL)
        identifier = Parser.parse_identifier(tokens[1])
        Parser.parse_sign(tokens[2], Sign.SEMICOLON)

        return Sentence(SentenceType.CALL, identifier)

    @staticmethod
    def separate_tokens_with_operators(operators, tokens):
        try:
            op_index = next(index for index, token in enumerate(tokens) if
                            token.type is TokenType.OPERATOR and token.object in operators)
        except StopIteration:
            return

        previous_tokens = tokens[:op_index]
        after_tokens = tokens[op_index + 1:]

        if not Parser.is_parans_match(previous_tokens):
            return
        if not Parser.is_parans_match(after_tokens):
            return

        return previous_tokens, tokens[op_index].object, after_tokens

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
