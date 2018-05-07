from tokens import Token, TokenType


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

    def read_identifier_or_number(self):
        text = ''
        while not self.is_finished():
            char = self.current_char()

            if not char.isalnum():
                break

            text += char
            self.advance_index()

        return text

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
            double_token = Token.doubles.get(char + self.input[self.index + 1], None)

            if double_token:
                self.advance_index()
                self.advance_index()
                return double_token

        token = Token.singles.get(char, None)

        if token:
            self.advance_index()
            return token

        if char.isalnum():
            string = self.read_identifier_or_number().lower()

            try:
                number = int(string)
                return Token(TokenType.NUMBER, number)
            except ValueError:
                pass

            word = Token.words.get(string, None)
            if word:
                return word

            return Token(TokenType.IDENTIFIER, string)

    def lex(self):
        tokens = []

        while True:
            token = self.advance_to_next_token()
            if not token:
                break

            tokens.append(token)

        return tokens
