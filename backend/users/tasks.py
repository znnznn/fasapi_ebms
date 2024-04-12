import resend

from settings import RESEND_API_KEY


def send_mail(subject, from_email, recipient_list, html_message):
    resend.api_key = RESEND_API_KEY
    params = {
        "from": from_email,
        "to": recipient_list,
        "subject": subject,
        "html": html_message,
    }
    resend.Emails.send(params)
