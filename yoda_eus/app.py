#!/usr/bin/env python3

__copyright__ = 'Copyright (c) 2023, Utrecht University'
__license__ = 'GPLv3, see LICENSE'

import secrets
import urllib.parse
from datetime import datetime
from os import path
from typing import Dict

import bcrypt
from flask import abort, Flask, jsonify, make_response, render_template, request, Response, send_from_directory
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from jinja2 import ChoiceLoader, FileSystemLoader
from yoda_eus.mail import send_email_template


db = SQLAlchemy()


class User(db.Model):
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


class UserZone(db.Model):
    __tablename__ = "user_zones"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    inviter_user = db.Column(db.String(255), nullable=False)
    inviter_zone = db.Column(db.String(255), nullable=False, primary_key=True, index=True)
    inviter_time = db.Column(db.TIMESTAMP, nullable=False)
    user = db.relationship("User", back_populates="user_zones")


def create_app(config_filename="flask.cfg") -> Flask:
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

    @app.route('/')
    @csrf_exempt
    def index() -> Response:
        return render_template('index.html')

    @app.route('/api/user/auth-check', methods=['POST'])
    @csrf_exempt
    def auth_check() -> Response:
        try:
            username = request.authorization.username
            password = request.authorization.password
        except BaseException:
            response_content = {"status": "error", "message": "Did not receive authorization credentials."}
            response = make_response(jsonify(response_content), 401)
            response.headers["WWW-Authenticate"] = "Basic realm = \"yoda-extuser\""
            return response

        user = User.query.filter_by(username=username).first()
        if user is None or user.password == "" or not bcrypt.checkpw(password, user.password):
            response_content = {"status": "error", "message": "Incorrect credentials."}
            response = make_response(jsonify(response_content), 401)
            response.headers["WWW-Authenticate"] = "Basic realm = \"yoda-extuser\""
            return response
        else:
            response = make_response("Authenticated", 200)
            return response

    @app.route('/api/user/delete', methods=['POST'])
    @csrf_exempt
    def delete_user() -> Response:
        content = request.json

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
        content = request.json
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

            if app.config.get("MAIL_ENABLED").lower() != "false":
                # Send invitation
                hash_url = "https://{}/user/activate/{}".format(app.config.get("YODA_EUS_FQDN"),
                                                                secret_hash)
                invitation_data = {'USERNAME': content['username'],
                                   'CREATOR': content["creator_user"],
                                   'HASH_URL': hash_url}
                send_email_template(app,
                                    content['username'],
                                    'Welcome to Yoda!',
                                    "invitation",
                                    **invitation_data)

                # Send invitation confirmation
                confirmation_data = {"USERNAME": content['username'],
                                     "CREATOR": content['creator_user']}
                send_email_template(app,
                                    content["username"],
                                    'You have invited an external user to Yoda',
                                    'invitation-sent',
                                    **confirmation_data)

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
        """Add security headers."""  # noqa DAR101 DAR201

        # Content Security Policy (CSP)
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'self'; form-action 'self'; object-src 'none'"  # noqa: E501

        # X-Content-Type-Options
        response.headers['X-Content-Type-Options'] = 'nosniff'

        return response

    @app.before_request
    def check_api_secret() -> Response:
        secret_header = 'HTTP_X_YODA_EXTERNAL_USER_SECRET'
        if not (request.path.startswith("/api/")):
            return
        elif secret_header in request.headers and request.headers[secret_header] == app.config.get("API_SECRET"):
            return
        else:
            abort(403)

    @app.before_request
    def static_loader() -> Response:
        """
        Static files handling - recognisable through '/assets/'
        Override requested static file if present in user_static_area
        If not present fall back to the standard supplied static file

        /assets - for the root of the application
        /static - for the static files

        :returns: Static file
        """
        if request.full_path.split('/')[1] == 'assets':
            user_static_area = path.join(app.config.get('YODA_THEME_PATH'), app.config.get('YODA_THEME'))
            asset_dir, asset_name = path.split(request.path)
            static_dir = asset_dir.replace('/assets', user_static_area + '/static')
            user_static_filename = path.join(static_dir, asset_name)

            if not path.exists(user_static_filename):
                static_dir = asset_dir.replace('/assets', '/var/www/yoda/static')

            return send_from_directory(static_dir, asset_name)

    @ app.url_defaults
    def add_cache_buster(endpoint: str, values: Dict[str, str]) -> None:
        """Add cache buster to asset (static) URLs."""
        if endpoint.endswith("static"):
            values['q'] = app.config.get('YODA_EUS_COMMIT')

    return app


def get_random_hash():
    return secrets.token_hex(64)


if __name__ == "__main__":
    create_app().run()
