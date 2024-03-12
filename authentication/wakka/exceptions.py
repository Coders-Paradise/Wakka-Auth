from rest_framework.exceptions import APIException


class BaseException(APIException):
    message: str
    status_code: int

    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidServerApiKeyException(BaseException):
    def __init__(self):
        super().__init__("Invalid server api key", 401)
