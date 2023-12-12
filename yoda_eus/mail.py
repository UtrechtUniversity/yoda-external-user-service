__copyright__ = 'Copyright (c) 2023, Utrecht University'
__license__   = 'GPLv3, see LICENSE'

import email
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from email_validator import EmailNotValidError, validate_email
from jinja2 import BaseLoader, Environment


def is_email_valid(address):
    """Determines whether an email address is valid

    :param address: the email address

    :returns: boolean value that indicates whether the email address is valid
    """
    try:
        validate_email(address, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def send_email_template_if_needed(app, to, subject, template_name, template_data):
    """Send an e-mail with specified recipient, subject and body using templates if
       application is configured to deliver it.

    An email is sent if and only if:
    - Email delivery has been enabled in the application configuration
    - The email address is valid (or email address validation has been disabled)

    The originating address and mail server credentials are taken from the
    app configuration. The templates are retrieved from the template directory
    specified in the app configuration.

    :param app:                Flask application, used for logging and retrieving configuration
    :param to:                 Recipient of the mail
    :param subject:            Subject of mail
    :param template_name:      Name of the template in the template directory to use, excluding extensions
    :param template_data:      Variables to interpolate, as a dictionary

    """
    if app.config.get("MAIL_ENABLED").lower() == "false":
        app.logger.warning("Not sending email to '{}' with subject '{}', because email delivery is disabled.".format(
                           to, subject))
        return

    if (not is_email_valid(to) and app.config.get("MAIL_ONLY_TO_VALID_ADDRESS").lower() == "true"):
        app.logger.warning("Not sending email to '{}' with subject '{}', because recipient address is invalid.".format(
            to, subject))
        return

    send_email_template(app, to, subject, template_name, template_data)


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

    plain_body_template = Environment(loader=BaseLoader).from_string(text_template)
    plain_body = plain_body_template.render(**template_data)
    html_body_template = Environment(loader=BaseLoader).from_string(html_full_template)
    html_body = html_body_template.render(**template_data)

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

    fmt_addr = '{} <{}>'.format

    mp_msg = MIMEMultipart('alternative')
    mp_msg['Reply-To'] = fmt_addr(app.config.get("SMTP_REPLYTO_NAME"),
                                  app.config.get("SMTP_REPLYTO_EMAIL"))
    mp_msg['Date'] = email.utils.formatdate()
    mp_msg['From'] = fmt_addr(app.config.get("SMTP_FROM_NAME"),
                              app.config.get("SMTP_FROM_EMAIL"))
    mp_msg['To'] = to
    mp_msg['Subject'] = subject

    # e.g. 'smtps://smtp.gmail.com:465' for SMTP over TLS, or
    # 'smtp://smtp.gmail.com:587' for STARTTLS on the mail submission port.
    proto, host, port = re.search(r'^(smtps?)://([^:]+)(?::(\d+))?$',
                                  app.config.get('SMTP_SERVER')).groups()

    # Default to port 465 for SMTP over TLS, and 587 for standard mail
    # submission with STARTTLS.
    port = int(port or (465 if proto == 'smtps' else 587))

    try:
        smtp = (smtplib.SMTP_SSL if proto == 'smtps' else smtplib.SMTP)(host, port)

        if proto != 'smtps' and app.config.get("SMTP_STARTTLS").lower() == "true":
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

    mp_msg.attach(MIMEText(plain_body, 'plain'))
    mp_msg.attach(MIMEText(html_body, 'html'))

    try:
        smtp.sendmail(app.config.get("SMTP_FROM_EMAIL"), [to], mp_msg.as_string())

    except Exception as e:
        raise Exception('[EMAIL] Could not send mail: {}'.format(e))

    try:
        smtp.quit()
    except Exception:
        pass
