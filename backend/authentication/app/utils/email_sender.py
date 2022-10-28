import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from platform import python_version

from backend.authentication.app.config import config

# from ..config import config

recipients = ['mr.jibrik@mail.ru']
subject = 'Проект Aniblog. Подтверждение регистрации аккаунта.'
text = """Привет! Рад приветствовать тебя на портале <b>https://www.Aniblog.com/</b>!. 
        Для подтверждения регистрации перейдите по ссылке ниже:
        <h1>https://www.google.com/</h1> 
        Надеюсь, тебе у нас понравится!"""
html = '<html><head></head><body><p>' + text + '</p></body></html>'

filepath = "fish.png"
basename = os.path.basename(filepath)
filesize = os.path.getsize(filepath)

msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = 'Python script <' + config.work_email + '>'
msg['To'] = ', '.join(recipients)
msg['Reply-To'] = config.work_email
msg['Return-Path'] = config.work_email
msg['X-Mailer'] = 'Python/' + (python_version())

part_text = MIMEText(text, 'plain')
part_html = MIMEText(html, 'html')
part_file = MIMEBase('application', 'octet-stream; name="{}"'.format(basename))
part_file.set_payload(open(filepath, "rb").read())
part_file.add_header('Content-Description', basename)
part_file.add_header('Content-Disposition', 'attachment; filename="{}"; size={}'.format(basename, filesize))
encoders.encode_base64(part_file)

msg.attach(part_text)
msg.attach(part_html)
msg.attach(part_file)

mail = smtplib.SMTP_SSL(config.smtp_server)
mail.login(config.work_email, config.email_password)
mail.sendmail(config.work_email, recipients, msg.as_string())
mail.quit()
