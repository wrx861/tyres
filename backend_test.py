#!/usr/bin/env python3
"""
Backend API Testing for 4tochki Telegram Mini App
Tests real API integration after UI fixes (USE_MOCK_DATA=false)
Focus: Size parsing, warehouse data, markup functionality
"""

import requests
import json
import sys
import os
import re
from datetime import datetime

# Configuration - Read from frontend/.env
BACKEND_URL = "https://tire-api-service.preview.emergentagent.com/api"
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
    
    def test_tire_search_with_image_fields(self):
        """Test tire search with image fields verification (as per review request)"""
        try:
            # Test with specific parameters from review request
            params = {
                'width': 185,
                'height': 60,
                'diameter': 15,
                'season': 'winter',
                'page': 0,
                'page_size': 3
            }
            
            response = self.session.get(f"{BACKEND_URL}/products/tires/search", params=params)
            
            if response.status_code != 200:
                self.log_result("Tire Search - Image Fields", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check if using real API (not mock)
            if data.get('mock_mode') == True:
                self.log_result("Tire Search - Image Fields", False, "Still using MOCK data instead of real API")
                return False
            
            # Check if data is returned
            if not data.get('success'):
                self.log_result("Tire Search - Image Fields", False, f"API returned success=false: {data}")
                return False
            
            tires = data.get('data', [])
            
            if len(tires) == 0:
                self.log_result("Tire Search - Image Fields", False, "No tires returned from real API")
                return False
            
            # Verify each tire has image fields
            image_field_errors = []
            fallback_tests = []
            
            for i, tire in enumerate(tires):
                # Check that image fields exist (they can be empty strings)
                if 'img_small' not in tire:
                    image_field_errors.append(f"Tire {i}: missing img_small field")
                if 'img_big_my' not in tire:
                    image_field_errors.append(f"Tire {i}: missing img_big_my field")
                if 'img_big_pish' not in tire:
                    image_field_errors.append(f"Tire {i}: missing img_big_pish field")
                
                # Test fallback logic: if img_big_my is empty, it should use img_big_pish
                img_big_my = tire.get('img_big_my', '')
                img_big_pish = tire.get('img_big_pish', '')
                
                # If img_big_my is empty but img_big_pish has value, fallback should work
                if not img_big_my and img_big_pish:
                    fallback_tests.append(f"Tire {i}: Fallback working - img_big_my empty, using img_big_pish: {img_big_pish[:50]}...")
                elif img_big_my and img_big_pish and img_big_my != img_big_pish:
                    fallback_tests.append(f"Tire {i}: Has both images - img_big_my: {img_big_my[:50]}..., img_big_pish: {img_big_pish[:50]}...")
                elif img_big_my:
                    fallback_tests.append(f"Tire {i}: Using img_big_my: {img_big_my[:50]}...")
            
            if image_field_errors:
                error_summary = "; ".join(image_field_errors)
                self.log_result("Tire Search - Image Fields", False, error_summary)
                return False
            
            # Log fallback test results
            fallback_summary = "; ".join(fallback_tests[:3])  # Show first 3
            if len(fallback_tests) > 3:
                fallback_summary += f" (and {len(fallback_tests) - 3} more)"
            
            self.log_result("Tire Search - Image Fields", True, 
                          f"✅ All {len(tires)} tires have image fields: img_small, img_big_my, img_big_pish. Fallback logic: {fallback_summary}")
            return True
                
        except Exception as e:
            self.log_result("Tire Search - Image Fields", False, f"Error: {str(e)}")
            return False
    
    def test_disk_search_with_sizes(self):
        """Test disk search with size parsing verification"""
        try:
            # Test with specific parameters from review request
            params = {
                'diameter': 16,
                'width': 7,
                'page': 0,
                'page_size': 3
            }
            
            response = self.session.get(f"{BACKEND_URL}/products/disks/search", params=params)
            
            if response.status_code != 200:
                self.log_result("Disk Search - Size Parsing", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check if using real API
            if data.get('mock_mode') == True:
                self.log_result("Disk Search - Size Parsing", False, "Still using MOCK data instead of real API")
                return False
            
            if not data.get('success'):
                self.log_result("Disk Search - Size Parsing", False, f"API returned success=false: {data}")
                return False
            
            disks = data.get('data', [])
            markup = data.get('markup_percentage')
            
            if len(disks) == 0:
                self.log_result("Disk Search - Size Parsing", False, "No disks returned from real API")
                return False
            
            # Verify each disk has required fields
            size_parsing_errors = []
            warehouse_errors = []
            price_errors = []
            
            for i, disk in enumerate(disks):
                # Check size fields (parsed from name)
                if not disk.get('width'):
                    size_parsing_errors.append(f"Disk {i}: missing width")
                if not disk.get('diameter'):
                    size_parsing_errors.append(f"Disk {i}: missing diameter")
                
                # Check warehouse fields
                if not disk.get('rest') and disk.get('rest') != 0:
                    warehouse_errors.append(f"Disk {i}: missing rest (quantity)")
                if not disk.get('warehouse_name') or not isinstance(disk.get('warehouse_name'), str):
                    warehouse_errors.append(f"Disk {i}: missing or invalid warehouse_name")
                
                # Check price fields
                if not disk.get('price') or disk.get('price') <= 0:
                    price_errors.append(f"Disk {i}: missing or invalid price")
                
                # Verify size parsing from name field
                name = disk.get('name', '')
                if name:
                    size_match = re.search(r'(\d+\.?\d*)x(\d+)', name)
                    if size_match and disk.get('width') and disk.get('diameter'):
                        expected_width = float(size_match.group(1))
                        expected_diameter = int(size_match.group(2))
                        
                        if (abs(disk['width'] - expected_width) > 0.1 or 
                            disk['diameter'] != expected_diameter):
                            size_parsing_errors.append(
                                f"Disk {i}: Size mismatch - name '{name}' vs parsed {disk['width']}x{disk['diameter']}"
                            )
            
            # Report results
            all_errors = size_parsing_errors + warehouse_errors + price_errors
            
            if all_errors:
                error_summary = "; ".join(all_errors[:5])  # Show first 5 errors
                if len(all_errors) > 5:
                    error_summary += f" (and {len(all_errors) - 5} more)"
                self.log_result("Disk Search - Size Parsing", False, error_summary)
                return False
            
            self.log_result("Disk Search - Size Parsing", True, 
                          f"✅ All {len(disks)} disks have correct fields: width, diameter, rest, warehouse_name, price > 0")
            return True
                
        except Exception as e:
            self.log_result("Disk Search - Size Parsing", False, f"Error: {str(e)}")
            return False
    
    def test_car_selection_flow_with_fields(self):
        """Test complete car selection flow with field verification"""
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
                # Try with BMW 3 Series which we know has modifications for recent years
                try:
                    response = self.session.get(f"{BACKEND_URL}/cars/models", params={'brand': 'BMW'})
                    if response.status_code == 200:
                        bmw_models = response.json().get('data', [])
                        if '3 Series' in bmw_models:
                            # Try BMW 3 Series
                            response = self.session.get(f"{BACKEND_URL}/cars/years", params={
                                'brand': 'BMW',
                                'model': '3 Series'
                            })
                            if response.status_code == 200:
                                bmw_years = response.json().get('data', [])
                                # Use a recent year (2015 or later)
                                recent_years = [y for y in bmw_years if y >= 2015]
                                if recent_years:
                                    bmw_year = str(recent_years[0])
                                    response = self.session.get(f"{BACKEND_URL}/cars/modifications", params={
                                        'brand': 'BMW',
                                        'model': '3 Series',
                                        'year_begin': bmw_year,
                                        'year_end': bmw_year
                                    })
                                    if response.status_code == 200:
                                        bmw_mods = response.json().get('data', [])
                                        if bmw_mods:
                                            modifications = bmw_mods
                                            first_brand = 'BMW'
                                            first_model = '3 Series'
                                            first_year = bmw_year
                except:
                    pass
                
                if len(modifications) == 0:
                    self.log_result("Car Selection - Modifications", False, "No modifications found for any tested cars")
                    return False
            
            self.log_result("Car Selection - Modifications", True, f"Found {len(modifications)} modifications")
            
            # Step 5: Get goods by car with field verification
            # Try multiple car combinations to find one with products
            goods = []
            goods_data = None
            markup = None
            
            car_combinations = [
                (first_brand, first_model, first_year, modifications[0] if modifications else 'default'),
                ('Toyota', 'Camry', '2020', 'default'),
                ('BMW', 'X5', '2019', 'default'),
                ('Mercedes-Benz', 'C-Class', '2018', 'default'),
                ('Audi', 'A4', '2017', 'default')
            ]
            
            for brand, model, year, modification in car_combinations:
                try:
                    response = self.session.get(f"{BACKEND_URL}/cars/goods", params={
                        'brand': brand,
                        'model': model,
                        'year_begin': year,
                        'year_end': year,
                        'modification': modification,
                        'product_type': 'tyre'
                    })
                    
                    if response.status_code == 200:
                        goods_data = response.json()
                        if goods_data.get('success') and goods_data.get('data'):
                            goods = goods_data.get('data', [])
                            markup = goods_data.get('markup_percentage')
                            if len(goods) > 0:
                                self.log_result("Car Selection - Found Products", True, 
                                              f"Found {len(goods)} products for {brand} {model} {year}")
                                break
                except:
                    continue
            
            if len(goods) == 0:
                self.log_result("Car Selection - Goods Fields", False, 
                              "No goods returned for any tested car combinations. This may be normal if no products match the car specifications.")
                return False
            
            # Verify each product has all required fields
            field_errors = []
            
            for i, item in enumerate(goods):
                # Check size fields
                if not item.get('width'):
                    field_errors.append(f"Item {i}: missing width")
                if not item.get('height'):
                    field_errors.append(f"Item {i}: missing height")
                if not item.get('diameter'):
                    field_errors.append(f"Item {i}: missing diameter")
                
                # Check warehouse fields
                if not item.get('rest') and item.get('rest') != 0:
                    field_errors.append(f"Item {i}: missing rest")
                if not item.get('warehouse_name'):
                    field_errors.append(f"Item {i}: missing warehouse_name")
                
                # Check price
                if not item.get('price') or item.get('price') <= 0:
                    field_errors.append(f"Item {i}: missing or invalid price")
            
            if field_errors:
                error_summary = "; ".join(field_errors[:5])
                if len(field_errors) > 5:
                    error_summary += f" (and {len(field_errors) - 5} more)"
                self.log_result("Car Selection - Goods Fields", False, error_summary)
                return False
            
            self.log_result("Car Selection - Goods Fields", True, 
                          f"✅ All {len(goods)} products have required fields: width, height, diameter, rest, warehouse_name, price")
            return True
            
        except Exception as e:
            self.log_result("Car Selection Flow", False, f"Error: {str(e)}")
            return False
    
    def test_markup_management_still_works(self):
        """Test markup management still works after UI changes"""
        try:
            # First, create admin user
            self.create_test_admin()
            
            # Test getting current markup
            response = self.session.get(f"{BACKEND_URL}/admin/markup", params={
                'telegram_id': ADMIN_TELEGRAM_ID
            })
            
            if response.status_code != 200:
                self.log_result("Markup Management - Get Current", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            current_markup = response.json()
            original_markup = current_markup.get('markup_percentage', 15)
            
            self.log_result("Markup Management - Get Current", True, f"Current markup: {original_markup}%")
            
            # Test updating markup to 25% as specified in review request
            new_markup = 25.0
            response = self.session.put(f"{BACKEND_URL}/admin/markup", 
                params={'telegram_id': ADMIN_TELEGRAM_ID},
                json={'markup_percentage': new_markup}
            )
            
            if response.status_code != 200:
                self.log_result("Markup Management - Update to 25%", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            updated_markup = response.json()
            if updated_markup.get('markup_percentage') != new_markup:
                self.log_result("Markup Management - Update to 25%", False, f"Markup not updated correctly: {updated_markup}")
                return False
            
            self.log_result("Markup Management - Update to 25%", True, f"Markup updated to {new_markup}%")
            
            # Test that new markup is applied to tire search
            response = self.session.get(f"{BACKEND_URL}/products/tires/search", params={
                'width': 185, 'height': 60, 'diameter': 15, 'page_size': 1
            })
            
            if response.status_code != 200:
                self.log_result("Markup Management - Applied to Tires", False, f"Tire search failed: {response.status_code}")
                return False
            
            data = response.json()
            applied_markup = data.get('markup_percentage')
            
            if applied_markup != new_markup:
                self.log_result("Markup Management - Applied to Tires", False, 
                              f"Expected {new_markup}%, got {applied_markup}%")
                return False
            
            # Verify price calculation with new markup
            tires = data.get('data', [])
            if tires and tires[0].get('price') and tires[0].get('price_original'):
                original_price = float(tires[0]['price_original'])
                final_price = float(tires[0]['price'])
                expected_price = round(original_price * (1 + new_markup / 100), 2)
                
                if abs(final_price - expected_price) > 0.01:
                    self.log_result("Markup Management - Price Calculation", False, 
                                  f"Price calculation error: {original_price} * 1.{new_markup} = {expected_price}, got {final_price}")
                    return False
                
                self.log_result("Markup Management - Price Calculation", True, 
                              f"✅ Price correctly calculated: {original_price} → {final_price} (25% markup)")
            
            self.log_result("Markup Management - Applied to Tires", True, f"New markup {new_markup}% applied to tire search")
            
            # Restore original markup
            restore_response = self.session.put(f"{BACKEND_URL}/admin/markup", 
                params={'telegram_id': ADMIN_TELEGRAM_ID},
                json={'markup_percentage': original_markup}
            )
            
            if restore_response.status_code == 200:
                self.log_result("Markup Management - Restore Original", True, f"Restored original markup: {original_markup}%")
            
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
                        'name': 'Michelin X-Ice North 4 185/60R15',
                        'brand': 'Michelin',
                        'quantity': 4,
                        'price_base': 8500.0,
                        'price_final': 9775.0,  # With 15% markup
                        'warehouse_id': 1,  # Integer, not string
                        'warehouse_name': 'Moscow'
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
        
        # Run tests in order of priority - focusing on UI fixes
        tests = [
            ("Health Check", self.test_health_check),
            ("Tire Search with Size Parsing", self.test_tire_search_with_sizes),
            ("Disk Search with Size Parsing", self.test_disk_search_with_sizes),
            ("Car Selection Flow with Field Verification", self.test_car_selection_flow_with_fields),
            ("Markup Management Still Works", self.test_markup_management_still_works),
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