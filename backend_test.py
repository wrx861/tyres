#!/usr/bin/env python3
"""
Backend API Testing for 4tochki Telegram Mini App
Tests real API integration (USE_MOCK_DATA=false)
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://wheelwhiz.preview.emergentagent.com/api"
ADMIN_TELEGRAM_ID = "508352361"
TEST_USER_TELEGRAM_ID = "123456789"  # Test user ID

class APITester:
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
    
    def test_tire_search(self):
        """Test tire search with real API data"""
        try:
            # Test with specific parameters
            params = {
                'width': 185,
                'height': 60,
                'diameter': 15,
                'season': 'winter'
            }
            
            response = self.session.get(f"{BACKEND_URL}/products/tires/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if using real API (not mock)
                if data.get('mock_mode') == True:
                    self.log_result("Tire Search - Real API", False, "Still using MOCK data instead of real API")
                    return False
                
                # Check if data is returned
                if not data.get('success'):
                    self.log_result("Tire Search - Real API", False, f"API returned success=false: {data}")
                    return False
                
                tires = data.get('data', [])
                markup = data.get('markup_percentage')
                
                if len(tires) == 0:
                    self.log_result("Tire Search - Real API", False, "No tires returned from real API")
                    return False
                
                # Check markup application
                markup_applied = False
                for tire in tires[:3]:  # Check first 3 items
                    if tire.get('price') and tire.get('price_original'):
                        original = float(tire['price_original'])
                        final = float(tire['price'])
                        expected = original * (1 + markup / 100)
                        if abs(final - expected) < 0.01:  # Allow small rounding differences
                            markup_applied = True
                            break
                
                if not markup_applied:
                    self.log_result("Tire Search - Markup", False, f"Markup {markup}% not properly applied to prices")
                else:
                    self.log_result("Tire Search - Markup", True, f"Markup {markup}% correctly applied")
                
                self.log_result("Tire Search - Real API", True, f"Found {len(tires)} tires, markup: {markup}%")
                return True
                
            else:
                self.log_result("Tire Search - Real API", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Tire Search - Real API", False, f"Error: {str(e)}")
            return False
    
    def test_disk_search(self):
        """Test disk search with real API data"""
        try:
            params = {
                'diameter': 15,
                'width': 6.5
            }
            
            response = self.session.get(f"{BACKEND_URL}/products/disks/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if using real API
                if data.get('mock_mode') == True:
                    self.log_result("Disk Search - Real API", False, "Still using MOCK data instead of real API")
                    return False
                
                if not data.get('success'):
                    self.log_result("Disk Search - Real API", False, f"API returned success=false: {data}")
                    return False
                
                disks = data.get('data', [])
                markup = data.get('markup_percentage')
                
                if len(disks) == 0:
                    self.log_result("Disk Search - Real API", False, "No disks returned from real API")
                    return False
                
                self.log_result("Disk Search - Real API", True, f"Found {len(disks)} disks, markup: {markup}%")
                return True
                
            else:
                self.log_result("Disk Search - Real API", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Disk Search - Real API", False, f"Error: {str(e)}")
            return False
    
    def test_car_selection_flow(self):
        """Test complete car selection flow"""
        try:
            # Step 1: Get car brands
            response = self.session.get(f"{BACKEND_URL}/cars/brands")
            if response.status_code != 200:
                self.log_result("Car Selection - Brands", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            brands_data = response.json()
            if brands_data.get('mock_mode') == True:
                self.log_result("Car Selection - Brands", False, "Still using MOCK data")
                return False
            
            brands = brands_data.get('data', [])
            if len(brands) == 0:
                self.log_result("Car Selection - Brands", False, "No brands returned")
                return False
            
            self.log_result("Car Selection - Brands", True, f"Found {len(brands)} brands")
            
            # Step 2: Get models for first brand
            first_brand = brands[0] if isinstance(brands[0], str) else brands[0].get('name', brands[0])
            response = self.session.get(f"{BACKEND_URL}/cars/models", params={'brand': first_brand})
            
            if response.status_code != 200:
                self.log_result("Car Selection - Models", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            models_data = response.json()
            if models_data.get('mock_mode') == True:
                self.log_result("Car Selection - Models", False, "Still using MOCK data")
                return False
            
            models = models_data.get('data', [])
            if len(models) == 0:
                self.log_result("Car Selection - Models", False, f"No models for brand {first_brand}")
                return False
            
            self.log_result("Car Selection - Models", True, f"Found {len(models)} models for {first_brand}")
            
            # Step 3: Get years
            first_model = models[0] if isinstance(models[0], str) else models[0].get('name', models[0])
            response = self.session.get(f"{BACKEND_URL}/cars/years", params={
                'brand': first_brand,
                'model': first_model
            })
            
            if response.status_code != 200:
                self.log_result("Car Selection - Years", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            years_data = response.json()
            if years_data.get('mock_mode') == True:
                self.log_result("Car Selection - Years", False, "Still using MOCK data")
                return False
            
            years = years_data.get('data', [])
            if len(years) == 0:
                self.log_result("Car Selection - Years", False, f"No years for {first_brand} {first_model}")
                return False
            
            self.log_result("Car Selection - Years", True, f"Found {len(years)} years")
            
            # Step 4: Get modifications
            first_year = years[0] if isinstance(years[0], str) else str(years[0])
            response = self.session.get(f"{BACKEND_URL}/cars/modifications", params={
                'brand': first_brand,
                'model': first_model,
                'year_begin': first_year,
                'year_end': first_year
            })
            
            if response.status_code != 200:
                self.log_result("Car Selection - Modifications", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            mods_data = response.json()
            if mods_data.get('mock_mode') == True:
                self.log_result("Car Selection - Modifications", False, "Still using MOCK data")
                return False
            
            modifications = mods_data.get('data', [])
            if len(modifications) == 0:
                self.log_result("Car Selection - Modifications", False, "No modifications found")
                return False
            
            self.log_result("Car Selection - Modifications", True, f"Found {len(modifications)} modifications")
            
            # Step 5: Get goods by car
            first_mod = modifications[0] if isinstance(modifications[0], str) else modifications[0].get('name', str(modifications[0]))
            response = self.session.get(f"{BACKEND_URL}/cars/goods", params={
                'brand': first_brand,
                'model': first_model,
                'year_begin': first_year,
                'year_end': first_year,
                'modification': first_mod,
                'product_type': 'tyre'
            })
            
            if response.status_code != 200:
                self.log_result("Car Selection - Goods", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            goods_data = response.json()
            if goods_data.get('mock_mode') == True:
                self.log_result("Car Selection - Goods", False, "Still using MOCK data")
                return False
            
            goods = goods_data.get('data', [])
            markup = goods_data.get('markup_percentage')
            
            self.log_result("Car Selection - Goods", True, f"Found {len(goods)} products, markup: {markup}%")
            return True
            
        except Exception as e:
            self.log_result("Car Selection Flow", False, f"Error: {str(e)}")
            return False
    
    def test_markup_management(self):
        """Test markup management for admin"""
        try:
            # First, create admin user
            self.create_test_admin()
            
            # Test getting current markup
            response = self.session.get(f"{BACKEND_URL}/admin/markup", params={
                'telegram_id': ADMIN_TELEGRAM_ID
            })
            
            if response.status_code != 200:
                self.log_result("Markup Management - Get", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            current_markup = response.json()
            original_markup = current_markup.get('markup_percentage', 15)
            
            self.log_result("Markup Management - Get", True, f"Current markup: {original_markup}%")
            
            # Test updating markup
            new_markup = 20.0
            response = self.session.put(f"{BACKEND_URL}/admin/markup", 
                params={'telegram_id': ADMIN_TELEGRAM_ID},
                json={'markup_percentage': new_markup}
            )
            
            if response.status_code != 200:
                self.log_result("Markup Management - Update", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            updated_markup = response.json()
            if updated_markup.get('markup_percentage') != new_markup:
                self.log_result("Markup Management - Update", False, f"Markup not updated correctly: {updated_markup}")
                return False
            
            self.log_result("Markup Management - Update", True, f"Markup updated to {new_markup}%")
            
            # Test that new markup is applied to products
            response = self.session.get(f"{BACKEND_URL}/products/tires/search", params={
                'width': 185, 'height': 60, 'diameter': 15
            })
            
            if response.status_code == 200:
                data = response.json()
                applied_markup = data.get('markup_percentage')
                if applied_markup == new_markup:
                    self.log_result("Markup Management - Applied", True, f"New markup {new_markup}% applied to products")
                else:
                    self.log_result("Markup Management - Applied", False, f"Expected {new_markup}%, got {applied_markup}%")
            
            # Restore original markup
            self.session.put(f"{BACKEND_URL}/admin/markup", 
                params={'telegram_id': ADMIN_TELEGRAM_ID},
                json={'markup_percentage': original_markup}
            )
            
            return True
            
        except Exception as e:
            self.log_result("Markup Management", False, f"Error: {str(e)}")
            return False
    
    def create_test_admin(self):
        """Create test admin user"""
        try:
            user_data = {
                'telegram_id': ADMIN_TELEGRAM_ID,
                'username': 'test_admin',
                'first_name': 'Test',
                'last_name': 'Admin'
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/telegram", json=user_data)
            return response.status_code == 200
        except:
            return False
    
    def create_test_user(self):
        """Create test user"""
        try:
            user_data = {
                'telegram_id': TEST_USER_TELEGRAM_ID,
                'username': 'test_user',
                'first_name': 'Test',
                'last_name': 'User'
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/telegram", json=user_data)
            return response.status_code == 200
        except:
            return False
    
    def test_authentication(self):
        """Test user authentication"""
        try:
            # Test creating new user
            user_data = {
                'telegram_id': TEST_USER_TELEGRAM_ID,
                'username': 'test_user_auth',
                'first_name': 'Test',
                'last_name': 'User'
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/telegram", json=user_data)
            
            if response.status_code != 200:
                self.log_result("Authentication - Create User", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            user = response.json()
            if user.get('telegram_id') != TEST_USER_TELEGRAM_ID:
                self.log_result("Authentication - Create User", False, f"Wrong user data: {user}")
                return False
            
            self.log_result("Authentication - Create User", True, f"User created: {user.get('username')}")
            
            # Test getting user info
            response = self.session.get(f"{BACKEND_URL}/auth/me", params={
                'telegram_id': TEST_USER_TELEGRAM_ID
            })
            
            if response.status_code != 200:
                self.log_result("Authentication - Get User", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            user_info = response.json()
            if user_info.get('telegram_id') != TEST_USER_TELEGRAM_ID:
                self.log_result("Authentication - Get User", False, f"Wrong user info: {user_info}")
                return False
            
            self.log_result("Authentication - Get User", True, "User info retrieved successfully")
            return True
            
        except Exception as e:
            self.log_result("Authentication", False, f"Error: {str(e)}")
            return False
    
    def test_orders(self):
        """Test order creation and management"""
        try:
            # Create test user first
            self.create_test_user()
            
            # Create test order
            order_data = {
                'items': [
                    {
                        'code': 'TEST123',
                        'brand': 'Michelin',
                        'model': 'X-Ice North 4',
                        'size': '185/60R15',
                        'price_original': 8500.0,
                        'price_final': 9775.0,  # With 15% markup
                        'quantity': 4,
                        'warehouse_id': 'MSK'
                    }
                ],
                'delivery_address': {
                    'city': 'Москва',
                    'street': 'Тестовая улица',
                    'house': '1',
                    'apartment': '1',
                    'phone': '+79991234567',
                    'name': 'Тест Тестов'
                }
            }
            
            response = self.session.post(f"{BACKEND_URL}/orders", 
                params={'telegram_id': TEST_USER_TELEGRAM_ID},
                json=order_data
            )
            
            if response.status_code != 200:
                self.log_result("Orders - Create", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            order = response.json()
            order_id = order.get('order_id')
            
            if not order_id:
                self.log_result("Orders - Create", False, f"No order_id in response: {order}")
                return False
            
            self.log_result("Orders - Create", True, f"Order created: {order_id}")
            
            # Test getting user orders
            response = self.session.get(f"{BACKEND_URL}/orders/my", params={
                'telegram_id': TEST_USER_TELEGRAM_ID
            })
            
            if response.status_code != 200:
                self.log_result("Orders - Get My Orders", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            orders = response.json()
            if not isinstance(orders, list) or len(orders) == 0:
                self.log_result("Orders - Get My Orders", False, f"No orders found: {orders}")
                return False
            
            self.log_result("Orders - Get My Orders", True, f"Found {len(orders)} orders")
            return True
            
        except Exception as e:
            self.log_result("Orders", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("BACKEND API TESTING - 4tochki Telegram Mini App")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Telegram ID: {ADMIN_TELEGRAM_ID}")
        print(f"Test started at: {datetime.now()}")
        print("=" * 60)
        print()
        
        # Run tests in order of priority
        tests = [
            ("Health Check", self.test_health_check),
            ("Tire Search (Real API)", self.test_tire_search),
            ("Disk Search (Real API)", self.test_disk_search),
            ("Car Selection Flow", self.test_car_selection_flow),
            ("Markup Management", self.test_markup_management),
            ("Authentication", self.test_authentication),
            ("Orders", self.test_orders),
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
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)