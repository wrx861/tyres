#!/usr/bin/env python3
"""
Backend API Testing for New Admin Functions
Tests: Hide Order, Reset Activity Logs, Reset Statistics
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://izuchi-nash.preview.emergentagent.com/api"
ADMIN_TELEGRAM_ID = "508352361"

class AdminFunctionsTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.results = []
        
    def log_result(self, test_name, success, details, critical=True):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'critical': critical
        })
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_health_check(self):
        """Test basic health check"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_result("Health Check", True, "API is healthy and database connected")
                    return True
                else:
                    self.log_result("Health Check", False, f"Unhealthy status: {data}")
                    return False
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_hide_order_functionality(self):
        """Test hiding completed orders from admin panel"""
        try:
            # Step 1: Get all orders
            print("   Step 1: Getting all orders...")
            response = self.session.get(
                f"{BACKEND_URL}/orders/admin/all",
                params={'telegram_id': ADMIN_TELEGRAM_ID}
            )
            
            if response.status_code != 200:
                self.log_result("Hide Order - Get All Orders", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
            
            all_orders = response.json()
            initial_count = len(all_orders)
            print(f"   Found {initial_count} orders initially")
            
            # Step 2: Find or create a completed order
            completed_order = None
            for order in all_orders:
                if order.get('status') == 'completed':
                    completed_order = order
                    break
            
            if not completed_order:
                print("   No completed order found. Creating test order and marking as completed...")
                
                # Create test user
                test_user_id = f"test_{int(datetime.now().timestamp())}"
                user_data = {
                    'telegram_id': test_user_id,
                    'username': 'test_hide_order',
                    'first_name': 'Test',
                    'last_name': 'HideOrder'
                }
                self.session.post(f"{BACKEND_URL}/auth/telegram", json=user_data)
                
                # Create test order
                order_data = {
                    'items': [
                        {
                            'code': 'TEST_HIDE_123',
                            'name': 'Test Tire for Hide 185/60R15',
                            'brand': 'TestBrand',
                            'quantity': 4,
                            'price_base': 5000.0,
                            'price_final': 5750.0,
                            'warehouse_id': 1,
                            'warehouse_name': 'Test Warehouse'
                        }
                    ],
                    'delivery_address': {
                        'city': 'Москва',
                        'street': 'Тестовая',
                        'house': '1',
                        'apartment': '1',
                        'phone': '+79991234567',
                        'name': 'Тест Тестов'
                    }
                }
                
                create_response = self.session.post(
                    f"{BACKEND_URL}/orders",
                    params={'telegram_id': test_user_id},
                    json=order_data
                )
                
                if create_response.status_code != 200:
                    self.log_result("Hide Order - Create Test Order", False,
                                  f"Failed to create test order: {create_response.text}")
                    return False
                
                created_order = create_response.json()
                order_id = created_order.get('order_id')
                print(f"   Created test order: {order_id}")
                
                # First confirm the order
                confirm_data = {
                    'admin_comment': 'Test order for hide functionality'
                }
                confirm_response = self.session.post(
                    f"{BACKEND_URL}/orders/{order_id}/confirm",
                    params={'telegram_id': ADMIN_TELEGRAM_ID},
                    json=confirm_data
                )
                
                if confirm_response.status_code != 200:
                    self.log_result("Hide Order - Confirm Order", False,
                                  f"Failed to confirm order: {confirm_response.text}")
                    return False
                
                print(f"   Confirmed order {order_id}")
                
                # Then change status to completed
                status_response = self.session.patch(
                    f"{BACKEND_URL}/orders/{order_id}/status",
                    params={
                        'telegram_id': ADMIN_TELEGRAM_ID,
                        'new_status': 'completed'
                    }
                )
                
                if status_response.status_code != 200:
                    self.log_result("Hide Order - Mark as Completed", False,
                                  f"Failed to mark order as completed: {status_response.text}")
                    return False
                
                completed_order = status_response.json()
                print(f"   Marked order {order_id} as completed")
            
            order_id = completed_order.get('order_id')
            print(f"   Using completed order: {order_id}")
            
            # Step 3: Hide the order
            print(f"   Step 3: Hiding order {order_id}...")
            hide_response = self.session.delete(
                f"{BACKEND_URL}/orders/{order_id}/hide",
                params={'telegram_id': ADMIN_TELEGRAM_ID}
            )
            
            if hide_response.status_code != 200:
                self.log_result("Hide Order - Hide Request", False,
                              f"HTTP {hide_response.status_code}: {hide_response.text}")
                return False
            
            hide_result = hide_response.json()
            if not hide_result.get('success'):
                self.log_result("Hide Order - Hide Request", False,
                              f"Hide request returned success=false: {hide_result}")
                return False
            
            print(f"   Order {order_id} hidden successfully")
            
            # Step 4: Verify order is hidden from admin panel
            print("   Step 4: Verifying order is hidden from admin panel...")
            verify_response = self.session.get(
                f"{BACKEND_URL}/orders/admin/all",
                params={'telegram_id': ADMIN_TELEGRAM_ID}
            )
            
            if verify_response.status_code != 200:
                self.log_result("Hide Order - Verify Hidden", False,
                              f"Failed to get orders after hiding: {verify_response.text}")
                return False
            
            orders_after_hide = verify_response.json()
            final_count = len(orders_after_hide)
            
            # Check that the order is not in the list
            order_still_visible = any(o.get('order_id') == order_id for o in orders_after_hide)
            
            if order_still_visible:
                self.log_result("Hide Order - Verify Hidden", False,
                              f"Order {order_id} is still visible in admin panel after hiding")
                return False
            
            print(f"   Orders count: {initial_count} → {final_count}")
            print(f"   Order {order_id} successfully hidden from admin panel")
            
            self.log_result("Hide Order Functionality", True,
                          f"✅ Order {order_id} successfully hidden from admin panel. "
                          f"Orders visible: {initial_count} → {final_count}")
            return True
            
        except Exception as e:
            self.log_result("Hide Order Functionality", False, f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_reset_activity_logs(self):
        """Test resetting activity logs"""
        try:
            # Step 1: Check current activity logs
            print("   Step 1: Checking current activity logs...")
            response = self.session.get(
                f"{BACKEND_URL}/admin/activity",
                params={'telegram_id': ADMIN_TELEGRAM_ID}
            )
            
            if response.status_code != 200:
                self.log_result("Reset Activity - Get Current Logs", False,
                              f"HTTP {response.status_code}: {response.text}")
                return False
            
            activity_data = response.json()
            if not activity_data.get('success'):
                self.log_result("Reset Activity - Get Current Logs", False,
                              f"Failed to get activity logs: {activity_data}")
                return False
            
            initial_logs = activity_data.get('logs', [])
            initial_count = activity_data.get('total', 0)
            print(f"   Found {initial_count} activity logs")
            
            # Step 2: Reset activity logs
            print("   Step 2: Resetting activity logs...")
            reset_response = self.session.delete(
                f"{BACKEND_URL}/admin/activity/reset",
                params={'telegram_id': ADMIN_TELEGRAM_ID}
            )
            
            if reset_response.status_code != 200:
                self.log_result("Reset Activity - Reset Request", False,
                              f"HTTP {reset_response.status_code}: {reset_response.text}")
                return False
            
            reset_result = reset_response.json()
            if not reset_result.get('success'):
                self.log_result("Reset Activity - Reset Request", False,
                              f"Reset returned success=false: {reset_result}")
                return False
            
            deleted_count = reset_result.get('deleted_count', 0)
            print(f"   Deleted {deleted_count} activity logs")
            
            # Step 3: Verify logs are deleted
            print("   Step 3: Verifying logs are deleted...")
            verify_response = self.session.get(
                f"{BACKEND_URL}/admin/activity",
                params={'telegram_id': ADMIN_TELEGRAM_ID}
            )
            
            if verify_response.status_code != 200:
                self.log_result("Reset Activity - Verify Deleted", False,
                              f"Failed to verify deletion: {verify_response.text}")
                return False
            
            verify_data = verify_response.json()
            final_count = verify_data.get('total', 0)
            
            if final_count != 0:
                self.log_result("Reset Activity - Verify Deleted", False,
                              f"Activity logs not fully deleted. Expected 0, got {final_count}")
                return False
            
            print(f"   Activity logs count: {initial_count} → {final_count}")
            
            self.log_result("Reset Activity Logs", True,
                          f"✅ Activity logs successfully reset. Deleted {deleted_count} logs. "
                          f"Count: {initial_count} → {final_count}")
            return True
            
        except Exception as e:
            self.log_result("Reset Activity Logs", False, f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_reset_statistics_endpoint_exists(self):
        """Test that reset statistics endpoint exists and requires admin (DO NOT CALL IT)"""
        try:
            # Step 1: Get current statistics
            print("   Step 1: Getting current statistics...")
            response = self.session.get(
                f"{BACKEND_URL}/admin/stats",
                params={'telegram_id': ADMIN_TELEGRAM_ID}
            )
            
            if response.status_code != 200:
                self.log_result("Reset Stats - Get Current Stats", False,
                              f"HTTP {response.status_code}: {response.text}")
                return False
            
            stats_data = response.json()
            if not stats_data.get('success'):
                self.log_result("Reset Stats - Get Current Stats", False,
                              f"Failed to get stats: {stats_data}")
                return False
            
            stats = stats_data.get('stats', {})
            print(f"   Current stats: {stats}")
            
            # Step 2: Test that endpoint requires admin (use non-admin ID)
            print("   Step 2: Testing that reset endpoint requires admin...")
            non_admin_id = "999999999"
            
            # Try to call reset with non-admin ID (should fail with 403)
            reset_response = self.session.delete(
                f"{BACKEND_URL}/admin/stats/reset",
                params={'telegram_id': non_admin_id}
            )
            
            if reset_response.status_code == 403:
                print("   ✅ Endpoint correctly rejects non-admin users (403)")
                self.log_result("Reset Statistics Endpoint", True,
                              f"✅ Reset statistics endpoint exists and correctly requires admin access. "
                              f"Non-admin request returned 403 as expected. "
                              f"Current stats: {stats.get('total_orders', 0)} orders, "
                              f"{stats.get('total_users', 0)} users")
                return True
            elif reset_response.status_code == 200:
                # This should not happen with non-admin ID
                self.log_result("Reset Statistics Endpoint", False,
                              "Endpoint allowed non-admin to reset statistics (security issue)")
                return False
            else:
                self.log_result("Reset Statistics Endpoint", False,
                              f"Unexpected response for non-admin: HTTP {reset_response.status_code}")
                return False
            
        except Exception as e:
            self.log_result("Reset Statistics Endpoint", False, f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("BACKEND API TESTING - New Admin Functions")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Telegram ID: {ADMIN_TELEGRAM_ID}")
        print(f"Test started at: {datetime.now()}")
        print("=" * 60)
        print()
        
        # Run tests in order
        tests = [
            ("Health Check", self.test_health_check),
            ("Hide Order Functionality", self.test_hide_order_functionality),
            ("Reset Activity Logs", self.test_reset_activity_logs),
            ("Reset Statistics Endpoint", self.test_reset_statistics_endpoint_exists),
        ]
        
        for test_name, test_func in tests:
            print(f"Running: {test_name}")
            print("-" * 40)
            test_func()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        critical_failures = sum(1 for r in self.results if not r['success'] and r['critical'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Critical Failures: {critical_failures}")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    status = "CRITICAL" if result['critical'] else "MINOR"
                    print(f"  [{status}] {result['test']}: {result['details']}")
            print()
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if critical_failures == 0:
            print("✅ All critical functionality is working!")
        else:
            print(f"❌ {critical_failures} critical issues found!")
        
        return critical_failures == 0

if __name__ == "__main__":
    tester = AdminFunctionsTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
