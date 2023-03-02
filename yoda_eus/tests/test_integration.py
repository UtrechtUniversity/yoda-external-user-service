import base64

import pytest
from yoda_eus.app import create_app


class TestMain:
    @pytest.fixture
    def app(self):
        app = create_app(config_filename="tests/flask.test.cfg")
        app.config['PROPAGATE_EXCEPTIONS'] = True
        app.config['TRAP_BAD_REQUEST_ERRORS'] = True
        return app

    @pytest.fixture
    def test_client(self, app):
        return app.test_client()

    def test_main_page(self, test_client):
        with test_client as c:
            response = c.get('/')
            assert response.status_code == 200

    def test_config(self, app):
        assert app.config.get("INTEGRATION_TEST") == "testvalue"

    def test_no_api_secret(self, test_client):
        with test_client as c:
            response1 = c.post('/api/user/add', json={})
            assert response1.status_code == 403
            response2 = c.post('/api/user/delete', json={})
            assert response2.status_code == 403
            response3 = c.post('/api/user/auth-check', json={})
            assert response3.status_code == 403

    def test_wrong_api_secret(self, test_client):
        auth_headers = {'HTTP_X_YODA_EXTERNAL_USER_SECRET': "wrong_secret"}
        with test_client as c:
            response1 = c.post('/api/user/add', json={}, headers=auth_headers)
            assert response1.status_code == 403
            response2 = c.post('/api/user/delete', json={}, headers=auth_headers)
            assert response2.status_code == 403
            response3 = c.post('/api/user/auth-check', json={}, headers=auth_headers)
            assert response3.status_code == 403

    def test_delete_nonexisting(self, test_client):
        auth_headers = {'HTTP_X_YODA_EXTERNAL_USER_SECRET': 'dummy_api_secret'}
        params = {"username": "notexisting", "userzone": "shouldnotmatter"}
        with test_client as c:
            response = c.post('/api/user/delete', json=params, headers=auth_headers)
            assert response.status_code == 404

    def test_add_and_remove_user_once(self, test_client):
        auth_headers = {'HTTP_X_YODA_EXTERNAL_USER_SECRET': 'dummy_api_secret'}
        username = "testuser"
        creator_user = "technicaladmin"
        creator_zone = "testZone"
        add_params = {"username": username, "creator_user": creator_user, "creator_zone": creator_zone}
        rm_params = {"username": username, "userzone": creator_zone}

        with test_client as c:
            response1 = c.post('/api/user/add', json=add_params, headers=auth_headers)
            assert response1.status_code == 201
            response2 = c.post('/api/user/delete', json=rm_params, headers=auth_headers)
            assert response2.status_code == 204

    def test_add_and_remove_user_twice(self, test_client):
        auth_headers = {'HTTP_X_YODA_EXTERNAL_USER_SECRET': 'dummy_api_secret'}
        username = "testuser"
        creator_user = "technicaladmin"
        creator_zone1 = "testZone1"
        creator_zone2 = "testZone2"
        add1_params = {"username": username, "creator_user": creator_user, "creator_zone": creator_zone1}
        add2_params = {"username": username, "creator_user": creator_user, "creator_zone": creator_zone2}
        rm1_params = {"username": username, "userzone": creator_zone1}
        rm2_params = {"username": username, "userzone": creator_zone2}

        with test_client as c:
            response1 = c.post('/api/user/add', json=add1_params, headers=auth_headers)
            assert response1.status_code == 201
            response2 = c.post('/api/user/add', json=add2_params, headers=auth_headers)
            assert response2.status_code == 200
            response3 = c.post('/api/user/delete', json=rm1_params, headers=auth_headers)
            assert response3.status_code == 204
            response4 = c.post('/api/user/delete', json=rm2_params, headers=auth_headers)
            assert response4.status_code == 204

    def test_forgot_password_show_form(self, test_client):
        with test_client as c:
            response = c.get('/user/forgot-password')
            assert response.status_code == 200

    def test_forgot_password_nonexistent(self, test_client):
        with test_client as c:
            response = c.post('/user/forgot-password', json={"f-forgot-password-username": "doesnotexist"})
            assert response.status_code == 404

    def test_forgot_password_existing(self, test_client):
        auth_headers = {'HTTP_X_YODA_EXTERNAL_USER_SECRET': 'dummy_api_secret'}
        username = "testforgotuser"
        creator_user = "technicaladmin"
        creator_zone = "testZone"
        add_params = {"username": username, "creator_user": creator_user, "creator_zone": creator_zone}

        with test_client as c:
            response1 = c.post('/api/user/add', json=add_params, headers=auth_headers)
            assert response1.status_code == 201
            response2 = c.post('/user/forgot-password', json={"f-forgot-password-username": username})
            assert response2.status_code == 200

    def test_activate_no_hash(self, test_client):
        with test_client as c:
            response1 = c.get('/user/activate')
            assert response1.status_code == 404
            response2 = c.get('/user/activate/')
            assert response2.status_code == 404

    def test_activate_wrong_hash(self, test_client):
        with test_client as c:
            response = c.get('/user/activate/wronghash')
            assert response.status_code == 403

    def test_activate_wrong_form_input(self, test_client):
        activate_url = '/user/activate/goodhash'
        mismatched_passwords_params = {"f-activation-username": "unactivatedusername",
                                       "f-activation-password": "Test1234567!!!",
                                       "f-activation-password-repeat": "Test7654321!!!",
                                       "cb-activation-tou": ""}
        toosimple_password_params = {"f-activation-username": "unactivatedusername",
                                     "f-activation-password": "Test",
                                     "f-activation-password-repeat": "Test",
                                     "cb-activation-tou": ""}
        tou_not_accepted_params = {"f-activation-username": "unactivatedusername",
                                   "f-activation-password": "Test1234567!!!",
                                   "f-activation-password-repeat": "Test1234567!!!"}
        multiple_problems_params = {"f-activation-username": "unactivatedusername",
                                    "f-activation-password": "Test",
                                    "f-activation-password-repeat": "Test1234567!!!"}
        missing_field_params = {"f-activation-username": "unactivatedusername",
                                "f-activation-password": "Test1234567!!!",
                                "cb-activation-tou": ""}
        with test_client as c:
            response1 = c.post(activate_url, json=mismatched_passwords_params)
            assert response1.status_code == 422
            response2 = c.post(activate_url, json=toosimple_password_params)
            assert response2.status_code == 422
            response3 = c.post(activate_url, json=tou_not_accepted_params)
            assert response3.status_code == 422
            response4 = c.post(activate_url, json=multiple_problems_params)
            assert response4.status_code == 422
            response5 = c.post(activate_url, json=missing_field_params)
            assert response5.status_code == 422

    def test_activate_and_check_auth(self, test_client):
        username = "unactivateduser"
        password = "Test1234567!!!"
        good_credentials = username + ":" + password
        bad_credentials = username + ":wrongpassword"
        good_credentials_base64 = base64.b64encode(good_credentials.encode('utf-8')).decode('utf-8')
        bad_credentials_base64 = base64.b64encode(bad_credentials.encode('utf-8')).decode('utf-8')
        auth_headers_ok = {'HTTP_X_YODA_EXTERNAL_USER_SECRET': 'dummy_api_secret',
                           'Authorization': 'Basic ' + good_credentials_base64}
        auth_headers_wrong_password = {'HTTP_X_YODA_EXTERNAL_USER_SECRET': 'dummy_api_secret',
                                       'Authorization': 'Basic ' + bad_credentials_base64}

        activate_url = '/user/activate/goodhash'
        password = "Test1234567!!!"
        good_params = {"f-activation-username": username,
                       "f-activation-password": password,
                       "f-activation-password-repeat": password,
                       "cb-activation-tou": ""}
        with test_client as c:
            response1 = c.post(activate_url, json=good_params)
            assert response1.status_code == 200
            response2 = c.post('/api/user/auth-check', headers=auth_headers_ok)
            assert response2.status_code == 200
            response3 = c.post('/api/user/auth-check', headers=auth_headers_wrong_password)
            assert response3.status_code == 401

    def test_auth_check_user_does_not_exist(self, test_client):
        bad_credentials = "userdoesnotexist:somepassword"
        bad_credentials_base64 = base64.b64encode(bad_credentials.encode('utf-8')).decode('utf-8')
        auth_headers = {'HTTP_X_YODA_EXTERNAL_USER_SECRET': 'dummy_api_secret',
                        'Authorization': 'Basic ' + bad_credentials_base64}
        with test_client as c:
            response = c.post('/api/user/auth-check', headers=auth_headers)
            assert response.status_code == 401