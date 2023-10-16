from app.command.command import CommandInterface, ExecAction


class GrafanaCommand(CommandInterface):
    TAG: str = 'grafana'

    def __init__(self, action: ExecAction):
        self.action = action

    def get_commands(self):
        if self.action == ExecAction.INSTALL:
            return [
                'sudo dnf -y install grafana',
                'sudo systemctl start grafana-server',
                'sudo systemctl enable grafana-server',
                'sudo systemctl status grafana-server',
                'sudo firewall-cmd --add-port=3000/tcp --permanent',
                'sudo firewall-cmd --reload',
            ]
        else:
            return [
                'sudo systemctl stop grafana-server',
                'sudo dnf -y remove grafana',
            ]

    def get_tag(self) -> str:
        return self.TAG

    def get_action(self):
        return self.action
