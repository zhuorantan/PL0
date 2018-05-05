from tokens import Token, TokenType, Sign, BinaryOperator, Word
from element import Expression, ExpressionType, Condition, ConditionType, Sentence, SentenceType, Element, ElementType


class TokenError(Exception):

    def __init__(self, token, expected_type=None, expected_object=None):
        self.token = token
        self.expected_type = expected_type
        self.expected_object = expected_object


class Parser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def current_token(self):
        return self.tokens[self.index]

    def advance_to_next_token(self):
        self.index += 1

    def parse_identifier(self):
        token = self.current_token()
        if token.type != TokenType.IDENTIFIER:
            raise TokenError(token, TokenType.IDENTIFIER)

        self.advance_to_next_token()

        return token.object

    def parse_number(self):
        token = self.current_token()
        if token.type != TokenType.NUMBER:
            raise TokenError(token, TokenType.NUMBER)

        self.advance_to_next_token()

        return token.object

    def parse_token(self, token):
        if token != self.current_token():
            raise TokenError(self.current_token(), token.type, token.object)

        self.advance_to_next_token()

    def parse_comma_if_possible(self):
        if self.current_token() == Token(TokenType.SIGN, Sign.COMMA):
            self.advance_to_next_token()

    def parse_consts(self):
        if self.current_token() != Token(TokenType.WORD, Word.CONST):
            return

        self.advance_to_next_token()

        consts = []

        while self.current_token() != Token(TokenType.SIGN, Sign.SEMICOLON):
            identifier = self.parse_identifier()
            self.parse_token(Token(TokenType.OPERATOR, BinaryOperator.EQUAL))
            number = self.parse_number()
            self.parse_comma_if_possible()

            consts.append((identifier, number))

        self.advance_to_next_token()

        return Element(ElementType.CONSTS, consts)

    def parse_variables(self):
        if self.current_token() != Token(TokenType.WORD, Word.VAR):
            return

        self.advance_to_next_token()

        variables = []

        while self.current_token() != Token(TokenType.SIGN, Sign.SEMICOLON):
            identifier = self.parse_identifier()
            self.parse_comma_if_possible()

            variables.append(identifier)

        self.advance_to_next_token()

        return Element(ElementType.VARS, variables)

    def parse_sentence(self):
        assign = self.parse_assign()
        if assign:
            return assign

        condition = self.parse_condition_sentence()
        if condition:
            return condition

        loop = self.parse_loop_sentence()
        if loop:
            return loop

        call = self.parse_call()
        if call:
            return call

        compound = self.parse_compound()
        if compound:
            return compound

        read = self.parse_read()
        if read:
            return read

        write = self.parse_write()
        if write:
            return write

        if self.current_token() == Token(TokenType.SIGN, Sign.SEMICOLON):
            self.advance_to_next_token()

    def parse_assign(self):
        if self.index + 1 >= len(self.tokens) or self.tokens[self.index + 1] != Token(TokenType.OPERATOR, BinaryOperator.ASSIGN):
            return

        identifier = self.parse_identifier()
        self.advance_to_next_token()

        expression_tokens = []
        token = self.current_token()
        while token != Token(TokenType.SIGN, Sign.SEMICOLON):
            expression_tokens.append(token)
            self.advance_to_next_token()
            token = self.current_token()
        self.advance_to_next_token()

        expression = Parser.parse_expression(expression_tokens)

        return Sentence(SentenceType.ASSIGN, (identifier, expression))

    def parse_condition_sentence(self):
        if self.current_token() != Token(TokenType.WORD, Word.IF):
            return
        self.advance_to_next_token()

        condition_tokens = []
        token = self.current_token()
        while token != Token(TokenType.WORD, Word.THEN):
            condition_tokens.append(self.current_token())
            self.advance_to_next_token()
            token = self.current_token()
        self.advance_to_next_token()

        condition_expression = Parser.parse_condition_expression(condition_tokens)
        sentence = self.parse_sentence()

        return Sentence(SentenceType.CONDITION, (condition_expression, sentence))

    def parse_loop_sentence(self):
        if self.current_token() != Token(TokenType.WORD, Word.WHILE):
            return
        self.advance_to_next_token()

        condition_tokens = []
        token = self.current_token()
        while token != Token(TokenType.WORD, Word.DO):
            condition_tokens.append(self.current_token())
            self.advance_to_next_token()
            token = self.current_token()
        self.advance_to_next_token()

        condition_expression = Parser.parse_condition_expression(condition_tokens)
        sentence = self.parse_sentence()

        return Sentence(SentenceType.LOOP, (condition_expression, sentence))

    def parse_call(self):
        if self.current_token() != Token(TokenType.WORD, Word.CALL):
            return
        self.advance_to_next_token()

        identifier = self.parse_identifier()

        self.parse_token(Token(TokenType.SIGN, Sign.SEMICOLON))

        return Sentence(SentenceType.CALL, identifier)

    def parse_compound(self):
        if self.current_token() != Token(TokenType.WORD, Word.BEGIN):
            return
        self.advance_to_next_token()

        sentence = self.parse_sentence()
        sentences = []
        while self.current_token() != Token(TokenType.WORD, Word.END) and sentence is not None:
            sentences.append(sentence)
            sentence = self.parse_sentence()

        if sentence is not None:
            sentences.append(sentence)

        self.parse_token(Token(TokenType.WORD, Word.END))

        return Sentence(SentenceType.COMPOUND, sentences)

    def parse_read(self):
        if self.current_token() != Token(TokenType.WORD, Word.READ):
            return
        self.advance_to_next_token()

        self.parse_token(Token(TokenType.SIGN, Sign.LEFTPAREN))

        identifiers = []

        while self.current_token() != Token(TokenType.SIGN, Sign.RIGHTPAREN):
            identifier = self.parse_identifier()
            self.parse_comma_if_possible()

            identifiers.append(identifier)

        self.advance_to_next_token()
        self.parse_token(Token(TokenType.SIGN, Sign.SEMICOLON))

        return Sentence(SentenceType.READ, identifiers)

    def parse_write(self):
        if self.current_token() != Token(TokenType.WORD, Word.WRITE):
            return
        self.advance_to_next_token()

        self.parse_token(Token(TokenType.SIGN, Sign.LEFTPAREN))

        expressions = []

        while self.current_token() != Token(TokenType.SIGN, Sign.RIGHTPAREN):
            token = self.current_token()
            tokens = []
            while token != Token(TokenType.SIGN, Sign.COMMA) and token != Token(TokenType.SIGN, Sign.RIGHTPAREN):
                tokens.append(token)
                self.advance_to_next_token()
                token = self.current_token()

            if token == Token(TokenType.SIGN, Sign.COMMA):
                self.advance_to_next_token()

            expressions.append(Parser.parse_expression(tokens))

        self.advance_to_next_token()
        self.parse_token(Token(TokenType.SIGN, Sign.SEMICOLON))

        return Sentence(SentenceType.WRITE, expressions)

    def parse_subprogram(self):
        consts = self.parse_consts()
        variables = self.parse_variables()

        procedure = self.parse_procedure()
        procedures = []
        while procedure is not None:
            procedures.append(procedure)
            procedure = self.parse_procedure()

        sentence = self.parse_sentence()

        return Element(ElementType.SUBPROGRAM, (consts, variables, procedures, sentence))

    def parse_procedure(self):
        if self.current_token() != Token(TokenType.WORD, Word.PROCEDURE):
            return
        self.advance_to_next_token()

        identifier = self.parse_identifier()
        self.parse_token(Token(TokenType.SIGN, Sign.SEMICOLON))
        subprogram = self.parse_subprogram()

        return Element(ElementType.PROCEDURE, (identifier, subprogram))

    def parse_program(self):
        subprogram = self.parse_subprogram()

        self.parse_token(Token(TokenType.SIGN, Sign.PERIOD))

        return Element(ElementType.PROGRAM, subprogram)

    @staticmethod
    def parse_expression(tokens):
        expressions = []
        operators = []

        def peak(stack):
            return stack[-1] if stack else None

        def apply_operator():
            operator = operators.pop()
            right = expressions.pop()
            left = expressions.pop()
            expressions.append(Expression(ExpressionType.BINARY, (left, operator, right)))

        precedences = {
            BinaryOperator.PLUS: 1,
            BinaryOperator.MINUS: 1,
            BinaryOperator.TIMES: 2,
            BinaryOperator.SLASH: 2
        }

        for token in tokens:
            if token.type == TokenType.NUMBER:
                expressions.append(Expression(ExpressionType.NUMBER, token.object))
            elif token.type == TokenType.IDENTIFIER:
                expressions.append(Expression(ExpressionType.IDENTIFIER, token.object))
            elif token == Token(TokenType.SIGN, Sign.LEFTPAREN):
                operators.append(token.object)
            elif token == Token(TokenType.SIGN, Sign.RIGHTPAREN):
                top = peak(operators)
                while top is not None and top != Sign.LEFTPAREN:
                    apply_operator()
                    top = peak(operators)
                operators.pop()
            else:
                if token.object not in {BinaryOperator.PLUS, BinaryOperator.MINUS, BinaryOperator.TIMES,
                                        BinaryOperator.SLASH}:
                    raise TokenError(token, TokenType.OPERATOR)

                top = peak(operators)
                while top is not None and top not in {Sign.LEFTPAREN, Sign.RIGHTPAREN} and precedences[top] > \
                        precedences[token.object]:
                    apply_operator()
                    top = peak(operators)
                operators.append(token.object)
        while peak(operators) is not None:
            apply_operator()

        return expressions[0] if expressions else None

    @staticmethod
    def parse_condition_expression(tokens):
        if len(tokens) == 0:
            return

        if tokens[0] == Token(TokenType.WORD, Word.ODD):
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

        separated_tokens = Parser.separate_tokens_with_operators(tokens, condition_operators)
        if separated_tokens:
            previous_tokens, operator, after_tokens = separated_tokens

            previous = Parser.parse_expression(previous_tokens)
            after = Parser.parse_expression(after_tokens)

            if not previous or not after:
                raise TokenError(Token(TokenType.OPERATOR, operator))

            return Condition(ConditionType.BINARY, (previous, operator, after))

        raise TokenError(tokens[0])

    @staticmethod
    def separate_tokens_with_operators(tokens, operators):
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
