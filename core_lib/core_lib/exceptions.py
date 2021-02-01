class NewsRoomException(Exception):
    pass


class AuthorizationException(NewsRoomException):
    pass


class AuthorizationFailed(AuthorizationException):
    pass


class UserNameTaken(AuthorizationException):
    pass


class PasswordsDoNotMatch(AuthorizationException):
    pass


class IllegalPassword(AuthorizationException):
    pass
