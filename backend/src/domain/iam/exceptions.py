from src.common.exceptions import BadRequestError, ConflictError, UnauthorizedError


class AdminRequiredError(UnauthorizedError):
    pass


class UserNotFoundError(UnauthorizedError):
    pass


class InvalidCredentialsError(UnauthorizedError):
    pass


class EmailDuplicateError(ConflictError):
    pass


class UserInactiveError(UnauthorizedError):
    pass


class SelfDeletionError(BadRequestError):
    pass


class CrossUserAccessError(UnauthorizedError):
    pass
