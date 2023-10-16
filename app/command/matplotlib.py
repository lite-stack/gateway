from app.command.command import CommandInterface, ExecAction


class MatplotlibCommand(CommandInterface):
    TAG: str = 'matplotlib'

    def __init__(self, action: ExecAction):
        self.action = action

    def get_commands(self):
        if self.action == ExecAction.INSTALL:
            return [
                'sudo dnf install -y pip',
                'pip install matplotlib',
            ]
        else:
            return [
                'pip uninstall -y matplotlib',
            ]

    def get_tag(self) -> str:
        return self.TAG

    def get_action(self):
        return self.action