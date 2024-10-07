
class APIError(Exception):
    BASE_MESSAGES = ['refresh your captcha!!', 'Incorrect answer. Try again!']
    pass

    def __init__(self, error: str, response_data: dict=None):
        self.error = error
        self.response_data = response_data

    @property
    def error_message(self) -> str:
        if self.response_data:
            try:
                return self.response_data['error']['message']
            except KeyError:
                return str(self.error)
        return None

    def __str__(self):
        return self.error