class TargetError(Exception):
    pass


class ProbeError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class TimeoutError(Exception):
    pass


class ConfigError(Exception):
    def __init__(self, exc, contents):
        super(ConfigError, self).__init__()
        self.exc = exc
        self.contents = contents


class CommandError(Exception):
    def __init__(self, exc, commands):
        super(CommandError, self).__init__()
        self.exc = exc
        self.commands = commands


class LoginNotReadyError(Exception):
    def __init__(self, exc, message):
        super(LoginNotReadyError, self).__init__(message=message)
        self.exc = exc
