import email
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from flask import render_template


def send_email_template(app, to, subject, template_name, template_data):
    """Send an e-mail with specified recipient, subject and body using templates

    The originating address and mail server credentials are taken from the
    app configuration. The templates are retrieved from the template directory
    specified in the app configuration.

    :param app:                Flask application, used for logging and retrieving configuration
    :param to:                 Recipient of the mail
    :param subject:            Subject of mail
    :param template_name:      Name of the template in the template directory to use, excluding extensions
    :param template_data:      Variables to interpolate, as a dictionary

    """
    template_path = os.path.join(app.config.get("MAIL_TEMPLATE_DIR"),
                                 app.config.get("MAIL_TEMPLATE"))

    text_template = Path(os.path.join(template_path, template_name + ".txt.j2")).read_text()
    html_main_template = Path(os.path.join(template_path, template_name + ".html.j2")).read_text()
    html_header_template = Path(os.path.join(template_path, "common-start.html.j2")).read_text()
    html_footer_template = Path(os.path.join(template_path, "common-end.html.j2")).read_text()
    html_full_template = html_header_template + html_main_template + html_footer_template

    plain_body = render_template(text_template, **template_data)
    html_body = render_template(html_full_template, **template_data)

    send_email(app, to, subject, plain_body, html_body)


def send_email(app, to, subject, plain_body, html_body):
    """Send an e-mail with specified recipient, subject and body.

    The originating address and mail server credentials are taken from the
    app configuration file.

    :param app:        Flask application, used for logging and retrieving configuration
    :param to:         Recipient of the mail
    :param subject:    Subject of mail
    :param plain_body: Body of mail (plain text)
    :param html_body:  Body of mail (HTML)

    :raises Exception: For errors during sending the email

    """
    app.logger.info('Sending mail to <{}>, subject <{}>'.format(to, subject))
    mp_msg = MIMEMultipart('alternative')

    # e.g. 'smtps://smtp.gmail.com:465' for SMTP over TLS, or
    # 'smtp://smtp.gmail.com:587' for STARTTLS on the mail submission port.
    proto, host, port = re.search(r'^(smtps?)://([^:]+)(?::(\d+))?$',
                                  app.config.get('SMTP_SERVER').groups())

    # Default to port 465 for SMTP over TLS, and 587 for standard mail
    # submission with STARTTLS.
    port = int(port or (465 if proto == 'smtps' else 587))

    try:
        smtp = (smtplib.SMTP_SSL if proto == 'smtps' else smtplib.SMTP)(host, port)

        if proto != 'smtps' and app.config.get("smtp_starttls").lower() == "true":
            # Enforce TLS.
            smtp.starttls()

    except Exception as e:
        raise Exception('[EMAIL] Could not connect to mail server at {}://{}:{}: {}'.format(proto, host, port, e))

    try:
        if app.config.get("SMTP_AUTH").lower() == "true":
            smtp.login(app.config.get("SMTP_USERNAME"),
                       app.config.get("SMTP_PASSWORD"))

    except Exception:
        raise Exception('[EMAIL] Could not login to mail server with configured credentials')

    fmt_addr = '{} <{}>'.format

    plain_msg = MIMEText(plain_body, 'plain', 'UTF-8')
    plain_msg['Reply-To'] = fmt_addr(app.config.get("SMTP_REPLYTO_NAME"),
                                     app.config.get("SMTP_REPLYTO_EMAIL"))
    plain_msg['Date'] = email.utils.formatdate()
    plain_msg['From'] = fmt_addr(app.config.get("SMTP_FROM_NAME"),
                                 app.config.get("SMTP_FROM_EMAIL"))
    plain_msg['To'] = to
    plain_msg['Subject'] = subject

    mp_msg.attach(plain_msg)
    mp_msg.attach(MIMEText(html_body, 'html'))

    try:
        smtp.sendmail(app.config.get("SMTP_FROM_EMAIL"), [to], mp_msg.as_string())

    except Exception as e:
        raise Exception('[EMAIL] Could not send mail: {}'.format(e))

    try:
        smtp.quit()
    except Exception:
        pass
