from enum import Enum


class CommandInterface:
    def get_commands(self):
        pass

    def get_tag(self) -> str:
        pass

    def get_action(self) -> str:
        pass


class ExecAction(Enum):
    INSTALL = 1
    DELETE = 2