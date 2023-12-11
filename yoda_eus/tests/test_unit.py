__copyright__ = "Copyright (c) 2023, Utrecht University"
__license__   = "GPLv3, see LICENSE"

import string
from unittest.mock import patch

from yoda_eus.mail import is_email_valid
from yoda_eus.password_complexity import check_password_complexity
from yoda_eus.util import get_validated_static_path


class TestMain:
    def test_password_validation_ok(self):
        result = check_password_complexity("Test123456789!")
        assert len(result) == 0

    def test_password_validation_empty(self):
        result = check_password_complexity("")
        assert result == ["Password is empty"]

    def test_password_validation_too_short(self):
        result = check_password_complexity("Tt1!")
        assert result == ["Password is too short: it needs to be at least 10 characters."]

    def test_password_validation_too_long(self):
        result = check_password_complexity(200 * "Test12345!")
        assert result == ["Password is too long: it can be no more than 1000 characters."]

    def test_password_validation_no_lowercase(self):
        result = check_password_complexity("TEST123456789!")
        assert result == ["Password needs to contain at least one lowercase letter."]

    def test_password_validation_no_uppercase(self):
        result = check_password_complexity("test123456789!")
        assert result == ["Password needs to contain at least one uppercase letter."]

    def test_password_validation_no_digit(self):
        result = check_password_complexity("TestTestTest!")
        assert result == ["Password needs to contain at least one digit."]

    def test_password_validation_no_punctuation(self):
        result = check_password_complexity("Test123456789")
        assert result == ["Password needs to contain at least one punctuation character ({})".format(string.punctuation)]

    def test_password_validation_backslash(self):
        result = check_password_complexity("Test\\123456789!")
        assert result == ["Password must not contain backslashes."]

    def test_password_validation_multiple(self):
        result = check_password_complexity("Test")
        assert len(result) == 3
        assert "Password is too short: it needs to be at least 10 characters." in result
        assert "Password needs to contain at least one digit." in result
        assert (
            "Password needs to contain at least one punctuation character ({})".format(
                string.punctuation
            )
            in result
        )

    def is_email_valid_yes(self):
        assert is_email_valid("yoda@uu.nl")

    def is_email_valid_no(self):
        assert not is_email_valid("this is not a valid email address")

    def exists_return_value(self, pathname):
        """ Mock path.exists function. True if path does not contain "theme" and "uu" """
        return not ("theme" in pathname and "uu" in pathname)

    @patch("os.path.exists")
    def test_static_loader_valid_path(self, mock_exists):
        mock_exists.side_effect = self.exists_return_value
        # uu theme
        static_dir, asset_name = get_validated_static_path(
            "/assets/img/logo.svg?wekr",
            "/assets/img/logo.svg",
            "/var/www/yoda/themes",
            "uu",
        )
        assert static_dir == "/var/www/yoda/static/img"
        assert asset_name == "logo.svg"
        # other theme
        static_dir, asset_name = get_validated_static_path(
            "/assets/img/logo.svg?wekr",
            "/assets/img/logo.svg",
            "/var/www/yoda/themes",
            "wur",
        )
        assert static_dir == "/var/www/yoda/themes/wur/static/img"
        assert asset_name == "logo.svg"

    @patch("os.path.exists")
    def test_static_loader_invalid_path(self, mock_exists):
        mock_exists.side_effect = self.exists_return_value
        # Too short
        assert (
            get_validated_static_path("/?sawerw", "/", "/var/www/yoda/themes", "uu")
            is None
        )
        # Path traversal attack
        assert (
            get_validated_static_path(
                "/assets/../../../../etc/passwd?werwrwr",
                "/assets/../../../../etc/passwd",
                "/var/www/yoda/themes",
                "uu",
            )
            is None
        )
        # non-printable characters
        full_path = "/assets/" + chr(13) + "img/logo.svg?werwer"
        path = "/assets/" + chr(13) + "img/logo.svg"
        assert (
            get_validated_static_path(full_path, path, "/var/www/yoda/themes", "uu")
            is None
        )
        assert (
            get_validated_static_path(full_path, path, "/var/www/yoda/themes", "wur")
            is None
        )
        # non-printable characters in asset name
        full_path = "/assets/img/l" + chr(13) + "ogo.svg?werwer"
        path = "/assets/img/l" + chr(13) + "ogo.svg"
        assert (
            get_validated_static_path(full_path, path, "/var/www/yoda/themes", "uu")
            is None
        )
        assert (
            get_validated_static_path(full_path, path, "/var/www/yoda/themes", "wur")
            is None
        )
        # .. in file name
        assert (
            get_validated_static_path(
                "/assets/img/lo..go.svg?sklaerw",
                "/assets/img/lo..go.svg?sklaerw",
                "/var/www/yoda/themes",
                "uu",
            )
            is None
        )
