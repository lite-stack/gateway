import asyncio
import time

from app.command.command import CommandInterface, ExecAction


class TorchCommand(CommandInterface):
    TAG: str = 'torch'

    def __init__(self, action: ExecAction):
        self.action = action

    def get_commands(self):
        if self.action == ExecAction.INSTALL:
            return [
                'sudo dnf install -y python3-pip'
                'pip3 install -y torch==1.10.0+cpu torchvision==0.11.1+cpu torchaudio==0.10.0+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html',
            ]
        else:
            return [
                'python - m pip uninstall - y torch'
                'python - m pip uninstall - y torchvision'
                'python - m pip uninstall - y torchaudio'
            ]

    def get_tag(self) -> str:
        return self.TAG

    def get_action(self):
        return self.action
