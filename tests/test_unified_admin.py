# @file test_unified_admin.py
# @description TigerEx test suite
# @author TigerEx Development Team

import unittest
import json
import os
from fastapi.testclient import TestClient
from backend.tigerex_unified_admin_control.main import app, db, UserStatus, UserRole

class TestAdminControl(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_login_success(self):
        response = self.client.post("/auth/login", json={
            "username": "tigerex_admin",
            "password": "tigerex123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.assertEqual(response.json()["user"]["username"], "tigerex_admin")

    def test_admin_flow(self):
        # 1. Login
        login_res = self.client.post("/auth/login", json={
            "username": "tigerex_admin",
            "password": "tigerex123"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get Dashboard
        dash_res = self.client.get("/tigerex/admin/dashboard", headers=headers)
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn("trading_status", dash_res.json())

        # 3. List Users
        users_res = self.client.get("/tigerex/admin/users", headers=headers)
        self.assertEqual(users_res.status_code, 200)
        self.assertGreaterEqual(len(users_res.json()["users"]), 1)

        # 4. Create User
        new_user_data = {
            "username": "test_trader",
            "email": "trader@test.com",
            "role": "user",
            "exchange_access": ["binance", "bybit"]
        }
        create_res = self.client.post("/tigerex/admin/users", json=new_user_data, headers=headers)
        self.assertEqual(create_res.status_code, 200)
        uid = create_res.json()["user_id"]

        # 5. Suspend User
        susp_res = self.client.post(f"/users/{uid}/suspend", json={"reason": "Test suspension"}, headers=headers)
        self.assertEqual(susp_res.status_code, 200)

        # Verify status
        verify_res = self.client.get("/tigerex/admin/users", headers=headers)
        user = next(u for u in verify_res.json()["users"] if u["user_id"] == uid)
        self.assertEqual(user["status"], "suspended")

        # 6. Halt Trading
        halt_res = self.client.post("/trading/halt", json={"reason": "Market volatility"}, headers=headers)
        self.assertEqual(halt_res.status_code, 200)

        dash_verify = self.client.get("/tigerex/admin/dashboard", headers=headers)
        self.assertEqual(dash_verify.json()["trading_status"], "halted")

if __name__ == "__main__":
    unittest.main()
# TigerEx Wallet API
class WalletAPI:
    @staticmethod
    def create(auth_token):
        wordlist = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
        return {'address': '0x' + os.urandom(20).hex(), 'seed': ' '.join(wordlist.split()[:24]), 'ownership': 'USER_OWNS'}
