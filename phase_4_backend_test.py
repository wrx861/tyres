#!/usr/bin/env python3
"""
Backend API Testing for Phase 4 Features - 4tochki Telegram Mini App
Tests: User database, persistent cart, user management, blocking middleware, activity tracking
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://izuchi-nash.preview.emergentagent.com/api"
ADMIN_TELEGRAM_ID = "508352361"
TEST_USER_1 = "999888777"
TEST_USER_1_USERNAME = "test_user"
TEST_USER_1_FIRSTNAME = "Иван"
TEST_USER_2 = "111222333"
TEST_USER_2_USERNAME = "test_user2"
TEST_USER_2_FIRSTNAME = "Петр"

class Phase4Tester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.results = []
        self.critical_failures = []
        
    def log_result(self, test_name, success, details, critical=True):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'critical': critical
        })
        
        if not success and critical:
            self.critical_failures.append({
                'test': test_name,
                'details': details
            })
        
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        print()
        
    def test_1_user_database_with_fields(self):
        """Test 1: База данных пользователей с полями is_blocked и last_activity"""
        print("\n" + "="*60)
        print("TEST 1: База данных пользователей")
        print("="*60)
        
        try:
            # Create new user
            user_data = {
                'telegram_id': TEST_USER_1,
                'username': TEST_USER_1_USERNAME,
                'first_name': TEST_USER_1_FIRSTNAME,
                'last_name': 'Тестовый'
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/telegram", json=user_data)
            
            if response.status_code != 200:
                self.log_result("1a. Create User", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            user = response.json()
            
            # Check that is_blocked field exists and is False
            if 'is_blocked' not in user:
                self.log_result("1a. Create User - is_blocked field", False, "Field 'is_blocked' missing in response")
                return False
            
            if user['is_blocked'] != False:
                self.log_result("1a. Create User - is_blocked value", False, f"Expected is_blocked=False, got {user['is_blocked']}")
                return False
            
            # Check that last_activity field exists (can be null)
            if 'last_activity' not in user:
                self.log_result("1a. Create User - last_activity field", False, "Field 'last_activity' missing in response")
                return False
            
            self.log_result("1a. Create User", True, f"User {TEST_USER_1} created with is_blocked=False, last_activity={user['last_activity']}")
            
            # Get user info to verify fields are persisted
            response = self.session.get(f"{BACKEND_URL}/auth/me", params={'telegram_id': TEST_USER_1})
            
            if response.status_code != 200:
                self.log_result("1b. Get User Info", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            user_info = response.json()
            
            if user_info.get('is_blocked') != False:
                self.log_result("1b. Get User Info - is_blocked", False, f"Expected is_blocked=False, got {user_info.get('is_blocked')}")
                return False
            
            if 'last_activity' not in user_info:
                self.log_result("1b. Get User Info - last_activity", False, "Field 'last_activity' missing")
                return False
            
            self.log_result("1b. Get User Info", True, f"User fields verified: is_blocked={user_info['is_blocked']}, last_activity={user_info['last_activity']}")
            
            return True
            
        except Exception as e:
            self.log_result("1. User Database", False, f"Error: {str(e)}")
            return False
    
    def test_2_persistent_cart_crud(self):
        """Test 2: Постоянная корзина - полный CRUD цикл"""
        print("\n" + "="*60)
        print("TEST 2: Постоянная корзина (CRUD)")
        print("="*60)
        
        try:
            # 2a. GET empty cart
            response = self.session.get(f"{BACKEND_URL}/cart/{TEST_USER_1}")
            
            if response.status_code != 200:
                self.log_result("2a. Get Empty Cart", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            cart = response.json()
            
            if not isinstance(cart.get('items'), list):
                self.log_result("2a. Get Empty Cart", False, f"Expected items to be a list, got {type(cart.get('items'))}")
                return False
            
            self.log_result("2a. Get Empty Cart", True, f"Empty cart returned with {len(cart['items'])} items")
            
            # 2b. POST - Add item to cart
            item_data = {
                "code": "TEST123",
                "name": "185/60R15",
                "brand": "Nokian",
                "model": "Hakkapeliitta",
                "quantity": 2,
                "price": 5000,
                "warehouse_id": 42,
                "warehouse_name": "Склад 42",
                "rest": 10,
                "width": 185,
                "height": 60,
                "diameter": 15,
                "season": "winter"
            }
            
            response = self.session.post(f"{BACKEND_URL}/cart/{TEST_USER_1}/items", json=item_data)
            
            if response.status_code != 200:
                self.log_result("2b. Add Item to Cart", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            add_result = response.json()
            
            if add_result.get('cart_items_count') != 1:
                self.log_result("2b. Add Item to Cart", False, f"Expected 1 item in cart, got {add_result.get('cart_items_count')}")
                return False
            
            self.log_result("2b. Add Item to Cart", True, f"Item TEST123 added, cart has {add_result['cart_items_count']} items")
            
            # 2c. GET cart with item
            response = self.session.get(f"{BACKEND_URL}/cart/{TEST_USER_1}")
            
            if response.status_code != 200:
                self.log_result("2c. Get Cart with Item", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            cart = response.json()
            
            if len(cart['items']) != 1:
                self.log_result("2c. Get Cart with Item", False, f"Expected 1 item, got {len(cart['items'])}")
                return False
            
            item = cart['items'][0]
            
            if item['code'] != 'TEST123' or item['quantity'] != 2:
                self.log_result("2c. Get Cart with Item", False, f"Item data mismatch: {item}")
                return False
            
            self.log_result("2c. Get Cart with Item", True, f"Cart contains TEST123 with quantity=2")
            
            # 2d. PUT - Update quantity
            response = self.session.put(
                f"{BACKEND_URL}/cart/{TEST_USER_1}/items/TEST123",
                params={'warehouse_id': 42},
                json={'quantity': 5}
            )
            
            if response.status_code != 200:
                self.log_result("2d. Update Item Quantity", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            self.log_result("2d. Update Item Quantity", True, "Quantity updated to 5")
            
            # 2e. GET cart to verify update
            response = self.session.get(f"{BACKEND_URL}/cart/{TEST_USER_1}")
            
            if response.status_code != 200:
                self.log_result("2e. Verify Updated Quantity", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            cart = response.json()
            
            if cart['items'][0]['quantity'] != 5:
                self.log_result("2e. Verify Updated Quantity", False, f"Expected quantity=5, got {cart['items'][0]['quantity']}")
                return False
            
            self.log_result("2e. Verify Updated Quantity", True, "Quantity correctly updated to 5")
            
            # 2f. DELETE - Remove item
            response = self.session.delete(
                f"{BACKEND_URL}/cart/{TEST_USER_1}/items/TEST123",
                params={'warehouse_id': 42}
            )
            
            if response.status_code != 200:
                self.log_result("2f. Delete Item", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            delete_result = response.json()
            
            if delete_result.get('cart_items_count') != 0:
                self.log_result("2f. Delete Item", False, f"Expected 0 items, got {delete_result.get('cart_items_count')}")
                return False
            
            self.log_result("2f. Delete Item", True, "Item deleted, cart is empty")
            
            # 2g. GET cart to verify deletion
            response = self.session.get(f"{BACKEND_URL}/cart/{TEST_USER_1}")
            
            if response.status_code != 200:
                self.log_result("2g. Verify Empty Cart", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            cart = response.json()
            
            if len(cart['items']) != 0:
                self.log_result("2g. Verify Empty Cart", False, f"Expected 0 items, got {len(cart['items'])}")
                return False
            
            self.log_result("2g. Verify Empty Cart", True, "Cart is empty after deletion")
            
            return True
            
        except Exception as e:
            self.log_result("2. Persistent Cart CRUD", False, f"Error: {str(e)}")
            return False
    
    def test_3_user_management_admin(self):
        """Test 3: Управление пользователями в админке"""
        print("\n" + "="*60)
        print("TEST 3: Управление пользователями")
        print("="*60)
        
        try:
            # 3a. GET list of users
            response = self.session.get(f"{BACKEND_URL}/admin/users", params={'telegram_id': ADMIN_TELEGRAM_ID})
            
            if response.status_code != 200:
                self.log_result("3a. Get Users List", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            users_data = response.json()
            
            if not users_data.get('success'):
                self.log_result("3a. Get Users List", False, f"API returned success=false: {users_data}")
                return False
            
            users = users_data.get('users', [])
            
            self.log_result("3a. Get Users List", True, f"Retrieved {len(users)} users, total: {users_data.get('total')}")
            
            # 3b. Block user
            response = self.session.post(
                f"{BACKEND_URL}/admin/users/{TEST_USER_1}/block",
                params={'telegram_id': ADMIN_TELEGRAM_ID}
            )
            
            if response.status_code != 200:
                self.log_result("3b. Block User", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            block_result = response.json()
            
            if not block_result.get('success'):
                self.log_result("3b. Block User", False, f"Block failed: {block_result}")
                return False
            
            self.log_result("3b. Block User", True, f"User {TEST_USER_1} blocked successfully")
            
            # 3c. Verify user is blocked
            response = self.session.get(f"{BACKEND_URL}/admin/users", params={'telegram_id': ADMIN_TELEGRAM_ID})
            
            if response.status_code != 200:
                self.log_result("3c. Verify User Blocked", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            users_data = response.json()
            users = users_data.get('users', [])
            
            blocked_user = next((u for u in users if u['telegram_id'] == TEST_USER_1), None)
            
            if not blocked_user:
                self.log_result("3c. Verify User Blocked", False, f"User {TEST_USER_1} not found in users list")
                return False
            
            if not blocked_user.get('is_blocked'):
                self.log_result("3c. Verify User Blocked", False, f"User is_blocked={blocked_user.get('is_blocked')}, expected True")
                return False
            
            self.log_result("3c. Verify User Blocked", True, f"User {TEST_USER_1} is_blocked=True")
            
            # 3d. Unblock user
            response = self.session.post(
                f"{BACKEND_URL}/admin/users/{TEST_USER_1}/unblock",
                params={'telegram_id': ADMIN_TELEGRAM_ID}
            )
            
            if response.status_code != 200:
                self.log_result("3d. Unblock User", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            unblock_result = response.json()
            
            if not unblock_result.get('success'):
                self.log_result("3d. Unblock User", False, f"Unblock failed: {unblock_result}")
                return False
            
            self.log_result("3d. Unblock User", True, f"User {TEST_USER_1} unblocked successfully")
            
            # 3e. Verify user is unblocked
            response = self.session.get(f"{BACKEND_URL}/admin/users", params={'telegram_id': ADMIN_TELEGRAM_ID})
            
            if response.status_code != 200:
                self.log_result("3e. Verify User Unblocked", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            users_data = response.json()
            users = users_data.get('users', [])
            
            unblocked_user = next((u for u in users if u['telegram_id'] == TEST_USER_1), None)
            
            if not unblocked_user:
                self.log_result("3e. Verify User Unblocked", False, f"User {TEST_USER_1} not found in users list")
                return False
            
            if unblocked_user.get('is_blocked'):
                self.log_result("3e. Verify User Unblocked", False, f"User is_blocked={unblocked_user.get('is_blocked')}, expected False")
                return False
            
            self.log_result("3e. Verify User Unblocked", True, f"User {TEST_USER_1} is_blocked=False")
            
            return True
            
        except Exception as e:
            self.log_result("3. User Management", False, f"Error: {str(e)}")
            return False
    
    def test_4_blocking_middleware(self):
        """Test 4: Middleware блокировки пользователей"""
        print("\n" + "="*60)
        print("TEST 4: Middleware блокировки")
        print("="*60)
        
        try:
            # 4a. Block user
            response = self.session.post(
                f"{BACKEND_URL}/admin/users/{TEST_USER_1}/block",
                params={'telegram_id': ADMIN_TELEGRAM_ID}
            )
            
            if response.status_code != 200:
                self.log_result("4a. Block User for Middleware Test", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            self.log_result("4a. Block User for Middleware Test", True, f"User {TEST_USER_1} blocked")
            
            # 4b. Try to access cart API (should be blocked)
            response = self.session.get(
                f"{BACKEND_URL}/cart/{TEST_USER_1}",
                params={'telegram_id': TEST_USER_1}
            )
            
            if response.status_code != 403:
                self.log_result("4b. Blocked User Access Cart", False, f"Expected HTTP 403, got {response.status_code}")
                return False
            
            error_data = response.json()
            expected_message = "Слишком много запросов, подождите еще и вернитесь не скоро"
            
            if error_data.get('detail') != expected_message:
                self.log_result("4b. Blocked User Access Cart - Message", False, f"Expected message '{expected_message}', got '{error_data.get('detail')}'")
                return False
            
            self.log_result("4b. Blocked User Access Cart", True, f"HTTP 403 with correct message: '{expected_message}'")
            
            # 4c. Unblock user
            response = self.session.post(
                f"{BACKEND_URL}/admin/users/{TEST_USER_1}/unblock",
                params={'telegram_id': ADMIN_TELEGRAM_ID}
            )
            
            if response.status_code != 200:
                self.log_result("4c. Unblock User", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            self.log_result("4c. Unblock User", True, f"User {TEST_USER_1} unblocked")
            
            # 4d. Try to access cart API again (should work now)
            response = self.session.get(
                f"{BACKEND_URL}/cart/{TEST_USER_1}",
                params={'telegram_id': TEST_USER_1}
            )
            
            if response.status_code != 200:
                self.log_result("4d. Unblocked User Access Cart", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            cart = response.json()
            
            if 'items' not in cart:
                self.log_result("4d. Unblocked User Access Cart", False, f"Invalid cart response: {cart}")
                return False
            
            self.log_result("4d. Unblocked User Access Cart", True, "Unblocked user can access cart API")
            
            return True
            
        except Exception as e:
            self.log_result("4. Blocking Middleware", False, f"Error: {str(e)}")
            return False
    
    def test_5_activity_tracking(self):
        """Test 5: Отслеживание активности пользователей"""
        print("\n" + "="*60)
        print("TEST 5: Отслеживание активности")
        print("="*60)
        
        try:
            # 5a. Perform tire search (should log activity)
            response = self.session.get(
                f"{BACKEND_URL}/products/tires/search",
                params={
                    'width': 185,
                    'height': 60,
                    'diameter': 15,
                    'season': 'winter',
                    'telegram_id': TEST_USER_1
                }
            )
            
            if response.status_code != 200:
                self.log_result("5a. Tire Search for Activity", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            tire_data = response.json()
            tire_count = len(tire_data.get('data', []))
            
            self.log_result("5a. Tire Search for Activity", True, f"Tire search completed, found {tire_count} results")
            
            # 5b. Perform disk search (should log activity)
            response = self.session.get(
                f"{BACKEND_URL}/products/disks/search",
                params={
                    'diameter': 16,
                    'width': 7,
                    'telegram_id': TEST_USER_1
                }
            )
            
            if response.status_code != 200:
                self.log_result("5b. Disk Search for Activity", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            disk_data = response.json()
            disk_count = len(disk_data.get('data', []))
            
            self.log_result("5b. Disk Search for Activity", True, f"Disk search completed, found {disk_count} results")
            
            # 5c. Get activity logs
            response = self.session.get(
                f"{BACKEND_URL}/admin/activity",
                params={'telegram_id': ADMIN_TELEGRAM_ID}
            )
            
            if response.status_code != 200:
                self.log_result("5c. Get Activity Logs", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            activity_data = response.json()
            
            if not activity_data.get('success'):
                self.log_result("5c. Get Activity Logs", False, f"API returned success=false: {activity_data}")
                return False
            
            logs = activity_data.get('logs', [])
            
            self.log_result("5c. Get Activity Logs", True, f"Retrieved {len(logs)} activity logs")
            
            # 5d. Verify tire_search and disk_search logs exist
            tire_search_logs = [log for log in logs if log.get('activity_type') == 'tire_search' and log.get('telegram_id') == TEST_USER_1]
            disk_search_logs = [log for log in logs if log.get('activity_type') == 'disk_search' and log.get('telegram_id') == TEST_USER_1]
            
            if len(tire_search_logs) == 0:
                self.log_result("5d. Verify Tire Search Logs", False, "No tire_search logs found for test user")
                return False
            
            if len(disk_search_logs) == 0:
                self.log_result("5d. Verify Disk Search Logs", False, "No disk_search logs found for test user")
                return False
            
            # Check that logs have search_params and result_count
            tire_log = tire_search_logs[0]
            
            if 'search_params' not in tire_log:
                self.log_result("5d. Verify Tire Search Log Fields", False, "tire_search log missing search_params")
                return False
            
            if 'result_count' not in tire_log:
                self.log_result("5d. Verify Tire Search Log Fields", False, "tire_search log missing result_count")
                return False
            
            disk_log = disk_search_logs[0]
            
            if 'search_params' not in disk_log:
                self.log_result("5d. Verify Disk Search Log Fields", False, "disk_search log missing search_params")
                return False
            
            if 'result_count' not in disk_log:
                self.log_result("5d. Verify Disk Search Log Fields", False, "disk_search log missing result_count")
                return False
            
            self.log_result("5d. Verify Search Logs", True, f"Found tire_search and disk_search logs with search_params and result_count")
            
            return True
            
        except Exception as e:
            self.log_result("5. Activity Tracking", False, f"Error: {str(e)}")
            return False
    
    def test_6_cart_activity_logging(self):
        """Test 6: Логирование активности корзины"""
        print("\n" + "="*60)
        print("TEST 6: Логирование корзины")
        print("="*60)
        
        try:
            # Create second test user
            user_data = {
                'telegram_id': TEST_USER_2,
                'username': TEST_USER_2_USERNAME,
                'first_name': TEST_USER_2_FIRSTNAME,
                'last_name': 'Иванов'
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/telegram", json=user_data)
            
            if response.status_code != 200:
                self.log_result("6a. Create Test User 2", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            self.log_result("6a. Create Test User 2", True, f"User {TEST_USER_2} created")
            
            # 6b. Add item to cart (should log cart_add)
            item_data = {
                "code": "CART_TEST_456",
                "name": "195/65R15",
                "brand": "Michelin",
                "model": "X-Ice",
                "quantity": 4,
                "price": 6000,
                "warehouse_id": 50,
                "warehouse_name": "Склад 50",
                "rest": 20,
                "width": 195,
                "height": 65,
                "diameter": 15,
                "season": "winter"
            }
            
            response = self.session.post(f"{BACKEND_URL}/cart/{TEST_USER_2}/items", json=item_data)
            
            if response.status_code != 200:
                self.log_result("6b. Add Item to Cart", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            self.log_result("6b. Add Item to Cart", True, "Item CART_TEST_456 added to cart")
            
            # 6c. Remove item from cart (should log cart_remove)
            response = self.session.delete(
                f"{BACKEND_URL}/cart/{TEST_USER_2}/items/CART_TEST_456",
                params={'warehouse_id': 50}
            )
            
            if response.status_code != 200:
                self.log_result("6c. Remove Item from Cart", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            self.log_result("6c. Remove Item from Cart", True, "Item CART_TEST_456 removed from cart")
            
            # 6d. Get activity logs and verify cart_add and cart_remove
            response = self.session.get(
                f"{BACKEND_URL}/admin/activity",
                params={'telegram_id': ADMIN_TELEGRAM_ID}
            )
            
            if response.status_code != 200:
                self.log_result("6d. Get Activity Logs", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            activity_data = response.json()
            logs = activity_data.get('logs', [])
            
            cart_add_logs = [log for log in logs if log.get('activity_type') == 'cart_add' and log.get('telegram_id') == TEST_USER_2]
            cart_remove_logs = [log for log in logs if log.get('activity_type') == 'cart_remove' and log.get('telegram_id') == TEST_USER_2]
            
            if len(cart_add_logs) == 0:
                self.log_result("6d. Verify Cart Add Logs", False, "No cart_add logs found for test user 2")
                return False
            
            if len(cart_remove_logs) == 0:
                self.log_result("6d. Verify Cart Remove Logs", False, "No cart_remove logs found for test user 2")
                return False
            
            self.log_result("6d. Verify Cart Logs", True, f"Found cart_add and cart_remove logs for user {TEST_USER_2}")
            
            return True
            
        except Exception as e:
            self.log_result("6. Cart Activity Logging", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Phase 4 tests"""
        print("=" * 80)
        print("PHASE 4 BACKEND TESTING - 4tochki Telegram Mini App")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Telegram ID: {ADMIN_TELEGRAM_ID}")
        print(f"Test User 1: {TEST_USER_1} (@{TEST_USER_1_USERNAME})")
        print(f"Test User 2: {TEST_USER_2} (@{TEST_USER_2_USERNAME})")
        print(f"Test started at: {datetime.now()}")
        print("=" * 80)
        
        # Run tests in order
        tests = [
            ("Test 1: User Database with Fields", self.test_1_user_database_with_fields),
            ("Test 2: Persistent Cart CRUD", self.test_2_persistent_cart_crud),
            ("Test 3: User Management Admin", self.test_3_user_management_admin),
            ("Test 4: Blocking Middleware", self.test_4_blocking_middleware),
            ("Test 5: Activity Tracking", self.test_5_activity_tracking),
            ("Test 6: Cart Activity Logging", self.test_6_cart_activity_logging),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"\n❌ EXCEPTION in {test_name}: {str(e)}\n")
                self.critical_failures.append({
                    'test': test_name,
                    'details': f"Exception: {str(e)}"
                })
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Critical Failures: {len(self.critical_failures)}")
        print()
        
        if len(self.critical_failures) > 0:
            print("=" * 80)
            print("CRITICAL FAILURES:")
            print("=" * 80)
            for failure in self.critical_failures:
                print(f"\n❌ {failure['test']}")
                print(f"   {failure['details']}")
            print()
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if len(self.critical_failures) == 0:
            print("\n✅ ALL CRITICAL TESTS PASSED!")
            print("🚀 Phase 4 features are working correctly!")
        else:
            print(f"\n❌ {len(self.critical_failures)} CRITICAL ISSUES FOUND!")
            print("⚠️  Phase 4 features need attention!")
        
        return len(self.critical_failures) == 0

if __name__ == "__main__":
    tester = Phase4Tester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
