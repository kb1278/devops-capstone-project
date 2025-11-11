import unittest
from service.routes import app
from service.models import Account

class TestAccounts(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        Account._accounts = []

    def _create_accounts(self, n):
        accounts = []
        for i in range(n):
            acc = Account(name=f"Account {i+1}")
            acc.save()
            accounts.append(acc)
        return accounts

    def test_list_accounts(self):
        self._create_accounts(3)
        resp = self.client.get("/accounts")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(len(data), 3)

    def test_list_accounts_empty(self):
        resp = self.client.get("/accounts")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

if __name__ == "__main__":
    unittest.main()
