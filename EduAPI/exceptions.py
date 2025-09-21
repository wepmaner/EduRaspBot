class Errors(Exception):
    def __init__(self, text, error_code):
        self.txt = text
        self.error_code = error_code


class EduDown(Exception):
    pass
