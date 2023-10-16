from app.command.command import CommandInterface, ExecAction


class EchoCommand(CommandInterface):
    TAG: str = 'echo'

    def get_commands(self):
        return ['echo "test"']

    def get_tag(self) -> str:
        return self.TAG

    def get_action(self):
        return ''