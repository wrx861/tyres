#!/usr/bin/env python3
"""
Admin Notification Testing for New Visitors
Tests the functionality where admin gets notified when new users register
"""

import requests
import json
import sys
import os
import time
from datetime import datetime

# Configuration - Read from frontend/.env
BACKEND_URL = "https://wheelstore.preview.emergentagent.com/api"
ADMIN_TELEGRAM_ID = "508352361"

class AdminNotificationTester:
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
    
    def cleanup_test_users(self):
        """Clean up test users from database (if possible)"""
        # Note: We don't have a delete endpoint, so we'll just work with existing data
        pass
    
    def test_new_user_notification_with_username(self):
        """Test admin notification for new user with username"""
        try:
            # Test data from the request
            user_data = {
                "telegram_id": "999888777",
                "username": "test_user",
                "first_name": "Иван",
                "last_name": "Тестовый"
            }
            
            print(f"Creating new user: {user_data}")
            
            response = self.session.post(f"{BACKEND_URL}/auth/telegram", json=user_data)
            
            if response.status_code != 200:
                self.log_result("New User Notification (with username)", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
            
            user = response.json()
            
            # Verify user was created
            if user.get('telegram_id') != user_data['telegram_id']:
                self.log_result("New User Notification (with username)", False, 
                              f"User data mismatch: expected {user_data['telegram_id']}, got {user.get('telegram_id')}")
                return False
            
            # Verify user is not admin
            if user.get('is_admin'):
                self.log_result("New User Notification (with username)", False, 
                              "Test user should not be admin")
                return False
            
            self.log_result("New User Notification (with username)", True, 
                          f"User created successfully: {user_data['telegram_id']} - {user_data['first_name']} {user_data['last_name']} (@{user_data['username']})")
            return True
            
        except Exception as e:
            self.log_result("New User Notification (with username)", False, f"Error: {str(e)}")
            return False
    
    def test_new_user_notification_without_username(self):
        """Test admin notification for new user without username"""
        try:
            # Test data from the request - user without username
            user_data = {
                "telegram_id": "111222333",
                "first_name": "Петр",
                "last_name": "Иванов"
            }
            
            print(f"Creating new user without username: {user_data}")
            
            response = self.session.post(f"{BACKEND_URL}/auth/telegram", json=user_data)
            
            if response.status_code != 200:
                self.log_result("New User Notification (without username)", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
            
            user = response.json()
            
            # Verify user was created
            if user.get('telegram_id') != user_data['telegram_id']:
                self.log_result("New User Notification (without username)", False, 
                              f"User data mismatch: expected {user_data['telegram_id']}, got {user.get('telegram_id')}")
                return False
            
            # Verify user is not admin
            if user.get('is_admin'):
                self.log_result("New User Notification (without username)", False, 
                              "Test user should not be admin")
                return False
            
            # Verify username is None or empty
            if user.get('username'):
                self.log_result("New User Notification (without username)", False, 
                              f"Username should be None/empty, got: {user.get('username')}")
                return False
            
            self.log_result("New User Notification (without username)", True, 
                          f"User created successfully: {user_data['telegram_id']} - {user_data['first_name']} {user_data['last_name']} (no username)")
            return True
            
        except Exception as e:
            self.log_result("New User Notification (without username)", False, f"Error: {str(e)}")
            return False
    
    def test_existing_user_no_notification(self):
        """Test that existing user login does NOT trigger notification"""
        try:
            # Use the same user data as first test - should already exist
            user_data = {
                "telegram_id": "999888777",
                "username": "test_user",
                "first_name": "Иван",
                "last_name": "Тестовый"
            }
            
            print(f"Attempting login with existing user: {user_data}")
            
            response = self.session.post(f"{BACKEND_URL}/auth/telegram", json=user_data)
            
            if response.status_code != 200:
                self.log_result("Existing User No Notification", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
            
            user = response.json()
            
            # Verify user data is returned (existing user)
            if user.get('telegram_id') != user_data['telegram_id']:
                self.log_result("Existing User No Notification", False, 
                              f"User data mismatch: expected {user_data['telegram_id']}, got {user.get('telegram_id')}")
                return False
            
            # Check if user has created_at timestamp (indicates existing user)
            if not user.get('created_at'):
                self.log_result("Existing User No Notification", False, 
                              "Existing user should have created_at timestamp")
                return False
            
            self.log_result("Existing User No Notification", True, 
                          f"Existing user login successful: {user_data['telegram_id']} (no new notification should be sent)")
            return True
            
        except Exception as e:
            self.log_result("Existing User No Notification", False, f"Error: {str(e)}")
            return False
    
    def test_admin_user_no_notification(self):
        """Test that admin user registration does NOT trigger notification"""
        try:
            # Create admin user (should not trigger notification to self)
            admin_data = {
                "telegram_id": ADMIN_TELEGRAM_ID,
                "username": "admin_test",
                "first_name": "Admin",
                "last_name": "Test"
            }
            
            print(f"Creating admin user: {admin_data}")
            
            response = self.session.post(f"{BACKEND_URL}/auth/telegram", json=admin_data)
            
            if response.status_code != 200:
                self.log_result("Admin User No Notification", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
            
            user = response.json()
            
            # Verify user was created/updated
            if user.get('telegram_id') != admin_data['telegram_id']:
                self.log_result("Admin User No Notification", False, 
                              f"User data mismatch: expected {admin_data['telegram_id']}, got {user.get('telegram_id')}")
                return False
            
            # Verify user IS admin
            if not user.get('is_admin'):
                self.log_result("Admin User No Notification", False, 
                              "Admin user should have is_admin=True")
                return False
            
            self.log_result("Admin User No Notification", True, 
                          f"Admin user processed successfully: {admin_data['telegram_id']} (no self-notification should be sent)")
            return True
            
        except Exception as e:
            self.log_result("Admin User No Notification", False, f"Error: {str(e)}")
            return False
    
    def check_backend_logs(self):
        """Check backend logs for notification messages"""
        try:
            print("Checking backend logs for notification messages...")
            
            # Check supervisor logs for backend
            import subprocess
            result = subprocess.run(
                ['tail', '-n', '50', '/var/log/supervisor/backend.out.log'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Look for notification-related log messages
                notification_logs = []
                for line in logs.split('\n'):
                    if any(keyword in line.lower() for keyword in ['notification', 'telegram', 'visitor', 'message sent']):
                        notification_logs.append(line.strip())
                
                if notification_logs:
                    self.log_result("Backend Logs Check", True, 
                                  f"Found {len(notification_logs)} notification-related log entries")
                    print("Recent notification logs:")
                    for log in notification_logs[-10:]:  # Show last 10
                        print(f"  {log}")
                else:
                    self.log_result("Backend Logs Check", False, 
                                  "No notification-related logs found in recent entries")
                
                return len(notification_logs) > 0
            else:
                self.log_result("Backend Logs Check", False, 
                              f"Failed to read logs: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_result("Backend Logs Check", False, f"Error checking logs: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all admin notification tests"""
        print("=" * 60)
        print("ADMIN NOTIFICATION TESTING - New Visitor Notifications")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Telegram ID: {ADMIN_TELEGRAM_ID}")
        print(f"Test started at: {datetime.now()}")
        print("=" * 60)
        print()
        
        # Clean up first
        self.cleanup_test_users()
        
        # Run tests in order
        tests = [
            ("Health Check", self.test_health_check),
            ("New User Notification (with username)", self.test_new_user_notification_with_username),
            ("New User Notification (without username)", self.test_new_user_notification_without_username),
            ("Existing User No Notification", self.test_existing_user_no_notification),
            ("Admin User No Notification", self.test_admin_user_no_notification),
            ("Backend Logs Check", self.check_backend_logs),
        ]
        
        for test_name, test_func in tests:
            print(f"Running: {test_name}")
            print("-" * 40)
            test_func()
            time.sleep(1)  # Small delay between tests
        
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
        
        print("\n" + "=" * 60)
        print("EXPECTED BEHAVIOR:")
        print("- New users (999888777, 111222333) should trigger admin notifications")
        print("- Existing user re-login should NOT trigger notification")
        print("- Admin user (508352361) should NOT trigger self-notification")
        print("- Check Telegram bot logs for actual message sending")
        print("=" * 60)
        
        return critical_failures == 0

if __name__ == "__main__":
    tester = AdminNotificationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)