import base64

from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from users.tasks import send_mail
from settings import FRONTEND_HOST, RESEND_FROM_EMAIL
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="users/templates")


def urlsafe_base64_encode(s):
    return base64.urlsafe_b64encode(s).rstrip(b"\n=").decode("ascii")


def urlsafe_base64_decode(s):
    s = s.encode()
    try:
        return base64.urlsafe_b64decode(s.ljust(len(s) + len(s) % 4, b"="))
    except (LookupError, ValueError) as e:
        raise ValueError(e)


def force_bytes(s, encoding="utf-8", errors="strict"):
    if isinstance(s, bytes):
        if encoding == "utf-8":
            return s
        else:
            return s.decode("utf-8", errors).encode(encoding, errors)
    if isinstance(s, memoryview):
        return bytes(s)
    return str(s).encode(encoding, errors)


class EmailSender:
    from_email = RESEND_FROM_EMAIL

    @staticmethod
    def email_send(subject, from_email, recipient_list, html_message):
        return send_mail(subject, from_email, recipient_list, html_message)

    @staticmethod
    def get_uuid_token_url(request, obj_user, token):
        uidb64 = urlsafe_base64_encode(force_bytes(obj_user.id))
        # token = urlsafe_base64_encode(force_bytes(token.encode()))
        http = 'https://'
        return ''.join([http, FRONTEND_HOST, '/password-reset/', uidb64, '/', token, '/'])

    def send_email_reset_password(self, request, obj_user, token):
        invite_url =self.get_uuid_token_url(request, obj_user, token)
        text = """We received a request to reset your password.\n
                  If this was you, click the button below to set up a new
                  password for your account. If this wasn't you, ignore
                  this email."""
        context = {
            'title': 'Password reset',
            'body_title': 'Password reset',
            'body_text': text,
            'button_title': 'Reset password',
            'invite_url': invite_url
        }
        html = templates.get_template('main.html').render({'request':request, **context})
        # html = html.render(html)
        self.email_send(
            subject=context['title'],
            from_email=self.from_email,
            recipient_list=[obj_user.email],
            html_message=html,
        )
        return True

    def send_email_invite_new_user(self, request, obj_user):
        invite_url = self.get_uuid_token_url(request, obj_user)
        text = f"""Congratulation {obj_user.get_full_name()}!\n
                  You have been invited to join our company as {obj_user.role}\n
                  Click the button below to set up a new password for your account."""
        context = {
            'title': 'Invited to join',
            'body_title': 'Invited to join',
            'body_text': text,
            'button_title': 'set up password',
            'invite_url': invite_url
        }
        html = render_to_string('main.html', context=context, request=request)
        self.email_send(
            subject=context['title'],
            from_email=self.from_email,
            recipient_list=[obj_user.email],
            html_message=html,
        )
        return True
