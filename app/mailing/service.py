from typing import Any

from fastapi import BackgroundTasks
from fastapi_mail import MessageSchema, FastMail, MessageType

from app.mailing.config import conf


async def send_email(
        background_tasks: BackgroundTasks,
        subject: str,
        email_to: str,
        body: dict[str, Any],
        files: list,
        template_name: str,
):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body,
        subtype=MessageType.html,
        attachments=files
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message, template_name)
