__copyright__ = 'Copyright (c) 2023, Utrecht University'
__license__ = 'GPLv3, see LICENSE'

import string

from yoda_eus.password_complexity import check_password_complexity


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

    def test_password_validation_multiple(self):
        result = check_password_complexity("Test")
        assert len(result) == 3
        assert "Password is too short: it needs to be at least 10 characters." in result
        assert "Password needs to contain at least one digit." in result
        assert "Password needs to contain at least one punctuation character ({})".format(string.punctuation) in result
