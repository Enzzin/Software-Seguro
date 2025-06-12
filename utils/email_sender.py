# utils/email_sender.py
"""
Camada fina para envio de e-mail.
– Respeita as flags MAIL_USE_SSL / MAIL_USE_TLS
– Caso porta 465 mas MAIL_USE_SSL=false, força SMTP_SSL
"""

from flask import current_app
from flask_mail import Message
from extensions import mail

import smtplib, ssl

def _manual_ssl_send(subject: str, recipients: list[str], html: str, text: str | None = None):
    """Fallback: conexão manual SMTP-SSL (porta 465)."""
    cfg = current_app.config
    context = ssl.create_default_context()
    username = cfg["MAIL_USERNAME"]
    password = cfg["MAIL_PASSWORD"]

    with smtplib.SMTP_SSL(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], context=context) as server:
        server.login(username, password)
        for rcpt in recipients:
            server.sendmail(
                username,
                rcpt,
                f"Subject: {subject}\n"
                f"From: {username}\n"
                f"To: {rcpt}\n"
                f"MIME-Version: 1.0\n"
                f"Content-Type: text/html; charset=UTF-8\n\n"
                f"{html}"
            )

def send_email(
    subject: str,
    recipients: list[str],
    html_body: str,
    text_body: str | None = None,
) -> None:
    """Envia e-mail usando Flask-Mail ou fallback SMTP_SSL."""
    cfg = current_app.config
    port      = int(cfg.get("MAIL_PORT", 0))
    use_ssl   = cfg.get("MAIL_USE_SSL", False)
    use_tls   = cfg.get("MAIL_USE_TLS", False)

    # se config está OK, deixa o Flask-Mail cuidar
    if (port == 465 and use_ssl) or (port == 587 and use_tls):
        msg = Message(
            subject   = subject,
            recipients= recipients,
            html      = html_body,
            body      = text_body or ""
        )
        mail.send(msg)
        return

    # caso contrário força SSL quando porta for 465
    if port == 465 and not use_ssl:
        _manual_ssl_send(subject, recipients, html_body, text_body)
        return

    # último recurso: tentamos SMTP padrão + STARTTLS manual
    username = cfg["MAIL_USERNAME"]
    password = cfg["MAIL_PASSWORD"]

    with smtplib.SMTP(cfg["MAIL_SERVER"], port) as server:
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.login(username, password)
        for rcpt in recipients:
            server.sendmail(
                username,
                rcpt,
                f"Subject: {subject}\n"
                f"From: {username}\n"
                f"To: {rcpt}\n"
                f"MIME-Version: 1.0\n"
                f"Content-Type: text/html; charset=UTF-8\n\n"
                f"{html_body}"
            )
