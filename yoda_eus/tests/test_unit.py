__copyright__ = 'Copyright (c) 2023-2026, Utrecht University'
__license__  = 'GPLv3, see LICENSE'

import re
import string
from unittest.mock import patch

from yoda_eus.app import get_random_hash
from yoda_eus.mail import _get_html_body, _get_plain_body, is_email_valid
from yoda_eus.password_complexity import check_password_complexity
from yoda_eus.util import get_validated_static_path


class TestMain:
    def test_password_validation_ok(self):
        result = check_password_complexity("Test123456789!")
        assert len(result) == 0
        # Exactly 10 characters is also accepted.
        assert check_password_complexity("Aa1!aaaaaa") == []
        # Exactly 1000 characters is also accepted
        password = "Aa1!" + "a" * 996
        assert len(password) == 1000
        assert check_password_complexity(password) == []

    def test_password_validation_empty(self):
        result = check_password_complexity("")
        assert result == ["Password is empty"]

    def test_password_validation_too_short(self):
        result = check_password_complexity("Aa1!aaaaa")
        assert result == ["Password is too short: it needs to be at least 10 characters."]

    def test_password_validation_too_long(self):
        result = check_password_complexity(200 * "Test12345!")
        assert result == ["Password is too long: it can be no more than 1000 characters."]
        password = "Aa1!" + "a" * 997
        assert len(password) == 1001
        result = check_password_complexity(password)
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

    @patch("os.path.exists")
    def test_static_loader_path_too_short(self, mock_exists):
        mock_exists.side_effect = self.exists_return_value
        # Fewer than three path segments: no asset can be addressed.
        assert (
            get_validated_static_path("/assets", "/assets", "/var/www/yoda/themes", "uu")
            is None
        )

    @patch("os.path.exists")
    def test_static_loader_not_assets_prefix(self, mock_exists):
        mock_exists.side_effect = self.exists_return_value
        # Second segment must be "assets".
        assert (
            get_validated_static_path(
                "/foo/img/logo.svg", "/foo/img/logo.svg", "/var/www/yoda/themes", "uu"
            )
            is None
        )

    @patch("os.path.exists")
    def test_static_loader_nested_subdirectory(self, mock_exists):
        mock_exists.side_effect = self.exists_return_value
        # Nested asset directories are preserved in the returned static dir.
        static_dir, asset_name = get_validated_static_path(
            "/assets/css/sub/app.css?x",
            "/assets/css/sub/app.css",
            "/var/www/yoda/themes",
            "wur",
        )
        assert static_dir == "/var/www/yoda/themes/wur/static/css/sub"
        assert asset_name == "app.css"

    def test_plain_body_email(self):
        template_parameters = {"USERNAME": "user",
                               "CREATOR": "creator",
                               "HASH_URL": "https://hashurl"}
        expected_body = """Hello user,

A Yoda account has been created for you by creator.
Please contact this person in case it is unclear why
you have received this invitation.

Yoda is a research data management system.
You can activate your account by visiting the following webpage:

https://hashurl

More information on Yoda can be found at https://www.uu.nl/yoda

Kind regards,

The Yoda External User Service"""

        assert (_get_plain_body("templates/mail/uu",
                                "invitation",
                                template_parameters)
                == expected_body)

    def test_html_body_email(self):
        template_parameters = {"USERNAME": "user",
                               "CREATOR": "creator",
                               "HASH_URL": "https://hashurl"}
        expected_body = """<!DOCTYPE html>
<html>
    <head>
        <title></title>
        <meta charset="utf-8">
    </head>
    <body>
<p>
Hello user,
</p>

<p>
A Yoda account has been created for you by creator.
Please contact this person in case it is unclear why
you have received this invitation.
</p>

<p>
Yoda is a research data management system.
You can activate your account by visiting the following webpage:
</p>

<a href="https://hashurl">https://hashurl</a>

<p>
More information on Yoda can be found 
at <a href="https://www.uu.nl/yoda">https://www.uu.nl/yoda</a>
</p>

<p>
Kind regards,
</p>

<p>
The Yoda External User Service
</p>
    </body>
</html>"""  # noqa W291
        assert (_get_html_body("templates/mail/uu",
                               "invitation",
                               template_parameters)
                == expected_body)

    def test_html_body_email_escape_text(self):
        # Ensure that we are preventing HTML injection in HTML templates
        template_parameters = {"USERNAME": "user",
                               "CREATOR": "<script>alert( 'Creator!');</script>",
                               "HASH_URL": "https://hashurl"}
        expected_body = """<!DOCTYPE html>
<html>
    <head>
        <title></title>
        <meta charset="utf-8">
    </head>
    <body>
<p>
Hello user,
</p>

<p>
A Yoda account has been created for you by &lt;script&gt;alert( &#39;Creator!&#39;);&lt;/script&gt;.
Please contact this person in case it is unclear why
you have received this invitation.
</p>

<p>
Yoda is a research data management system.
You can activate your account by visiting the following webpage:
</p>

<a href="https://hashurl">https://hashurl</a>

<p>
More information on Yoda can be found 
at <a href="https://www.uu.nl/yoda">https://www.uu.nl/yoda</a>
</p>

<p>
Kind regards,
</p>

<p>
The Yoda External User Service
</p>
    </body>
</html>"""  # noqa W291
        assert (_get_html_body("templates/mail/uu",
                               "invitation",
                               template_parameters)
                == expected_body)

    # Test cases is_email_valid
    def test_is_email_valid_normal_address(self):
        assert is_email_valid("yoda@uu.nl")

    def test_is_email_valid_empty(self):
        assert not is_email_valid("")

    def test_is_email_valid_missing_at(self):
        assert not is_email_valid("plainstring")

    def test_is_email_valid_missing_domain(self):
        assert not is_email_valid("@nodomain.nl")

    def test_is_email_valid_missing_tld(self):
        # A bare hostname without a top-level domain is not accepted.
        assert not is_email_valid("no@tld")
        assert not is_email_valid("user@localhost")

    def test_is_email_valid_double_at(self):
        assert not is_email_valid("two@@at.nl")

    def test_is_email_valid_surrounding_whitespace(self):
        # Leading/trailing whitespace is not stripped and makes the address invalid.
        assert not is_email_valid(" yoda@uu.nl ")

    def test_is_email_valid_display_name(self):
        # The "Display Name <addr>" form is not a bare address and is rejected.
        assert not is_email_valid("Yoda <yoda@uu.nl>")

    def test_is_email_valid_short_domain(self):
        # A minimal but well-formed address is accepted.
        assert is_email_valid("a@b.co")

    # get_random_hash tests
    def test_get_random_hash_length(self):
        # secrets.token_hex(32) yields 64 hexadecimal characters.
        assert len(get_random_hash()) == 64

    def test_get_random_hash_is_hex(self):
        assert re.fullmatch("[0-9a-f]{64}", get_random_hash()) is not None

    def test_get_random_hash_is_random(self):
        # Successive calls should not collide.
        hashes = {get_random_hash() for _ in range(5)}
        assert len(hashes) == 5
