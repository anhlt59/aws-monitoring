from src.common.exceptions import ConflictError, NotFoundError


class EventNotFoundError(NotFoundError):
    pass


class EventConflictError(ConflictError):
    pass
