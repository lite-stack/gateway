import asyncio
import threading

import paramiko
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import session_maker
from app.command.command import ExecAction
from app.openstack.models import get_os_default_user
from app.servers.db_service import update_user_server
from app.servers.models import Server
from app.command.command import CommandInterface

class CommandRunner:
    LOADING_TAG="loading"
    ERROR_TAG="loading"

    SSH_PORT = 22

    def __init__(
            self,
            server: Server,
            executor: CommandInterface,
            ip_address: str,
    ):
        self.server = server
        self.executor = executor
        self.ip_address = ip_address

    def _run_command_on_server(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = paramiko.RSAKey.from_private_key_file(f'./keys/{self.server.owner_id}_devstask')

        try:
            ssh.connect(self.ip_address, port=self.SSH_PORT, username=get_os_default_user(self.server.image), pkey=private_key)

            for command in self.executor.get_commands():
                print(f'Executing command: {command}')
                stdin, stdout, stderr = ssh.exec_command(command)
                print('Output:')
                for line in stdout:
                    print(line.strip())

                for line in stderr:
                    print(f"Err: {line.strip()}")

        except Exception as e:
            raise e
        finally:
            ssh.close()

    def run(self):
        self._add_tag(self.LOADING_TAG)
        with session_maker() as session:
            update_user_server(self.server, session)

            try:
                self._run_command_on_server()
            except Exception as e:
                print(f'Error: {e}')
                self._add_tag(self.ERROR_TAG)
            else:
                tag = self.executor.get_tag()
                if self.executor.get_action() == ExecAction.INSTALL:
                    self._add_tag(tag)
                elif self.executor.get_action() == ExecAction.DELETE:
                    self._remove_tag(tag)
            finally:
                self._remove_tag(self.LOADING_TAG)
                update_user_server(self.server, session)

    def _add_tag(self, tag):
        if self.server.tags is None:
            self.server.tags = []

        if tag not in self.server.tags:
            self.server.tags.append(tag)

    def _remove_tag(self, tag):
        if self.server.tags is None:
            self.server.tags = []

        self.server.tags.remove(tag)