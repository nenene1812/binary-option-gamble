from django.core.mail import EmailMessage
import uuid


class Util:
    @staticmethod 
    def send_email(data):
        email = EmailMessage(subject=data['email_subject'],
                                body=data['email_body'],
                                to=[data['to_email']])
        email.send()


def generate_ref_code():
    uuid = uuid.uuid4()
    return uuid