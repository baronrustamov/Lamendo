from .api import get_board_acronyms


class URLSpace:
    def __init__(self):
        self.board_acronyms = get_board_acronyms()

    def valid_board_acronym(self, val):
        return val in self.board_acronyms
