from rest_framework import status
from rest_framework.exceptions import APIException


class BaseException(APIException):
    message: str
    status_code: int

    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidAppNameException(BaseException):
    def __init__(self):
        super().__init__("Invalid app name in header", status.HTTP_400_BAD_REQUEST)


class InvalidServerApiKeyException(BaseException):
    def __init__(self):
        super().__init__("Invalid server api key in header", status.HTTP_403_FORBIDDEN)


class InvalidCredentialsException(BaseException):
    def __init__(self):
        super().__init__("Invalid credentials", status.HTTP_401_UNAUTHORIZED)


class InvalidRefreshTokenException(BaseException):
    def __init__(self):
        super().__init__("Invalid refresh token", status.HTTP_400_BAD_REQUEST)


class UserAlreadyExistsException(BaseException):
    def __init__(self):
        super().__init__("User already exists", status.HTTP_409_CONFLICT)


class UserDoesNotExistException(BaseException):
    def __init__(self):
        super().__init__("User does not exist", status.HTTP_404_NOT_FOUND)


class VerificationEmailSendingFailedException(BaseException):
    def __init__(self):
        super().__init__(
            "Verification email sending failed", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class InvalidEmailVerificationLinkException(BaseException):
    def __init__(self):
        super().__init__("Invalid email verification link", status.HTTP_400_BAD_REQUEST)


class OneTimeTokenInvalidException(BaseException):
    def __init__(self):
        super().__init__("One time token is invalid", status.HTTP_400_BAD_REQUEST)


class OneTimeTokenExpiredException(BaseException):
    def __init__(self):
        super().__init__("One time token is expired", status.HTTP_400_BAD_REQUEST)


class UserNotVerifiedException(BaseException):
    def __init__(self):
        super().__init__("User is not verified", status.HTTP_400_BAD_REQUEST)
