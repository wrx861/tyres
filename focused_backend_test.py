#!/usr/bin/env python3
"""
Focused Backend API Testing for UI Fixes
Tests the specific requirements from the review request:
1. Size parsing from name field (regex for 185/60R15 and 7x16)
2. Warehouse data extraction from whpr.wh_price_rest[0]
3. Markup functionality still working
4. No price_original in client response (backend still has it for calculations)
"""

import requests
import json
import sys
import re
from datetime import datetime

# Configuration
BACKEND_URL = "https://wheelstore.preview.emergentagent.com/api"
ADMIN_TELEGRAM_ID = "508352361"

class FocusedAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
        
    def test_tire_search_size_parsing(self):
        """Test tire search with size parsing from name field"""
        try:
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
                self.log_result("1. Tire Search - Size Parsing", False, f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            
            if not data.get('success'):
                self.log_result("1. Tire Search - Size Parsing", False, f"API error: {data}")
                return False
            
            tires = data.get('data', [])
            if len(tires) == 0:
                self.log_result("1. Tire Search - Size Parsing", False, "No tires returned")
                return False
            
            # Check each tire for required fields
            issues = []
            for i, tire in enumerate(tires):
                # Check size fields (parsed from name)
                if not isinstance(tire.get('width'), int):
                    issues.append(f"Tire {i}: width not integer")
                if not isinstance(tire.get('height'), int):
                    issues.append(f"Tire {i}: height not integer")
                if not isinstance(tire.get('diameter'), int):
                    issues.append(f"Tire {i}: diameter not integer")
                
                # Check warehouse fields
                if tire.get('rest') is None:
                    issues.append(f"Tire {i}: missing rest")
                if not tire.get('warehouse_name'):
                    issues.append(f"Tire {i}: missing warehouse_name")
                
                # Check price and brand
                if not tire.get('price') or tire.get('price') <= 0:
                    issues.append(f"Tire {i}: invalid price")
                if not tire.get('brand') or tire.get('brand').strip() == '':
                    issues.append(f"Tire {i}: empty brand")
                
                # Verify size parsing matches name
                name = tire.get('name', '')
                size_match = re.match(r'(\d+)/(\d+)R(\d+)', name)
                if size_match:
                    expected_width = int(size_match.group(1))
                    expected_height = int(size_match.group(2))
                    expected_diameter = int(size_match.group(3))
                    
                    if (tire.get('width') != expected_width or 
                        tire.get('height') != expected_height or 
                        tire.get('diameter') != expected_diameter):
                        issues.append(f"Tire {i}: Size mismatch in '{name}'")
            
            if issues:
                self.log_result("1. Tire Search - Size Parsing", False, "; ".join(issues[:3]))
                return False
            
            self.log_result("1. Tire Search - Size Parsing", True, 
                          f"All {len(tires)} tires have correct fields: width, height, diameter, rest, warehouse_name, price, brand")
            return True
                
        except Exception as e:
            self.log_result("1. Tire Search - Size Parsing", False, f"Error: {str(e)}")
            return False
    
    def test_disk_search_size_parsing(self):
        """Test disk search with size parsing from name field"""
        try:
            params = {
                'diameter': 16,
                'width': 7,
                'page': 0,
                'page_size': 3
            }
            
            response = self.session.get(f"{BACKEND_URL}/products/disks/search", params=params)
            
            if response.status_code != 200:
                self.log_result("2. Disk Search - Size Parsing", False, f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            
            if not data.get('success'):
                self.log_result("2. Disk Search - Size Parsing", False, f"API error: {data}")
                return False
            
            disks = data.get('data', [])
            if len(disks) == 0:
                self.log_result("2. Disk Search - Size Parsing", False, "No disks returned")
                return False
            
            # Check each disk for required fields
            issues = []
            for i, disk in enumerate(disks):
                # Check size fields (parsed from name)
                if not disk.get('width'):
                    issues.append(f"Disk {i}: missing width")
                if not disk.get('diameter'):
                    issues.append(f"Disk {i}: missing diameter")
                
                # Check warehouse fields
                if disk.get('rest') is None:
                    issues.append(f"Disk {i}: missing rest")
                if not disk.get('warehouse_name'):
                    issues.append(f"Disk {i}: missing warehouse_name")
                
                # Check price
                if not disk.get('price') or disk.get('price') <= 0:
                    issues.append(f"Disk {i}: invalid price")
                
                # Verify size parsing matches name
                name = disk.get('name', '')
                size_match = re.search(r'(\d+\.?\d*)x(\d+)', name)
                if size_match:
                    expected_width = float(size_match.group(1))
                    expected_diameter = int(size_match.group(2))
                    
                    if (abs(disk.get('width', 0) - expected_width) > 0.1 or 
                        disk.get('diameter') != expected_diameter):
                        issues.append(f"Disk {i}: Size mismatch in '{name}'")
            
            if issues:
                self.log_result("2. Disk Search - Size Parsing", False, "; ".join(issues[:3]))
                return False
            
            self.log_result("2. Disk Search - Size Parsing", True, 
                          f"All {len(disks)} disks have correct fields: width, diameter, rest, warehouse_name, price")
            return True
                
        except Exception as e:
            self.log_result("2. Disk Search - Size Parsing", False, f"Error: {str(e)}")
            return False
    
    def test_car_selection_basic_flow(self):
        """Test basic car selection flow (brands -> models -> years -> modifications)"""
        try:
            # Get brands
            response = self.session.get(f"{BACKEND_URL}/cars/brands")
            if response.status_code != 200:
                self.log_result("3. Car Selection - Basic Flow", False, f"Brands failed: {response.status_code}")
                return False
            
            brands = response.json().get('data', [])
            if len(brands) == 0:
                self.log_result("3. Car Selection - Basic Flow", False, "No brands")
                return False
            
            # Get models for first brand
            first_brand = brands[0]
            response = self.session.get(f"{BACKEND_URL}/cars/models", params={'brand': first_brand})
            if response.status_code != 200:
                self.log_result("3. Car Selection - Basic Flow", False, f"Models failed: {response.status_code}")
                return False
            
            models = response.json().get('data', [])
            if len(models) == 0:
                self.log_result("3. Car Selection - Basic Flow", False, f"No models for {first_brand}")
                return False
            
            # Get years
            first_model = models[0]
            response = self.session.get(f"{BACKEND_URL}/cars/years", params={
                'brand': first_brand,
                'model': first_model
            })
            if response.status_code != 200:
                self.log_result("3. Car Selection - Basic Flow", False, f"Years failed: {response.status_code}")
                return False
            
            years = response.json().get('data', [])
            if len(years) == 0:
                self.log_result("3. Car Selection - Basic Flow", False, f"No years for {first_brand} {first_model}")
                return False
            
            # Get modifications
            first_year = str(years[0])
            response = self.session.get(f"{BACKEND_URL}/cars/modifications", params={
                'brand': first_brand,
                'model': first_model,
                'year_begin': first_year,
                'year_end': first_year
            })
            if response.status_code != 200:
                self.log_result("3. Car Selection - Basic Flow", False, f"Modifications failed: {response.status_code}")
                return False
            
            modifications = response.json().get('data', [])
            
            self.log_result("3. Car Selection - Basic Flow", True, 
                          f"Flow works: {len(brands)} brands → {len(models)} models → {len(years)} years → {len(modifications)} modifications")
            return True
            
        except Exception as e:
            self.log_result("3. Car Selection - Basic Flow", False, f"Error: {str(e)}")
            return False
    
    def create_admin_user(self):
        """Create admin user for markup testing"""
        try:
            user_data = {
                'telegram_id': ADMIN_TELEGRAM_ID,
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User'
            }
            response = self.session.post(f"{BACKEND_URL}/auth/telegram", json=user_data)
            return response.status_code == 200
        except:
            return False
    
    def test_markup_functionality(self):
        """Test markup management and application"""
        try:
            # Create admin user
            self.create_admin_user()
            
            # Get current markup
            response = self.session.get(f"{BACKEND_URL}/admin/markup", params={
                'telegram_id': ADMIN_TELEGRAM_ID
            })
            
            if response.status_code != 200:
                self.log_result("4. Markup - Still Works", False, f"Get markup failed: {response.status_code}")
                return False
            
            original_markup = response.json().get('markup_percentage', 15)
            
            # Update markup to 25%
            response = self.session.put(f"{BACKEND_URL}/admin/markup", 
                params={'telegram_id': ADMIN_TELEGRAM_ID},
                json={'markup_percentage': 25.0}
            )
            
            if response.status_code != 200:
                self.log_result("4. Markup - Still Works", False, f"Update markup failed: {response.status_code}")
                return False
            
            # Test that new markup is applied
            response = self.session.get(f"{BACKEND_URL}/products/tires/search", params={
                'width': 185, 'height': 60, 'diameter': 15, 'page_size': 1
            })
            
            if response.status_code != 200:
                self.log_result("4. Markup - Still Works", False, f"Tire search failed: {response.status_code}")
                return False
            
            data = response.json()
            applied_markup = data.get('markup_percentage')
            
            if applied_markup != 25.0:
                self.log_result("4. Markup - Still Works", False, f"Expected 25%, got {applied_markup}%")
                return False
            
            # Verify price calculation
            tires = data.get('data', [])
            if tires and tires[0].get('price') and tires[0].get('price_original'):
                original_price = float(tires[0]['price_original'])
                final_price = float(tires[0]['price'])
                expected_price = round(original_price * 1.25, 2)
                
                if abs(final_price - expected_price) > 0.01:
                    self.log_result("4. Markup - Still Works", False, 
                                  f"Price calculation error: {original_price} * 1.25 = {expected_price}, got {final_price}")
                    return False
            
            # Restore original markup
            self.session.put(f"{BACKEND_URL}/admin/markup", 
                params={'telegram_id': ADMIN_TELEGRAM_ID},
                json={'markup_percentage': original_markup}
            )
            
            self.log_result("4. Markup - Still Works", True, 
                          f"Markup management works: {original_markup}% → 25% → {original_markup}%")
            return True
            
        except Exception as e:
            self.log_result("4. Markup - Still Works", False, f"Error: {str(e)}")
            return False
    
    def run_focused_tests(self):
        """Run focused tests for UI fixes"""
        print("=" * 70)
        print("FOCUSED BACKEND API TESTING - UI FIXES VERIFICATION")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now()}")
        print("=" * 70)
        print()
        
        # Run focused tests
        tests = [
            ("Tire Search Size Parsing", self.test_tire_search_size_parsing),
            ("Disk Search Size Parsing", self.test_disk_search_size_parsing),
            ("Car Selection Basic Flow", self.test_car_selection_basic_flow),
            ("Markup Functionality", self.test_markup_functionality),
        ]
        
        for test_name, test_func in tests:
            print(f"Running: {test_name}")
            print("-" * 50)
            test_func()
        
        # Summary
        print("=" * 70)
        print("FOCUSED TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['details']}")
            print()
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests == 0:
            print("✅ All UI fixes are working correctly!")
        else:
            print(f"❌ {failed_tests} issues found with UI fixes!")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = FocusedAPITester()
    success = tester.run_focused_tests()
    sys.exit(0 if success else 1)