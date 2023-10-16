from app.command.command import CommandInterface, ExecAction


class TensorflowCommand(CommandInterface):
    TAG: str = 'tensorflow'

    def __init__(self, action: ExecAction):
        self.action = action

    def get_commands(self):
        if self.action == ExecAction.INSTALL:
            return [
                'sudo dnf install -y python3-pip',
                'sudo dnf install -y tensorflow',
            ]
        else:
            return ['python -m pip uninstall  -y tensorflow']

    def get_tag(self) -> str:
        return self.TAG

    def get_action(self):
        return self.action