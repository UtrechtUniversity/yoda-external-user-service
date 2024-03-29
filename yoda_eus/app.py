#!/usr/bin/env python3

__copyright__ = 'Copyright (c) 2023, Utrecht University'
__license__   = 'GPLv3, see LICENSE'

import secrets
import urllib.parse
from datetime import datetime
from os import path
from typing import Any, Dict, Optional

import bcrypt
from flask import abort, Flask, jsonify, make_response, render_template, request, Response, send_from_directory
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from jinja2 import ChoiceLoader, FileSystemLoader
from yoda_eus.mail import is_email_valid, send_email_template_if_needed
from yoda_eus.password_complexity import check_password_complexity
from yoda_eus.util import get_validated_static_path


db = SQLAlchemy()


class User(db.Model):  # type: ignore
    """
    This class provides the ORM model for the users table, which stores data about external users.
    Their username is their email address. The hash columns refer to the secret hash value that is
    used for authenticating account activation and password resets. The creator columns refer to
    the Yoda user who invited this external user.
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, db.Sequence("users_id_seq"), primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password = db.Column(db.String(60))
    hash = db.Column(db.String(64), unique=True)
    hash_time = db.Column(db.TIMESTAMP)
    creator_time = db.Column(db.TIMESTAMP, nullable=False)
    creator_user = db.Column(db.String(255), nullable=False)
    creator_zone = db.Column(db.String(255), nullable=False)
    user_zones = db.relationship("UserZone", back_populates="user")


class UserZone(db.Model):  # type: ignore
    """
    This class provides the ORM model for the user_zones table, which stores data about invitations.
    It is possible that external users have been invited by more than one Yoda user. For example, this can
    happen if an EUS instance is shared by multiple Yoda instances. EUS keeps tracks of invitations in order
    to determine when an account can be removed completely.
    """
    __tablename__ = "user_zones"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    inviter_user = db.Column(db.String(255), nullable=False)
    inviter_zone = db.Column(db.String(255), nullable=False, primary_key=True, index=True)
    inviter_time = db.Column(db.TIMESTAMP, nullable=False)
    user = db.relationship("User", back_populates="user_zones")


def create_app(config_filename: str = "flask.cfg", enable_api: bool = True) -> Flask:
    # create a minimal app
    app = Flask(__name__,
                static_folder="/var/www/yoda/static/",
                static_url_path="/assets",
                template_folder="templates/web")

    # Load configuration
    with app.app_context():
        app.config.from_pyfile(config_filename)

    # Configure database connection
    if "DB_OVERRIDE_URI" in app.config:
        app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get("DB_OVERRIDE_URI")
    else:
        encoded_db_username = urllib.parse.quote_plus(app.config.get("DB_USER"))
        encoded_db_password = urllib.parse.quote_plus(app.config.get("DB_PASSWORD"))
        app.config["SQLALCHEMY_DATABASE_URI"] = \
            "{}://{}:{}@{}/{}".format(app.config.get("DB_DIALECT"),
                                      encoded_db_username,
                                      encoded_db_password,
                                      app.config.get("DB_HOST"),
                                      app.config.get("DB_NAME"))

    # Initialize database
    db.init_app(app)

    # Create database schema, if needed
    with app.app_context():
        db.create_all()
        db.session.commit()

    # Add CSRF protection
    if app.config.get("CSRF_TOKENS_ENABLED").lower() != "false":
        csrf = CSRFProtect()
        csrf.init_app(app)

        def csrf_tokens_enabled():
            return True
        app.jinja_env.globals.update(csrf_tokens_enabled=csrf_tokens_enabled)
    else:
        def csrf_tokens_enabled():
            return False
        app.jinja_env.globals.update(csrf_tokens_enabled=csrf_tokens_enabled)

    def csrf_exempt(f):
        if app.config.get("CSRF_TOKENS_ENABLED").lower() != "false":
            return csrf.exempt(f)
        else:
            return f

    # Add theme loader.
    theme = app.config.get('YODA_THEME', "uu")
    theme_path = app.config.get('YODA_THEME_PATH', "/var/www/yoda/themes")
    full_theme_path = path.join(theme_path, theme)
    theme_loader = ChoiceLoader([
        FileSystemLoader(full_theme_path),
        app.jinja_loader,
    ])
    app.jinja_loader = theme_loader

    # Initialize sessions
    Session(app)

    # Load test data if required for integration tests
    if app.config.get("LOAD_TEST_DATA", "false").lower() != "false":
        with app.app_context():
            now = datetime.now()
            hashed_password = bcrypt.hashpw("Test123456!!!".encode("utf-8"), bcrypt.gensalt())
            for n in range(1, 6):
                unactivated_user = User(username="unactivateduser" + str(n),
                                        creator_time=now,
                                        creator_user="creator",
                                        creator_zone="testZone",
                                        hash="goodhash" + str(n),
                                        hash_time=now)
                db.session.add(unactivated_user)
            activated_user = User(username="activateduser",
                                  creator_time=now,
                                  creator_user="creator",
                                  creator_zone="testZone",
                                  hash="resethash",
                                  hash_time=now,
                                  password=hashed_password.decode('utf-8'))
            db.session.add(activated_user)
            db.session.commit()
            for user in [activated_user, unactivated_user]:
                new_user_zone = UserZone(user_id=user.id,
                                         inviter_time=now,
                                         inviter_user="creator",
                                         inviter_zone="testZone")
                db.session.add(new_user_zone)

    @app.route('/')
    @csrf_exempt
    def index() -> Response:
        """
        The index page can be used for determining whether the EUS is available (e.g. in a basic load balancer
        health check).

        :Returns: Flask response (shows themed empty page)
        """
        return render_template('index.html')

    @app.route('/api/user/auth-check', methods=['POST'])
    @csrf_exempt
    def auth_check() -> Response:
        """
        API endpoint used by Yoda to authenticate external users. The credentials are provided
        via basic authentication.

        :Returns: Flask response (200 "Authenticated" if credentials match; otherwise
                  401 + JSON response.
        """
        try:
            username = request.authorization.username
            password = request.authorization.password
        except BaseException:
            response_content = {"status": "error", "message": "Did not receive authorization credentials."}
            response = make_response(jsonify(response_content), 401)
            response.headers["WWW-Authenticate"] = "Basic realm = \"yoda-extuser\""
            return response

        def fail_incorrect_credentials():
            response_content = {"status": "error", "message": "Incorrect credentials."}
            response = make_response(jsonify(response_content), 401)
            response.headers["WWW-Authenticate"] = "Basic realm = \"yoda-extuser\""
            return response

        user = User.query.filter_by(username=username).first()
        if user is None or user.password == "":
            return fail_incorrect_credentials()

        password_to_check = password.rstrip('\n\r\0').encode("utf-8")
        hash_to_check = user.password.encode('utf-8')
        if bcrypt.checkpw(password_to_check, hash_to_check):
            return make_response("Authenticated", 200)
        else:
            return fail_incorrect_credentials()

    @app.route('/api/user/delete', methods=['POST'])
    @csrf_exempt
    def delete_user() -> Response:
        """
        API endpoint used by Yoda to delete external users. It should get a POST request
        with JSON content containing a username and userzone key.

        :Returns: Flask response (JSON content with status ("ok" or "error") and message
                  field.
        """
        content = request.get_json(force=True)

        compulsory_fields = ["username", "userzone"]
        for field in compulsory_fields:
            if field not in content:
                response = {"status": "error", "message": "Missing input field: " + field}
                return jsonify(response), 401

        user = User.query.filter_by(username=content['username']).first()

        if user is None:
            response = {"status": "error", "message": "User not found."}
            return jsonify(response), 404

        # Delete zone registration
        UserZone.query.filter_by(user_id=user.id, inviter_zone=content["userzone"]).delete()

        # Delete user account if no registrations left
        if len(UserZone.query.filter_by(user_id=user.id).all()) == 0:
            User.query.filter_by(username=content['username']).delete()

        # Return result
        response = {"status": "ok", "message": "User {} deleted from zone {}.".format(content["username"],
                                                                                      content["userzone"])}
        return jsonify(response), 204

    @app.route("/api/user/add", methods=['POST'])
    @csrf_exempt
    def add_user() -> Response:
        """
        API endpoint used by Yoda to create external users. It should get a POST request
        with JSON content containing a username field, as well as a creator_user and creator_zone
        field. The username is the email address of the new external user, whereas creator_user
        and creator_zone refer to the person who invited the external user first.

        :Returns: Flask response (JSON content with status ("ok" or "error") and message
                  field.
        """
        content = request.get_json(force=True)
        now = datetime.now()

        compulsory_fields = ["username", "creator_user", "creator_zone"]
        for field in compulsory_fields:
            if field not in content:
                response = {"status": "error", "message": "Missing input field: " + field}
                return jsonify(response), 401

        user = User.query.filter_by(username=content['username']).first()

        if user is None:

            # Create new account
            secret_hash = get_random_hash()
            new_user = User(username=content["username"],
                            creator_time=now,
                            creator_user=content["creator_user"],
                            creator_zone=content["creator_zone"],
                            hash=secret_hash,
                            hash_time=now)
            db.session.add(new_user)

            created_user = User.query.filter_by(username=content['username']).first()

            # Log invitation
            new_user_zone = UserZone(user_id=created_user.id,
                                     inviter_time=now,
                                     inviter_user=content["creator_user"],
                                     inviter_zone=content["creator_zone"])
            db.session.add(new_user_zone)

            db.session.commit()

            # Send invitation
            hash_url = "https://{}/user/activate/{}".format(app.config.get("YODA_EUS_FQDN"),
                                                            secret_hash)
            invitation_data = {'USERNAME': content['username'],
                               'CREATOR': content["creator_user"],
                               'HASH_URL': hash_url}
            send_email_template_if_needed(app,
                                          content['username'],
                                          'Welcome to Yoda!',
                                          "invitation",
                                          invitation_data)

            # Send invitation confirmation
            confirmation_data = {"USERNAME": content['username'],
                                 "CREATOR": content['creator_user']}
            send_email_template_if_needed(app,
                                          content["creator_user"],
                                          'You have invited an external user to Yoda',
                                          'invitation-sent',
                                          confirmation_data)

            # Send response
            response = {"status": "ok", "message": "User created."}
            return jsonify(response), 201

        else:

            # Log invitation
            new_user_zone = UserZone(user_id=user.id,
                                     inviter_time=now,
                                     inviter_user=content["creator_user"],
                                     inviter_zone=content["creator_zone"])
            db.session.add(new_user_zone)

            # Send response
            response = {"status": "ok", "message": "User already exists."}
            return jsonify(response), 200

    @app.route("/user/forgot-password", methods=['GET'])
    def show_forgot_password_form() -> Response:
        """
         Shows the forgot password form, which can be used by external users to request
         a link to reset their password.

         :Returns: Flask response
        """
        return render_template('forgot-password.html'), 200

    @app.route("/user/forgot-password", methods=['POST'])
    def process_forgot_password() -> Response:
        """
         Processes submits of the forgot password form by (presumably) external users

         :Returns: Flask response
        """
        username = request.form.get("username", "")

        # Check form input and handle errors
        if len(username) == 0:
            errors = {"errors": ["Please enter your user name (email address)"]}
            return render_template('forgot-password.html', **errors)

        user = User.query.filter_by(username=username).first()

        if user is None:
            errors = {"errors": ["User name not found. Only external users can reset their password."]}
            response = make_response(render_template('forgot-password.html', **errors))
            response.status_code = 404
            return response

        if (not is_email_valid(username) and app.config.get("MAIL_ONLY_TO_VALID_ADDRESS").lower() == "true"):
            errors = {
                "errors": ["Unable to send password reset email, "
                           "because your user name ('{}') is not a valid email address.".format(username)]
            }
            response = make_response(render_template('forgot-password.html', **errors))
            response.status_code = 404
            return response

        # Generate and update user hash
        secret_hash = get_random_hash()
        user.hash = secret_hash
        user.hash_time = datetime.now()
        db.session.commit()

        # Send password reset email
        hash_url = "https://{}/user/reset-password/{}".format(app.config.get("YODA_EUS_FQDN"),
                                                              secret_hash)
        reset_data = {'USERNAME': user.username,
                      'HASH_URL': hash_url}
        send_email_template_if_needed(app,
                                      user.username,
                                      'Yoda password reset',
                                      "reset-password",
                                      reset_data)

        return render_template("forgot-password-successful.html"), 200

    @app.route("/user/activate/<hash>", methods=['GET', 'POST'])
    def process_activate_account_form(hash: str) -> Response:
        """
         Processes clicks on activation links that external users receive via email when
         they are invited. They can use the link to create an account.

         :param hash: account activation hash

         :Returns: Flask response
        """
        # Sanity checks secret hash
        if hash is None or hash == "":
            # Failsafe
            failed_params = {"activation_error_message": "Activation link is invalid"}
            return render_template('activation-error.html', **failed_params), 403

        params: Dict[str, Any] = {"secret_hash": hash}

        # Validate secret hash and handle errors
        users = User.query.filter_by(hash=hash).all()

        if len(users) > 1:
            # Failsafe - it should not be possible that two users have
            # the same hash.
            params = {"activation_error_message": "Internal error."}
            return render_template('activation-error.html', **params), 500
        elif len(users) == 0:
            params = {"activation_error_message": "Activation link is invalid."}
            return render_template('activation-error.html', **params), 403
        elif users[0].password != "" and users[0].password is not None:
            params = {"activation_error_message": "Sorry, your activation link is no longer valid."}
            return render_template('activation-error.html', **params), 403

        user = users[0]
        params["username"] = user.username

        # If form wasn't submitted, show it
        if request.method == "GET":
            return render_template("activate.html", **params)

        # Input validation of form data
        form_inputs = request.form

        for field in ["username", "password", "password_again"]:
            if field not in form_inputs or form_inputs[field] == "":
                params["errors"] = ['Please fill in all required fields.']
                return render_template("activate.html", **params), 422

        if form_inputs["password"] != form_inputs["password_again"]:
            params["errors"] = ["The passwords do not match"]
            return render_template("activate.html", **params), 422

        password_complexity_errors = check_password_complexity(form_inputs["password"])
        if len(password_complexity_errors) > 0:
            params["errors"] = password_complexity_errors
            return render_template("activate.html", **params), 422

        if "cb-activation-tou" not in form_inputs:
            params["errors"] = ["Please check the box for acceptance of the terms of use."]
            return render_template("activate.html", **params), 422

        # Activate account
        salt = bcrypt.gensalt()
        password = form_inputs["password"]
        user.hash = None
        user.hashtime = None
        user.password = bcrypt.hashpw(password.encode('utf8'), salt).decode('utf-8')
        db.session.commit()

        # Send confirmation emails
        activation_data = {'USERNAME': user.username}
        send_email_template_if_needed(app,
                                      user.username,
                                      'You have successfully activated your Yoda account',
                                      "activation-successful",
                                      activation_data)
        activation_data["CREATOR"] = user.creator_user
        send_email_template_if_needed(app,
                                      user.creator_user,
                                      'An external user has activated their Yoda account',
                                      "invitation-accepted",
                                      activation_data)

        # Confirm activation to user
        return render_template("activation-successful.html", **params), 200

    @app.route("/user/reset-password/<hash>", methods=['GET', 'POST'])
    def process_reset_password_form(hash: str) -> Response:
        """
        Processes clicks on passwords reset links that external users receive via email when
        they request a reset using the forgot password form. They can use the link to reset
        their password.

        :param hash: password reset hash

        :Returns: Flask response
        """
        # Sanity checks secret hash
        if hash is None or hash == "":
            # Failsafe
            failed_params = {"reset_error_message": "Password reset link is invalid"}
            return render_template('reset-password-error.html', **failed_params), 403

        params: Dict[str, Any] = {"secret_hash": hash}

        # Validate secret hash and handle errors
        users = User.query.filter_by(hash=hash).all()

        if len(users) > 1:
            # Failsafe - it should not be possible that two users have
            # the same hash.
            params = {"reset_error_message": "Internal error."}
            return render_template('reset-password-error.html', **params), 500
        elif len(users) == 0:
            params = {"reset_error_message": "Password reset link is invalid."}
            return render_template('reset-password-error.html', **params), 403

        user = users[0]
        params["username"] = user.username

        # If form wasn't submitted, show it
        if request.method == "GET":
            return render_template("reset-password.html", **params)

        # Input validation of form data
        form_inputs = request.form

        for field in ["username", "password", "password_again"]:
            if field not in form_inputs or form_inputs[field] == "":
                params["errors"] = ['Please fill in all required fields.']
                return render_template("reset-password.html", **params), 422

        if form_inputs["password"] != form_inputs["password_again"]:
            params["errors"] = ["The passwords do not match"]
            return render_template("reset-password.html", **params), 422

        password_complexity_errors = check_password_complexity(form_inputs["password"])
        if len(password_complexity_errors) > 0:
            params["errors"] = password_complexity_errors
            return render_template("reset-password.html", **params), 422

        # Reset password account
        salt = bcrypt.gensalt()
        password = form_inputs["password"]
        user.hash = None
        user.hashtime = None
        user.password = bcrypt.hashpw(password.encode('utf8'), salt).decode('utf-8')
        db.session.commit()

        # Confirm activation to user
        return render_template("reset-password-successful.html", **params), 200

    @ app.errorhandler(403)
    def access_forbidden(e: Exception) -> Response:
        return render_template('403.html'), 403

    @ app.errorhandler(404)
    def page_not_found(e: Exception) -> Response:
        return render_template('404.html'), 404

    @ app.errorhandler(500)
    def internal_error(e: Exception) -> Response:
        return render_template('500.html'), 500

    @ app.after_request
    def add_security_headers(response: Response) -> Response:
        """Add generic security headers."""  # noqa DAR101 DAR201

        # Content Security Policy (CSP)
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'self'; form-action 'self'; object-src 'none'"  # noqa: E501

        # X-Content-Type-Options
        response.headers['X-Content-Type-Options'] = 'nosniff'

        return response

    if not enable_api:
        @app.before_request
        def refuse_api_requests() -> Response:
            """
            The EUS presents two web interfaces (vhosts) on two different TCP ports. One of these
            does not have the API available, so that API access can be restricted on a TCP level (e.g. in firewalls).

            If this instance does not have the API enabled, access to API functions is intercepted
            and blocked by this function.
            """
            if request.path.startswith("/api/"):
                abort(make_response(jsonify({
                    'status': 'error',
                    'message': 'The EUS API has been disabled on this interface.'
                }), 403))

    @app.before_request
    def check_api_secret() -> Response:
        """
        This ensures that API requests can only be processed if the right API secret is provided.

        :Returns: Flask response (optionally)
        """
        secret_header = 'X-Yoda-External-User-Secret'
        if not (request.path.startswith("/api/")):
            return
        elif secret_header in request.headers and request.headers[secret_header] == app.config.get("API_SECRET"):
            return
        else:
            abort(make_response(jsonify({
                'status': 'error',
                'message': 'EUS secret header not present or does not match.'
            }), 403))

    @app.before_request
    def static_loader() -> Optional[Response]:
        """
        Static files handling - recognisable through '/assets/'
        Override requested static file if present in user_static_area
        If not present fall back to the standard supplied static file

        /assets - for the root of the application
        /static - for the static files

        :returns: Static file
        """
        result = get_validated_static_path(
            request.full_path,
            request.path,
            app.config.get('YODA_THEME_PATH'),
            app.config.get('YODA_THEME')
        )
        if result is not None:
            static_dir, asset_name = result
            return send_from_directory(static_dir, asset_name)

        return None

    @ app.url_defaults
    def add_cache_buster(endpoint: str, values: Dict[str, str]) -> None:
        """Add cache buster to asset (static) URLs."""
        if endpoint.endswith("static"):
            values['q'] = app.config.get('YODA_EUS_COMMIT')

    return app


def get_random_hash():
    """
    :Returns: random value for the password reset and account activation secrets.
    """
    return secrets.token_hex(32)


if __name__ == "__main__":
    create_app().run()
