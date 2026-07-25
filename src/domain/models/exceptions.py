class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AlreadyPremiumError(Exception):
    pass


class SubscriptionNotFoundError(Exception):
    pass
