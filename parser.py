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
    def parse_condition_expression(tokens):
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
    def parse_sentence(tokens):
        if len(tokens) == 0:
            return

        assign = Parser.parse_assign(tokens)
        if assign:
            return assign

        condition = Parser.parse_condition_sentence(tokens)
        if condition:
            return condition

        loop = Parser.parse_loop_sentence(tokens)
        if loop:
            return loop

        call = Parser.parse_call(tokens)
        if call:
            return call

        compound = Parser.parse_compound(tokens)
        if compound:
            return compound

        read_or_write = Parser.parse_read_or_write(tokens)
        if read_or_write:
            return read_or_write

    @staticmethod
    def parse_assign(tokens):
        if len(tokens) == 0:
            return
        if len(tokens) < 3:
            return

        if not (tokens[1].type is TokenType.OPERATOR and tokens[1].object is BinaryOperator.ASSIGN):
            return

        identifier = Parser.parse_identifier(tokens[0])
        expression = Parser.parse_expression(tokens[2:-1])
        Parser.parse_sign(tokens[-1], Sign.SEMICOLON)

        return Sentence(SentenceType.ASSIGN, (identifier, expression))

    @staticmethod
    def parse_condition_sentence(tokens):
        if len(tokens) == 0:
            return

        if not (tokens[0].type is TokenType.WORD and tokens[0].object is Word.IF):
            return

        try:
            then_index = next(index for index, token in enumerate(tokens) if token.type is TokenType.WORD and token.object is Word.THEN)
        except StopIteration:
            return

        previous_tokens = tokens[1:then_index]
        after_tokens = tokens[then_index + 1:]

        condition_expression = Parser.parse_condition_expression(previous_tokens)
        sentence = Parser.parse_sentence(after_tokens)

        return Sentence(SentenceType.CONDITION, (condition_expression, sentence))

    @staticmethod
    def parse_loop_sentence(tokens):
        if len(tokens) == 0:
            return

        if not (tokens[0].type is TokenType.WORD and tokens[0].object is Word.WHILE):
            return

        try:
            then_index = next(index for index, token in enumerate(tokens) if token.type is TokenType.WORD and token.object is Word.DO)
        except StopIteration:
            return

        previous_tokens = tokens[1:then_index]
        after_tokens = tokens[then_index + 1:]

        condition_expression = Parser.parse_condition_expression(previous_tokens)
        sentence = Parser.parse_sentence(after_tokens)

        return Sentence(SentenceType.LOOP, (condition_expression, sentence))

    @staticmethod
    def parse_call(tokens):
        if len(tokens) == 0:
            return

        if not (tokens[0].type is TokenType.WORD and tokens[0].object is Word.CALL):
            return

        if len(tokens) != 3:
            raise TokenError(tokens[-1])

        identifier = Parser.parse_identifier(tokens[1])
        Parser.parse_sign(tokens[2], Sign.SEMICOLON)

        return Sentence(SentenceType.CALL, identifier)

    @staticmethod
    def parse_compound(tokens):
        if len(tokens) == 0:
            return

        if not (tokens[0].type is TokenType.WORD and tokens[0].object is Word.BEGIN):
            return

        Parser.parse_word(tokens[-1], Word.END)

        sentences = []
        start_index = 1
        generator = (index for index, token in enumerate(tokens) if token.type is TokenType.SIGN and token.object is Sign.SEMICOLON)
        while True:
            try:
                end_index = next(generator)
            except StopIteration:
                break

            sentences.append(Parser.parse_sentence(tokens[start_index:end_index+1]))
            start_index = end_index + 1

        return Sentence(SentenceType.COMPOUND, sentences)

    @staticmethod
    def parse_read_or_write(tokens):
        if len(tokens) == 0:
            return

        if not (tokens[0].type is TokenType.WORD and (tokens[0].object is Word.READ or tokens[0].object is Word.WRITE)):
            return

        Parser.parse_sign(tokens[1], Sign.LEFTPAREN)
        Parser.parse_sign(tokens[-2], Sign.RIGHTPAREN)
        Parser.parse_sign(tokens[-1], Sign.SEMICOLON)

        def read_parse_function(tokens):
            if len(tokens) == 0:
                raise EOFError
            if len(tokens) != 1:
                raise TokenError(tokens[-1])

            return Parser.parse_identifier(tokens[0])

        read_or_write = tokens[0].object
        content = Parser.parse_comma_separated(tokens[2:-2], read_parse_function if read_or_write is Word.READ else Parser.parse_expression)

        return Sentence(SentenceType.READ if read_or_write is Word.READ else SentenceType.WRITE, content)

    @staticmethod
    def parse_subprogram(tokens):
        if len(tokens) == 0:
            return

        start_index = 0

        consts = None
        variables = None

        if tokens[start_index].type is TokenType.WORD and tokens[start_index].object is Word.CONST:
            end_index = next(index for index, token in enumerate(tokens[start_index:]) if token.type is TokenType.SIGN and token.object is Sign.SEMICOLON)
            consts = Parser.parse_consts(tokens[start_index:end_index + 1])
            start_index = end_index + 1

        if tokens[start_index].type is TokenType.WORD and tokens[start_index].object is Word.VAR:
            end_index = next(index for index, token in enumerate(tokens[start_index:]) if token.type is TokenType.SIGN and token.object is Sign.SEMICOLON)
            variables = Parser.parse_variables(tokens[start_index:end_index + 1])
            start_index = end_index + 1

        if tokens[start_index].type is TokenType.WORD and tokens[start_index].object is Word.PROCEDURE:
            end_index = next(index for index, token in enumerate(tokens[start_index:]) if token.type is TokenType.SIGN and token.object is Sign.SEMICOLON)
            variables = Parser.parse_variables(tokens[start_index:end_index + 1])
            start_index = end_index + 1

    @staticmethod
    def parse_procedure(tokens):
        if len(tokens) == 0:
            return

        if len(tokens) < 3:
            raise TokenError(tokens[-1])

        Parser.parse_word(tokens[0], Word.PROCEDURE)
        identifier = Parser.parse_identifier(tokens[1])
        Parser.parse_sign(tokens[2], Sign.SEMICOLON)

        subprogram = Parser.parse_subprogram(tokens[3:])

        return Element(ElementType.PROCEDURE, (identifier, subprogram))

    @staticmethod
    def separate_tokens_with_operators(operators, tokens):
        generator = (index for index, token in enumerate(tokens) if token.type is TokenType.OPERATOR and token.object in operators)
        try:
            op_index = next(generator)
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
