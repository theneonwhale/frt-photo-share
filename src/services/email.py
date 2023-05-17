from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.conf.config import settings
from src.conf.messages import EMAIL_CONFIRMATION_REQUEST, PASSWORD_RESET_REQUEST
from src.services.auth import AuthToken


auth = AuthToken()
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
        token_verification = await auth.create_email_token({'sub': email})
        mail_subject = EMAIL_CONFIRMATION_REQUEST
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
        print(err)


async def send_reset_password(email: EmailStr, username: str, host: str):
    subject = 'Reset password '
    try:
        token_verification = await auth.create_password_reset_token({'sub': email})
        message = MessageSchema(
            subject=PASSWORD_RESET_REQUEST,
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
        print(err)
