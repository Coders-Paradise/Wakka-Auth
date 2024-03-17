from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler

from .constants import ErrorCode


def wakka_exception_handler(exc, context):
    """Custom exception handler for wakka app.
    This function adds the error code to the response data.
    """
    response = exception_handler(exc, context)
    if response is not None:
        if hasattr(exc, "code"):
            response.data["code"] = exc.code
        else:
            response.data["code"] = "ERROR"

    return response


class BaseException(APIException):
    message: str
    status_code: int
    code: ErrorCode

    def __init__(self, message: str, status_code: int, code: ErrorCode):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(self.message, self.code)


class InvalidAppNameException(BaseException):
    message = "Invalid app name in header"
    status_code = status.HTTP_400_BAD_REQUEST
    code = ErrorCode.INVALID_APP_NAME.value

    def __init__(self):
        super().__init__(self.message, self.status_code, self.code)


class InvalidServerApiKeyException(BaseException):
    message = "Invalid server api key in header"
    status_code = status.HTTP_403_FORBIDDEN
    code = ErrorCode.INVALID_SERVER_API_KEY.value

    def __init__(self):
        super().__init__(self.message, self.status_code, self.code)


class InvalidCredentialsException(BaseException):
    message = "Invalid credentials"
    status_code = status.HTTP_401_UNAUTHORIZED
    code = ErrorCode.INVALID_CREDENTIALS.value

    def __init__(self):
        super().__init__(self.message, self.status_code, self.code)


class InvalidRefreshTokenException(BaseException):
    message = "Invalid refresh token"
    status_code = status.HTTP_400_BAD_REQUEST
    code = ErrorCode.INVALID_REFRESH_TOKEN.value

    def __init__(self):
        super().__init__(self.message, self.status_code, self.code)


class UserAlreadyExistsException(BaseException):
    message = "User already exists"
    status_code = status.HTTP_409_CONFLICT
    code = ErrorCode.USER_ALREADY_EXISTS.value

    def __init__(self):
        super().__init__(self.message, self.status_code, self.code)


class UserDoesNotExistException(BaseException):
    message = "User does not exist"
    status_code = status.HTTP_404_NOT_FOUND
    code = ErrorCode.USER_DOES_NOT_EXIST.value

    def __init__(self):
        super().__init__(self.message, self.status_code, self.code)


class VerificationEmailSendingFailedException(BaseException):
    message = "Verification email sending failed"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = ErrorCode.VERIFICATION_EMAIL_SENDING_FAILED.value

    def __init__(self):
        super().__init__(self.message, self.status_code, self.code)


class ForgotPasswordEmailSendingFailedException(BaseException):
    message = "Forgot password email sending failed"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = ErrorCode.FORGOT_PASSWORD_EMAIL_SENDING_FAILED.value

    def __init__(self):
        super().__init__(self.message, self.status_code, self.code)


class OneTimeTokenInvalidException(BaseException):
    message = "One time token is invalid"
    status_code = status.HTTP_400_BAD_REQUEST
    code = ErrorCode.ONE_TIME_TOKEN_INVALID.value

    def __init__(self):
        super().__init__(self.message, self.status_code, self.code)


class OneTimeTokenExpiredException(BaseException):
    message = "One time token is expired"
    status_code = status.HTTP_400_BAD_REQUEST
    code = ErrorCode.ONE_TIME_TOKEN_EXPIRED.value

    def __init__(self):
        super().__init__(self.message, self.status_code, self.code)


class UserNotVerifiedException(BaseException):
    message = "User is not verified"
    status_code = status.HTTP_400_BAD_REQUEST
    code = ErrorCode.USER_NOT_VERIFIED.value

    def __init__(self):
        super().__init__(self.message, self.status_code, self.code)


class UserNotActiveException(BaseException):
    message = "User is not active"
    status_code = status.HTTP_400_BAD_REQUEST
    code = ErrorCode.USER_NOT_ACTIVE.value

    def __init__(self):
        super().__init__(self.message, self.status_code, self.code)
