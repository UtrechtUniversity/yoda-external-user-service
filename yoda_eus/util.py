#!/usr/bin/env python3

__copyright__ = 'Copyright (c) 2021-2023, Utrecht University'
__license__   = 'GPLv3, see LICENSE'

from typing import Optional, Tuple
from os import path
from re import fullmatch
from werkzeug.security import safe_join
from werkzeug.utils import secure_filename


def get_validated_static_path(full_path, request_path, yoda_theme_path, yoda_theme) -> Optional[Tuple[str, str]]:
    """
    Static files handling - recognisable through '/assets/'
    Confirms that input path is valid and return corresponding static path

    :param full_path: Full path of request
    :param request_path: Short path of request
    :param yoda_theme_path: Path to the yoda themes
    :param yoda_theme: Name of the chosen theme

    :returns: Tuple of static directory and filename for correct path, None for incorrect path
    """
    parts = full_path.split('/')

    if len(parts) > 2 and fullmatch('[ -~]*', full_path) is not None and parts[1] == 'assets':
        parts = parts[2:-1]
        user_static_area = path.join(yoda_theme_path, yoda_theme)
        _, asset_name = path.split(request_path)
        # Confirm that asset_name is safe
        if asset_name != secure_filename(asset_name):
            return

        static_dir = safe_join(user_static_area + '/static', *parts)
        if not static_dir:
            return
        user_static_filename = path.join(static_dir, asset_name)

        if not path.exists(user_static_filename):
            static_dir = safe_join('/var/www/yoda/static', *parts)

        return static_dir, asset_name
