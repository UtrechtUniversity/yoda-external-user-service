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
