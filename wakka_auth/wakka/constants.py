from enum import Enum


class ErrorCode(Enum):
    INVALID_APP_NAME = "INVALID_APP_NAME"
    INVALID_SERVER_API_KEY = "INVALID_SERVER_API_KEY"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INVALID_REFRESH_TOKEN = "INVALID_REFRESH_TOKEN"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    USER_DOES_NOT_EXIST = "USER_DOES_NOT_EXIST"
    VERIFICATION_EMAIL_SENDING_FAILED = "VERIFICATION_EMAIL_SENDING_FAILED"
    INVALID_EMAIL_VERIFICATION_LINK = "INVALID_EMAIL_VERIFICATION_LINK"
    ONE_TIME_TOKEN_INVALID = "ONE_TIME_TOKEN_INVALID"
    ONE_TIME_TOKEN_EXPIRED = "ONE_TIME_TOKEN_EXPIRED"
    USER_NOT_VERIFIED = "USER_NOT_VERIFIED"
    FORGOT_PASSWORD_EMAIL_SENDING_FAILED = "FORGOT_PASSWORD_EMAIL_SENDING_FAILED"
    USER_NOT_ACTIVE = "USER_NOT_ACTIVE"
    EMAIL_ALREADY_VERIFIED = "EMAIL_ALREADY_VERIFIED"


class OneTimeTokenType(Enum):
    FOROGT_PASSWORD = "FOROGT_PASSWORD"
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"


class AuthTokenType(Enum):
    ACCESS_TOKEN = "ACCESS_TOKEN"
    REFRESH_TOKEN = "REFRESH_TOKEN"


VERIFICATION_EXPIRED_LINK_TITLE: str = "Expired Email Verification Link"
VERIFICATION_EXPIRED_LINK_DESCRIPTION: str = (
    "The verification link is expired. Please request a new verification link."
)

VERIFICATION_INVALID_LINK_TITLE: str = "Invalid Email Verification Link"
VERIFICATION_INVALID_LINK_DESCRIPTION: str = (
    "The verification link is invalid. Please request a new verification link."
)

VERIFICATION_SUCCESS_TITLE: str = "Email Verification Successful"
VERIFICATION_SUCCESS_DESCRIPTION: str = (
    "Your email has been successfully verified. Please close this tab and continue with the application."
)

FORGOT_PASSWORD_EXPIRED_LINK_TITLE: str = "Expired Password Reset Link"
FORGOT_PASSWORD_EXPIRED_LINK_DESCRIPTION: str = (
    "The password reset link is expired. Please request a new password reset link."
)
FORGOT_PASSWORD_INVALID_LINK_TITLE: str = "Invalid Password Reset Link"
FORGOT_PASSWORD_INVALID_LINK_DESCRIPTION: str = (
    "The password reset link is invalid. Please request a new password reset link."
)
FORGOT_PASSWORD_SUCCESS_TITLE: str = "Password Reset Successful"
FORGOT_PASSWORD_SUCCESS_DESCRIPTION: str = (
    "Your password has been successfully reset. Please close this tab and continue with the application."
)

FORGOT_PASSWORD_FORM_TITLE: str = "Reset Password"
