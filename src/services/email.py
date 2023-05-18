from datetime import datetime
from pathlib import Path
import traceback

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.conf.config import settings
from src.conf import messages
from src.services.asyncdevlogging import async_logging_to_file
from src.services.auth import AuthToken

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=EmailStr(settings.mail_from),
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = await AuthToken.create_token(data={'sub': email}, token_type='email_token')
        mail_subject = messages.EMAIL_CONFIRMATION_REQUEST
        message = MessageSchema(
            subject=mail_subject,
            recipients=[email],
            template_body={
                'subject': mail_subject,
                'host': host,
                'username': username,
                'token': token_verification
            },
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name='email_template.html')

    except ConnectionErrors as err:
        await async_logging_to_file(f'\n500:\t{datetime.now()}\t{messages.MSC500_SENDING_EMAIL}: {err}\t{traceback.extract_stack(None, 2)[1][2]}')


async def send_new_password(email: EmailStr, username: str, host: str, password: str):
    subject = 'New password'
    try:
        message = MessageSchema(
            subject=messages.PASSWORD_RESET_REQUEST,
            recipients=[email],
            template_body={
                'subject': subject,
                'host': host,
                'username': username,
                'new_password': password,
            },
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name='new_password.html')

    except ConnectionErrors as err:
        await async_logging_to_file(f'\n500:\t{datetime.now()}\t{messages.MSC500_SENDING_EMAIL}: {err}\t{traceback.extract_stack(None, 2)[1][2]}')


async def send_reset_password(email: EmailStr, username: str, host: str):
    subject = 'Reset password '
    try:
        token_verification = await AuthToken.create_token(data={'sub': email}, token_type='password_reset_token')
        message = MessageSchema(
            subject=messages.PASSWORD_RESET_REQUEST,
            recipients=[email],
            template_body={
                'subject': subject,
                'host': host,
                'username': username,
                'token': token_verification,
            },
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name='password_reset.html')

    except ConnectionErrors as err:
        await async_logging_to_file(f'\n500:\t{datetime.now()}\t{messages.MSC500_SENDING_EMAIL}: {err}\t{traceback.extract_stack(None, 2)[1][2]}')
