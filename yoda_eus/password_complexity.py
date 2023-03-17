__copyright__ = 'Copyright (c) 2023, Utrecht University'
__license__ = 'GPLv3, see LICENSE'

import string
from typing import List


def check_password_complexity(password: str) -> List[str]:
    """Checks whether a password meets EUS password complexity requirements.

       :param password: Password to check
       :returns: List of validation error messages (empty list means it meets requirements)
    """
    if len(password) == 0:
        return ["Password is empty"]

    errors = []

    if len(password) < 10:
        errors.append("Password is too short: it needs to be at least 10 characters.")
    elif len(password) > 1000:
        errors.append("Password is too long: it can be no more than 1000 characters.")

    if not (any(c.islower() for c in password)):
        errors.append("Password needs to contain at least one lowercase letter.")

    if not (any(c.isupper() for c in password)):
        errors.append("Password needs to contain at least one uppercase letter.")

    if not (any(c.isdigit() for c in password)):
        errors.append("Password needs to contain at least one digit.")

    if not (any(c in string.punctuation for c in password)):
        errors.append("Password needs to contain at least one punctuation character ({})".format(string.punctuation))

    return errors
