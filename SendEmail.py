import smtplib
import email
import mimetypes
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email import encoders
import os


class BaseEmail:
    host, port = None, None
    _server = smtplib.SMTP()

    def __init__(self, sender: str, receiver: str, subject, message, message_type='plain', logger=None, server=None):
        self.msg = MIMEMultipart()

        self.msg['From'] = sender
        self.msg['To'] = receiver
        self.msg['Subject'] = subject
        self.msg['Cc'] = ''
        self.msg['Bcc'] = ''

        if server:
            self._server = server

        self.msg.attach(MIMEText(message, message_type))

    @classmethod
    def connect(cls):
        cls._server = smtplib.SMTP(host=cls.host, port=cls.port)
        cls._server.connect(host=cls.host, port=cls.port)
        cls._server.ehlo()
        cls._server.starttls()

    def _add_to_field(self, field, value):
        if type(value) != list:
            value = [value]
        self.msg[field] = email.utils.COMMASPACE.join((self.msg[field].split(email.utils.COMMASPACE) + value))

    def to(self, address):
        self._add_to_field('To', address)

    def cc(self, address):
        self._add_to_field('Cc', address)

    def bcc(self, address):
        self._add_to_field('Bcc', address)

    def add_attachment_simple(self, file):
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(file, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                        % os.path.basename(file))
        self.msg.attach(part)

    def add_attachment(self, path, file_name):
        ctype, encoding = mimetypes.guess_type(path)

        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"

        maintype, subtype = ctype.split("/", 1)

        if maintype == "text":
            fp = open(path)
            # Note: we should handle calculating the charset
            attachment = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == "image":
            fp = open(path, "rb")
            attachment = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == "audio":
            fp = open(path, "rb")
            attachment = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(path, "rb")
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(attachment)

        attachment.add_header("Content-Disposition", "attachment", file_name=file_name)
        self.msg.attach(attachment)

    def send(self):
        self._server.send_message(self.msg)


# BaseEmail.host = '10.22.15.2'
# BaseEmail.port = '25'
# BaseEmail.connect()
