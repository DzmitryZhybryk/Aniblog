import smtplib

from email.mime.text import MIMEText
from socket import gaierror
from fastapi import HTTPException, status

from backend.authentication.app.config import email_sender_config


class EmailSender:

    def __init__(self, recipient: str):
        self.recipient = recipient
        self.work_email = email_sender_config.work_email
        self.email_password = email_sender_config.email_password
        self.smtp_server_host = email_sender_config.smtp_server_host
        self.smtp_server_port = email_sender_config.smtp_server_port

    @staticmethod
    def _read_template() -> str:
        try:
            with open("template.html") as file:
                template = file.read()
                return template
        except IOError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The template was doesn't found")

    def _email_config(self, msg: MIMEText) -> MIMEText:
        msg["From"] = self.work_email
        msg["To"] = self.recipient
        msg["Subject"] = "Проект Aniblog. Подтверждение регистрации."
        return msg

    def send_email(self):
        try:
            server = smtplib.SMTP(self.smtp_server_host, self.smtp_server_port)
            server.starttls()
            server.login(self.work_email, self.email_password)
            # msg = MIMEText(self._read_template(), "html")
            msg = MIMEText("Какое-то сообщение")
            server.sendmail(self.work_email, self.recipient, msg.as_string())
            return "Сообщение было успешно отправлено"
        except gaierror:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Проблема с отправкой сообщения")


if __name__ == '__main__':
    d = EmailSender("mr.zhybryk@gmail.com")
    d.send_email()
