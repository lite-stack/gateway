from app.command.command import CommandInterface, ExecAction


class MongoCommand(CommandInterface):
    TAG: str = 'mongo'

    def __init__(self, action: ExecAction):
        self.action = action

    def get_commands(self):
        if self.action == ExecAction.INSTALL:
            return [
                'echo "[mongodb-upstream]" | sudo tee /etc/yum.repos.d/mongodb.repo',
                'echo "name=MongoDB Repository" | sudo tee -a /etc/yum.repos.d/mongodb.repo',
                'echo "baseurl=https://repo.mongodb.org/yum/redhat/\$releasever/mongodb-org/4.4/x86_64/" | sudo tee -a /etc/yum.repos.d/mongodb.repo',
                'echo "gpgcheck=1" | sudo tee -a /etc/yum.repos.d/mongodb.repo',
                'echo "enabled=1" | sudo tee -a /etc/yum.repos.d/mongodb.repo',
                'echo "gpgkey=https://www.mongodb.org/static/pgp/server-4.4.asc" | sudo tee -a /etc/yum.repos.d/mongodb.repo',
                'sudo dnf update',
                'sudo dnf install mongodb-org',
                'sudo systemctl start mongod',
                'sudo systemctl enable mongod',
                'mongod --version',
            ]
        else:
            return [
                'sudo systemctl stop mongod',
                'sudo dnf remove mongodb-org',
                'sudo rm -r /var/log/mongodb',
                'sudo rm -r /var/lib/mongo',
                'sudo userdel mongodb',
                'sudo groupdel mongodb',
                'sudo rm /etc/yum.repos.d/mongodb.repo',
            ]
    
    def get_tag(self) -> str:
        return self.TAG

    def get_action(self):
        return self.action