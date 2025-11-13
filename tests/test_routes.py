"""
Account API Service Test Suite

Test cases can be run with:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
#from service.routes import app
from service import talisman
from service import app


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"

HTTPS_ENVIRON = {'wsgi.url_scheme': 'https'}


class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)
        talisman.force_https = False

    @classmethod
    def tearDownClass(cls):
        """Run once after test suite"""
        pass

    def setUp(self):
        """Run before each test"""
        db.session.query(Account).delete()
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        """Run after each test"""
        db.session.remove()

    # -------------------- Helper Methods --------------------
    def _create_accounts(self, count):
        """Create multiple accounts for tests"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    # -------------------- Index / Health --------------------
    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["status"], "OK")

    # -------------------- Create --------------------
    def test_create_account(self):
        account = AccountFactory()
        response = self.client.post(BASE_URL, json=account.serialize(), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.headers.get("Location"))
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)

    def test_create_account_bad_data(self):
        bad_data = {"email": "test@test.com", "address": "123 Street"}  # missing 'name'
        response = self.client.post(BASE_URL, json=bad_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("Invalid account data", data["message"])

    def test_create_account_unsupported_media_type(self):
        account = AccountFactory()
        response = self.client.post(BASE_URL, json=account.serialize(), content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # -------------------- Read --------------------
    def test_get_account(self):
        account = self._create_accounts(1)[0]
        resp = self.client.get(f"{BASE_URL}/{account.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], account.name)

    def test_get_account_not_found(self):
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # -------------------- Update --------------------
    def test_update_account(self):
        account = self._create_accounts(1)[0]
        account.name = "Updated Name"
        resp = self.client.put(f"{BASE_URL}/{account.id}", json=account.serialize())
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["name"], "Updated Name")

    def test_update_account_not_found(self):
        account_data = AccountFactory().serialize()
        resp = self.client.put(f"{BASE_URL}/0", json=account_data)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_account_bad_data(self):
        account = self._create_accounts(1)[0]
        bad_data = {"email": "update@test.com"}  # missing required fields
        resp = self.client.put(f"{BASE_URL}/{account.id}", json=bad_data, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid account data", resp.get_json()["message"])

    def test_update_account_unsupported_media_type(self):
        account = self._create_accounts(1)[0]
        resp = self.client.put(f"{BASE_URL}/{account.id}", json=account.serialize(), content_type="text/html")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # -------------------- Delete --------------------
    def test_delete_account(self):
        account = self._create_accounts(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{account.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_account_not_found(self):
        resp = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_accounts(self):
        """It should list all accounts"""
        # Create some accounts first
        accounts = self._create_accounts(3)

        # Call the GET endpoint to list accounts
        resp = self.client.get(BASE_URL, content_type="application/json")

        # Assert HTTP 200 OK
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Assert that we get back 3 accounts
        data = resp.get_json()
        self.assertEqual(len(data), 3)

    def test_list_accounts_empty(self):
        """It should return an empty list if no accounts exist"""
        resp = self.client.get(BASE_URL, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data, [])

    def test_security_headers(self):
        """It should return security headers"""
        response = self.client.get('/', environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        headers = {
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'Content-Security-Policy': 'default-src \'self\'; object-src \'none\'',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        for key, value in headers.items():
            self.assertEqual(response.headers.get(key), value)


    
    def test_cors_security(self):
        """It should return a CORS header"""
        response = self.client.get('/', environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check for the CORS header
        self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')
