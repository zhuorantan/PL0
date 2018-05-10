from tokens import Token, TokenType, Sign, BinaryOperator


class Lexer:

    def __init__(self, input):
        self.input = input
        self.index = 0

    def advance_index(self):
        self.index += 1

    def is_finished(self):
        return self.index >= len(self.input)

    def current_char(self):
        return self.input[self.index]

    def line_index(self):
        return self.input.count('\n', 0, self.index)

    def index_in_current_line(self):
        return self.index - self.input.rfind('\n', 0, self.index) - 1

    def read_identifier_or_number(self):
        text = ''
        line, index = self.line_index(), self.index_in_current_line()

        while not self.is_finished():
            char = self.current_char()

            if not char.isalnum():
                break

            text += char
            self.advance_index()

        return text, line, index

    def advance_to_next_token(self):
        while not self.is_finished():
            char = self.current_char()

            if not char.isspace():
                break

            self.advance_index()

        if self.is_finished():
            return

        char = self.current_char()

        if self.index + 1 < len(self.input):
            operator = Token.double(char + self.input[self.index + 1])

            if operator:
                double_token = Token(TokenType.OPERATOR, operator, self.line_index(), self.index_in_current_line())

                self.advance_index()
                self.advance_index()
                return double_token

        sign_or_operator = Token.single(char)

        if sign_or_operator:
            token = Token(TokenType.SIGN if type(sign_or_operator) is Sign else TokenType.OPERATOR, sign_or_operator, self.line_index(), self.index_in_current_line())

            self.advance_index()
            return token

        if char.isalnum():
            string, line, index = self.read_identifier_or_number()
            string = string.lower()

            try:
                number = int(string)
                return Token(TokenType.NUMBER, number, line, index)
            except ValueError:
                pass

            word = Token.word(string)
            if word:
                token = Token(TokenType.WORD, word, line, index)
                return token

            return Token(TokenType.IDENTIFIER, string, line, index)

    def lex(self):
        tokens = []

        while True:
            token = self.advance_to_next_token()
            if not token:
                break

            tokens.append(token)

        return tokens
