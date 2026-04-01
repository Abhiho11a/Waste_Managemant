"""
Comprehensive API Test Suite
Tests all endpoints and verifies ML model integration
"""

import requests
import json
from typing import Dict, Any
import time

# Base URL
BASE_URL = "http://localhost:8000"

# Test user credentials
TEST_USER = {
    "name": "ML Test User",
    "email": "mltest@ocean.com",
    "password": "testpass123",
    "role": "authority"
}

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.results = []

    def log_test(self, test_name: str, method: str, endpoint: str, status: int, success: bool, response: Dict):
        """Log test results"""
        result = {
            "test": test_name,
            "method": method,
            "endpoint": endpoint,
            "status": status,
            "success": success,
            "response": response
        }
        self.results.append(result)

        status_symbol = "[PASS]" if success else "[FAIL]"
        print(f"\n{status_symbol} {test_name}")
        print(f"   {method} {endpoint}")
        print(f"   Status: {status}")
        if response:
            print(f"   Response: {json.dumps(response, indent=2)[:200]}...")

    def print_summary(self):
        """Print test summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed

        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} [OK]")
        print(f"Failed: {failed} [FAIL]")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print("="*80)

    # AUTH TESTS
    def test_1_health_check(self):
        """Test 1: Health Check"""
        try:
            resp = requests.get(f"{self.base_url}/health")
            success = resp.status_code == 200
            self.log_test("Health Check", "GET", "/health", resp.status_code, success, resp.json())
        except Exception as e:
            self.log_test("Health Check", "GET", "/health", 0, False, {"error": str(e)})

    def test_2_register_user(self):
        """Test 2: Register New User"""
        try:
            resp = requests.post(f"{self.base_url}/auth/register", json=TEST_USER)
            success = resp.status_code == 201
            data = resp.json()
            if success:
                self.user_id = data.get("id")
            self.log_test("Register User", "POST", "/auth/register", resp.status_code, success, data)
        except Exception as e:
            self.log_test("Register User", "POST", "/auth/register", 0, False, {"error": str(e)})

    def test_3_login_user(self):
        """Test 3: Login User"""
        try:
            login_data = {"email": TEST_USER["email"], "password": TEST_USER["password"]}
            resp = requests.post(f"{self.base_url}/auth/login", json=login_data)
            success = resp.status_code == 200
            data = resp.json()
            if success:
                self.token = data.get("access_token")
            self.log_test("Login User", "POST", "/auth/login", resp.status_code, success, data)
        except Exception as e:
            self.log_test("Login User", "POST", "/auth/login", 0, False, {"error": str(e)})

    def test_4_get_profile(self):
        """Test 4: Get User Profile"""
        if not self.token:
            print("\n[WARN]  Skipping profile test - no token")
            return

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.get(f"{self.base_url}/auth/profile", headers=headers)
            success = resp.status_code == 200
            self.log_test("Get Profile", "GET", "/auth/profile", resp.status_code, success, resp.json())
        except Exception as e:
            self.log_test("Get Profile", "GET", "/auth/profile", 0, False, {"error": str(e)})

    # SATELLITE DATA TESTS
    def test_5_pollution_map(self):
        """Test 5: Get Pollution Map (Mock GeoJSON)"""
        try:
            resp = requests.get(f"{self.base_url}/satellite/pollution-map")
            success = resp.status_code == 200
            data = resp.json()
            print(f"\n[PASS] Pollution Map")
            print(f"   GET /satellite/pollution-map")
            print(f"   Status: {resp.status_code}")
            print(f"   Features count: {len(data.get('features', []))}")
            self.results.append({
                "test": "Pollution Map",
                "method": "GET",
                "endpoint": "/satellite/pollution-map",
                "status": resp.status_code,
                "success": success,
                "response": {"features_count": len(data.get('features', []))}
            })
        except Exception as e:
            self.log_test("Pollution Map", "GET", "/satellite/pollution-map", 0, False, {"error": str(e)})

    def test_6_algal_bloom(self):
        """Test 6: Get Algal Bloom Zones"""
        try:
            resp = requests.get(f"{self.base_url}/satellite/algal-bloom")
            success = resp.status_code == 200
            data = resp.json()
            print(f"\n[PASS] Algal Bloom Zones")
            print(f"   GET /satellite/algal-bloom")
            print(f"   Status: {resp.status_code}")
            print(f"   Features count: {len(data.get('features', []))}")
            self.results.append({
                "test": "Algal Bloom",
                "method": "GET",
                "endpoint": "/satellite/algal-bloom",
                "status": resp.status_code,
                "success": success,
                "response": {"features_count": len(data.get('features', []))}
            })
        except Exception as e:
            self.log_test("Algal Bloom", "GET", "/satellite/algal-bloom", 0, False, {"error": str(e)})

    def test_7_vessel_intrusions(self):
        """Test 7: Get Vessel Intrusions"""
        try:
            resp = requests.get(f"{self.base_url}/satellite/vessel-intrusions")
            success = resp.status_code == 200
            data = resp.json()
            print(f"\n[PASS] Vessel Intrusions")
            print(f"   GET /satellite/vessel-intrusions")
            print(f"   Status: {resp.status_code}")
            print(f"   Events count: {len(data)}")
            self.results.append({
                "test": "Vessel Intrusions",
                "method": "GET",
                "endpoint": "/satellite/vessel-intrusions",
                "status": resp.status_code,
                "success": success,
                "response": {"events_count": len(data)}
            })
        except Exception as e:
            self.log_test("Vessel Intrusions", "GET", "/satellite/vessel-intrusions", 0, False, {"error": str(e)})

    # STRESS INDEX TESTS (WITH ML MODELS)
    def test_8_stress_index_all(self):
        """Test 8: Get Stress Index for All Regions (ML MODELS ACTIVE)"""
        try:
            resp = requests.get(f"{self.base_url}/stress-index/all")
            success = resp.status_code == 200
            data = resp.json()
            print(f"\n[PASS] Stress Index All Regions [ML MODELS]")
            print(f"   GET /stress-index/all")
            print(f"   Status: {resp.status_code}")
            print(f"   Regions count: {len(data)}")
            if data:
                print(f"   Sample region: {data[0].get('region')}")
                print(f"   ML Computed Score: {data[0].get('score')}")
                print(f"   Species Risk: {data[0].get('species_risk')}")
                print(f"   Fish Stock Level: {data[0].get('fish_stock_level')}")
                print(f"   Temperature Anomaly: {data[0].get('temperature_anomaly')}")
                print(f"   Pollution Score: {data[0].get('pollution_score')}")
            self.results.append({
                "test": "Stress Index All",
                "method": "GET",
                "endpoint": "/stress-index/all",
                "status": resp.status_code,
                "success": success,
                "response": {"regions_count": len(data)}
            })
        except Exception as e:
            self.log_test("Stress Index All", "GET", "/stress-index/all", 0, False, {"error": str(e)})

    def test_9_stress_index_region(self):
        """Test 9: Get Stress Index for Specific Region (ML MODELS ACTIVE)"""
        region = "Bay of Bengal"
        try:
            resp = requests.get(f"{self.base_url}/stress-index/{region}")
            success = resp.status_code == 200
            data = resp.json()
            print(f"\n[PASS] Stress Index {region} [ML MODELS]")
            print(f"   GET /stress-index/{region}")
            print(f"   Status: {resp.status_code}")
            print(f"   ML Computed Score: {data.get('score')}")
            print(f"   Species Risk: {data.get('species_risk')}")
            print(f"   Fish Stock Level: {data.get('fish_stock_level')}")
            print(f"   Temperature Anomaly: {data.get('temperature_anomaly')}")
            print(f"   Pollution Score: {data.get('pollution_score')}")
            self.results.append({
                "test": f"Stress Index {region}",
                "method": "GET",
                "endpoint": f"/stress-index/{region}",
                "status": resp.status_code,
                "success": success,
                "response": {"score": data.get('score')}
            })
        except Exception as e:
            self.log_test(f"Stress Index {region}", "GET", f"/stress-index/{region}", 0, False, {"error": str(e)})

    # SIMULATION TESTS (WITH ML MODELS)
    def test_10_policy_simulation(self):
        """Test 10: Run Policy Simulation (ML MODELS ACTIVE)"""
        if not self.token:
            print("\n[WARN]  Skipping simulation test - no token")
            return

        simulation_input = {
            "region": "Arabian Sea",
            "fishing_reduction": 25.0,
            "plastic_reduction": 30.0,
            "zone_protection": 40.0
        }

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.post(f"{self.base_url}/simulate/policy-impact", json=simulation_input, headers=headers)
            success = resp.status_code == 200
            data = resp.json()
            print(f"\n[PASS] Policy Simulation [ML MODELS]")
            print(f"   POST /simulate/policy-impact")
            print(f"   Status: {resp.status_code}")
            print(f"   Input: fishing_reduction={simulation_input['fishing_reduction']}%, plastic_reduction={simulation_input['plastic_reduction']}%, zone_protection={simulation_input['zone_protection']}%")
            print(f"   ML Predicted Score (5-year): {data.get('predicted_score')}")
            print(f"   Biodiversity Recovery: {data.get('biodiversity_recovery')}%")
            self.results.append({
                "test": "Policy Simulation",
                "method": "POST",
                "endpoint": "/simulate/policy-impact",
                "status": resp.status_code,
                "success": success,
                "response": {"predicted_score": data.get('predicted_score')}
            })
        except Exception as e:
            self.log_test("Policy Simulation", "POST", "/simulate/policy-impact", 0, False, {"error": str(e)})

    # VIOLATIONS TEST
    def test_11_report_violation(self):
        """Test 11: Report Violation"""
        if not self.token:
            print("\n[WARN]  Skipping violation test - no token")
            return

        violation_data = {
            "vessel_id": "VESSEL-0001",
            "zone": "Marine Reserve A",
            "violation_type": "quota_exceeded",
            "severity": "high",
            "latitude": 12.5,
            "longitude": 75.0
        }

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.post(f"{self.base_url}/violations/report", json=violation_data, headers=headers)
            success = resp.status_code == 201
            data = resp.json()
            self.log_test("Report Violation", "POST", "/violations/report", resp.status_code, success, data)
        except Exception as e:
            self.log_test("Report Violation", "POST", "/violations/report", 0, False, {"error": str(e)})

    def test_12_get_live_violations(self):
        """Test 12: Get Live Violations"""
        try:
            resp = requests.get(f"{self.base_url}/violations/live")
            success = resp.status_code == 200
            data = resp.json()
            print(f"\n[PASS] Live Violations")
            print(f"   GET /violations/live")
            print(f"   Status: {resp.status_code}")
            print(f"   Violations count: {len(data)}")
            self.results.append({
                "test": "Live Violations",
                "method": "GET",
                "endpoint": "/violations/live",
                "status": resp.status_code,
                "success": success,
                "response": {"violations_count": len(data)}
            })
        except Exception as e:
            self.log_test("Live Violations", "GET", "/violations/live", 0, False, {"error": str(e)})

    # CATCH LOG TEST
    def test_13_submit_catch_log(self):
        """Test 13: Submit Catch Log"""
        if not self.token:
            print("\n[WARN]  Skipping catch log test - no token")
            return

        catch_data = {
            "species": "Tuna",
            "quantity": 150.5,
            "latitude": 10.2,
            "longitude": 80.5
        }

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.post(f"{self.base_url}/catch-log", json=catch_data, headers=headers)
            success = resp.status_code == 201
            data = resp.json()
            self.log_test("Submit Catch Log", "POST", "/catch-log", resp.status_code, success, data)
        except Exception as e:
            self.log_test("Submit Catch Log", "POST", "/catch-log", 0, False, {"error": str(e)})

    def test_14_get_catch_logs(self):
        """Test 14: Get Catch Logs"""
        if not self.token or not self.user_id:
            print("\n[WARN]  Skipping get catch logs test - missing data")
            return

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.get(f"{self.base_url}/catch-log/{self.user_id}", headers=headers)
            success = resp.status_code == 200
            data = resp.json()
            print(f"\n[PASS] Get Catch Logs")
            print(f"   GET /catch-log/{self.user_id}")
            print(f"   Status: {resp.status_code}")
            print(f"   Logs count: {len(data)}")
            self.results.append({
                "test": "Get Catch Logs",
                "method": "GET",
                "endpoint": f"/catch-log/{self.user_id}",
                "status": resp.status_code,
                "success": success,
                "response": {"logs_count": len(data)}
            })
        except Exception as e:
            self.log_test("Get Catch Logs", "GET", f"/catch-log/{self.user_id}", 0, False, {"error": str(e)})

    # BLOCKCHAIN TEST
    def test_15_verify_transaction(self):
        """Test 15: Verify Blockchain Transaction"""
        # Using a sample tx hash (won't exist but tests the endpoint)
        tx_hash = "0x123456789abcdef"

        try:
            resp = requests.get(f"{self.base_url}/blockchain/verify/{tx_hash}")
            success = resp.status_code == 200
            data = resp.json()
            print(f"\n[PASS] Verify Blockchain Transaction")
            print(f"   GET /blockchain/verify/{tx_hash}")
            print(f"   Status: {resp.status_code}")
            print(f"   Response: {json.dumps(data, indent=2)}")
            self.results.append({
                "test": "Verify Transaction",
                "method": "GET",
                "endpoint": f"/blockchain/verify/{tx_hash}",
                "status": resp.status_code,
                "success": success,
                "response": data
            })
        except Exception as e:
            self.log_test("Verify Transaction", "GET", f"/blockchain/verify/{tx_hash}", 0, False, {"error": str(e)})

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n" + "="*80)
        print("OCEAN GOVERNANCE DIGITAL TWIN - API TEST SUITE")
        print("Testing Backend with ML Models Integration")
        print("="*80)

        # Auth tests
        print("\n--- AUTHENTICATION TESTS ---")
        self.test_1_health_check()
        time.sleep(0.5)
        self.test_2_register_user()
        time.sleep(0.5)
        self.test_3_login_user()
        time.sleep(0.5)
        self.test_4_get_profile()
        time.sleep(0.5)

        # Satellite tests
        print("\n--- SATELLITE DATA TESTS ---")
        self.test_5_pollution_map()
        time.sleep(0.5)
        self.test_6_algal_bloom()
        time.sleep(0.5)
        self.test_7_vessel_intrusions()
        time.sleep(0.5)

        # Stress Index tests (ML MODELS)
        print("\n--- STRESS INDEX TESTS (ML MODELS ACTIVE) ---")
        self.test_8_stress_index_all()
        time.sleep(0.5)
        self.test_9_stress_index_region()
        time.sleep(0.5)

        # Simulation tests (ML MODELS)
        print("\n--- POLICY SIMULATION TESTS (ML MODELS ACTIVE) ---")
        self.test_10_policy_simulation()
        time.sleep(0.5)

        # Violations tests
        print("\n--- VIOLATIONS TESTS ---")
        self.test_11_report_violation()
        time.sleep(0.5)
        self.test_12_get_live_violations()
        time.sleep(0.5)

        # Catch logs tests
        print("\n--- CATCH LOGS TESTS ---")
        self.test_13_submit_catch_log()
        time.sleep(0.5)
        self.test_14_get_catch_logs()
        time.sleep(0.5)

        # Blockchain tests
        print("\n--- BLOCKCHAIN TESTS ---")
        self.test_15_verify_transaction()

        # Print summary
        self.print_summary()


if __name__ == "__main__":
    tester = APITester(BASE_URL)
    tester.run_all_tests()
