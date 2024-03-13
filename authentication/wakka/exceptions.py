from rest_framework.exceptions import APIException
from rest_framework import status


class BaseException(APIException):
    message: str
    status_code: int

    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidAppNameException(BaseException):
    def __init__(self):
        super().__init__("Invalid app name", status.HTTP_400_BAD_REQUEST)


class InvalidServerApiKeyException(BaseException):
    def __init__(self):
        super().__init__("Invalid server api key", status.HTTP_403_FORBIDDEN)


class InvalidCredentialsException(BaseException):
    def __init__(self):
        super().__init__("Invalid credentials", status.HTTP_403_FORBIDDEN)

class InvalidRefreshTokenException(BaseException):
    def __init__(self):
        super().__init__("Invalid refresh token", status.HTTP_400_BAD_REQUEST)