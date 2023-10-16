from app.command.command import CommandInterface, ExecAction


class PostgresCommand(CommandInterface):
    TAG: str = 'postgres'

    def __init__(self, action: ExecAction):
        self.action = action

    def get_commands(self):
        if self.action == ExecAction.INSTALL:
            return [
                'sudo dnf install postgresql-server postgresql-contrib',
                'sudo systemctl enable postgresql',
                'sudo postgresql-setup --initdb --unit postgresql',
                'sudo systemctl start postgresql',
            ]
        else:
            return [
                'sudo systemctl stop postgresql',
                'sudo dnf remove postgresql-server postgresql-client',
                'sudo rm -rf /var/lib/pgsql/',
                'sudo userdel postgres',
                'sudo groupdel postgres',
            ]

    def get_tag(self) -> str:
        return self.TAG

    def get_action(self):
        return self.action