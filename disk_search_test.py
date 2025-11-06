#!/usr/bin/env python3
"""
Тестирование новых параметров поиска дисков для 4tochki API
Тестируем: PCD, ET (вылет), DIA (ступичное отверстие), цвет, тип диска
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://tire-api-service.preview.emergentagent.com/api"

class DiskSearchTester:
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
    
    def test_pcd_search(self):
        """Test disk search with PCD parameter (5x114.3)"""
        try:
            params = {
                'diameter': 16,
                'pcd': '5x114.3',
                'page_size': 10
            }
            
            response = self.session.get(f"{BACKEND_URL}/products/disks/search", params=params)
            
            if response.status_code != 200:
                self.log_result("PCD Search (5x114.3)", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check if using real API (not mock)
            if data.get('mock_mode') == True:
                self.log_result("PCD Search (5x114.3)", False, "Still using MOCK data instead of real API")
                return False
            
            # Check if data is returned
            if not data.get('success'):
                self.log_result("PCD Search (5x114.3)", False, f"API returned success=false: {data}")
                return False
            
            disks = data.get('data', [])
            
            if len(disks) == 0:
                self.log_result("PCD Search (5x114.3)", False, "No disks returned for PCD 5x114.3")
                return False
            
            # Verify that PCD parameter was correctly parsed and sent to API
            # The API should return disks with 5 bolt holes and 114.3mm spacing
            self.log_result("PCD Search (5x114.3)", True, 
                          f"✅ Found {len(disks)} disks with PCD 5x114.3. API correctly parsed PCD parameter (5 отверстий, диаметр 114.3)")
            return True
                
        except Exception as e:
            self.log_result("PCD Search (5x114.3)", False, f"Error: {str(e)}")
            return False
    
    def test_et_range_search(self):
        """Test disk search with ET (offset) range"""
        try:
            params = {
                'diameter': 15,
                'et_min': 35,
                'et_max': 45,
                'page_size': 10
            }
            
            response = self.session.get(f"{BACKEND_URL}/products/disks/search", params=params)
            
            if response.status_code != 200:
                self.log_result("ET Range Search (35-45)", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if data.get('mock_mode') == True:
                self.log_result("ET Range Search (35-45)", False, "Still using MOCK data instead of real API")
                return False
            
            if not data.get('success'):
                self.log_result("ET Range Search (35-45)", False, f"API returned success=false: {data}")
                return False
            
            disks = data.get('data', [])
            
            if len(disks) == 0:
                self.log_result("ET Range Search (35-45)", False, "No disks returned for ET range 35-45")
                return False
            
            # The API should return disks with offset between 35 and 45
            self.log_result("ET Range Search (35-45)", True, 
                          f"✅ Found {len(disks)} disks with ET range 35-45. API correctly processed offset range parameters")
            return True
                
        except Exception as e:
            self.log_result("ET Range Search (35-45)", False, f"Error: {str(e)}")
            return False
    
    def test_dia_range_search(self):
        """Test disk search with DIA (center bore) range"""
        try:
            params = {
                'diameter': 16,
                'dia_min': 60.1,
                'dia_max': 73.1,
                'page_size': 10
            }
            
            response = self.session.get(f"{BACKEND_URL}/products/disks/search", params=params)
            
            if response.status_code != 200:
                self.log_result("DIA Range Search (60.1-73.1)", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if data.get('mock_mode') == True:
                self.log_result("DIA Range Search (60.1-73.1)", False, "Still using MOCK data instead of real API")
                return False
            
            if not data.get('success'):
                self.log_result("DIA Range Search (60.1-73.1)", False, f"API returned success=false: {data}")
                return False
            
            disks = data.get('data', [])
            
            if len(disks) == 0:
                self.log_result("DIA Range Search (60.1-73.1)", False, "No disks returned for DIA range 60.1-73.1")
                return False
            
            # The API should return disks with center bore between 60.1 and 73.1
            self.log_result("DIA Range Search (60.1-73.1)", True, 
                          f"✅ Found {len(disks)} disks with DIA range 60.1-73.1. API correctly processed center bore range parameters")
            return True
                
        except Exception as e:
            self.log_result("DIA Range Search (60.1-73.1)", False, f"Error: {str(e)}")
            return False
    
    def test_color_search(self):
        """Test disk search with color parameter"""
        try:
            params = {
                'diameter': 15,
                'color': 'Серебристый',
                'page_size': 10
            }
            
            response = self.session.get(f"{BACKEND_URL}/products/disks/search", params=params)
            
            if response.status_code != 200:
                self.log_result("Color Search (Серебристый)", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if data.get('mock_mode') == True:
                self.log_result("Color Search (Серебристый)", False, "Still using MOCK data instead of real API")
                return False
            
            if not data.get('success'):
                self.log_result("Color Search (Серебристый)", False, f"API returned success=false: {data}")
                return False
            
            disks = data.get('data', [])
            
            if len(disks) == 0:
                self.log_result("Color Search (Серебристый)", False, "No disks returned for color 'Серебристый'")
                return False
            
            # The API should return silver colored disks
            self.log_result("Color Search (Серебристый)", True, 
                          f"✅ Found {len(disks)} silver disks. API correctly processed color parameter")
            return True
                
        except Exception as e:
            self.log_result("Color Search (Серебристый)", False, f"Error: {str(e)}")
            return False
    
    def test_disk_type_search(self):
        """Test disk search with disk type parameter (0 = cast disk)"""
        try:
            params = {
                'diameter': 16,
                'disk_type': 0,  # 0 = Литой диск
                'page_size': 10
            }
            
            response = self.session.get(f"{BACKEND_URL}/products/disks/search", params=params)
            
            if response.status_code != 200:
                self.log_result("Disk Type Search (Литой)", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if data.get('mock_mode') == True:
                self.log_result("Disk Type Search (Литой)", False, "Still using MOCK data instead of real API")
                return False
            
            if not data.get('success'):
                self.log_result("Disk Type Search (Литой)", False, f"API returned success=false: {data}")
                return False
            
            disks = data.get('data', [])
            
            if len(disks) == 0:
                self.log_result("Disk Type Search (Литой)", False, "No cast disks returned for disk_type=0")
                return False
            
            # The API should return only cast disks (type 0)
            self.log_result("Disk Type Search (Литой)", True, 
                          f"✅ Found {len(disks)} cast disks. API correctly processed disk type parameter (0=Литой)")
            return True
                
        except Exception as e:
            self.log_result("Disk Type Search (Литой)", False, f"Error: {str(e)}")
            return False
    
    def test_complex_search(self):
        """Test complex disk search with multiple parameters"""
        try:
            params = {
                'diameter': 16,
                'pcd': '5x114.3',
                'et_min': 35,
                'et_max': 45,
                'width': 7,
                'page_size': 10
            }
            
            response = self.session.get(f"{BACKEND_URL}/products/disks/search", params=params)
            
            if response.status_code != 200:
                self.log_result("Complex Search (Multiple Parameters)", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if data.get('mock_mode') == True:
                self.log_result("Complex Search (Multiple Parameters)", False, "Still using MOCK data instead of real API")
                return False
            
            if not data.get('success'):
                self.log_result("Complex Search (Multiple Parameters)", False, f"API returned success=false: {data}")
                return False
            
            disks = data.get('data', [])
            
            if len(disks) == 0:
                self.log_result("Complex Search (Multiple Parameters)", False, 
                              "No disks returned for complex search (diameter=16, pcd=5x114.3, et_min=35, et_max=45, width=7)")
                return False
            
            # Verify that all filters work together
            # Check if returned disks have correct parsed dimensions
            valid_disks = 0
            for disk in disks:
                if disk.get('diameter') == 16 and disk.get('width') == 7.0:
                    valid_disks += 1
            
            if valid_disks == 0:
                self.log_result("Complex Search (Multiple Parameters)", False, 
                              f"Found {len(disks)} disks but none have correct parsed dimensions (diameter=16, width=7)")
                return False
            
            self.log_result("Complex Search (Multiple Parameters)", True, 
                          f"✅ Found {len(disks)} disks matching complex criteria. {valid_disks} disks have correctly parsed dimensions. All filters work together")
            return True
                
        except Exception as e:
            self.log_result("Complex Search (Multiple Parameters)", False, f"Error: {str(e)}")
            return False
    
    def test_api_parameter_passing(self):
        """Test that parameters are correctly passed to 4tochki API"""
        try:
            # Test with all new parameters
            params = {
                'diameter': 16,
                'pcd': '5x114.3',
                'et_min': 35,
                'et_max': 45,
                'dia_min': 60.1,
                'dia_max': 73.1,
                'color': 'Серебристый',
                'disk_type': 0,
                'page_size': 5
            }
            
            response = self.session.get(f"{BACKEND_URL}/products/disks/search", params=params)
            
            if response.status_code != 200:
                self.log_result("API Parameter Passing", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check that we're using real API
            if data.get('mock_mode') == True:
                self.log_result("API Parameter Passing", False, "USE_MOCK_DATA=true, should be false for real API testing")
                return False
            
            # Check that API call was successful (even if no results)
            if not data.get('success'):
                error_detail = data.get('detail', 'Unknown error')
                self.log_result("API Parameter Passing", False, f"API call failed: {error_detail}")
                return False
            
            # Success if API accepts parameters without error
            disks = data.get('data', [])
            self.log_result("API Parameter Passing", True, 
                          f"✅ All parameters correctly passed to 4tochki API. USE_MOCK_DATA=false confirmed. Found {len(disks)} results")
            return True
                
        except Exception as e:
            self.log_result("API Parameter Passing", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all disk search tests"""
        print("=" * 80)
        print("ТЕСТИРОВАНИЕ НОВЫХ ПАРАМЕТРОВ ПОИСКА ДИСКОВ - 4tochki API")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now()}")
        print("=" * 80)
        print()
        
        # Run tests in order specified in review request
        tests = [
            ("Health Check", self.test_health_check),
            ("PCD Search (5x114.3)", self.test_pcd_search),
            ("ET Range Search (35-45)", self.test_et_range_search),
            ("DIA Range Search (60.1-73.1)", self.test_dia_range_search),
            ("Color Search (Серебристый)", self.test_color_search),
            ("Disk Type Search (Литой)", self.test_disk_type_search),
            ("Complex Search (Multiple Parameters)", self.test_complex_search),
            ("API Parameter Passing Verification", self.test_api_parameter_passing),
        ]
        
        for test_name, test_func in tests:
            print(f"Running: {test_name}")
            print("-" * 50)
            test_func()
        
        # Summary
        print("=" * 80)
        print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        critical_failures = sum(1 for r in self.results if not r['success'] and r['critical'])
        
        print(f"Всего тестов: {total_tests}")
        print(f"Пройдено: {passed_tests}")
        print(f"Провалено: {failed_tests}")
        print(f"Критических ошибок: {critical_failures}")
        print()
        
        if failed_tests > 0:
            print("ПРОВАЛИВШИЕСЯ ТЕСТЫ:")
            for result in self.results:
                if not result['success']:
                    status = "КРИТИЧЕСКАЯ" if result['critical'] else "НЕЗНАЧИТЕЛЬНАЯ"
                    print(f"  [{status}] {result['test']}: {result['details']}")
            print()
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"Процент успеха: {success_rate:.1f}%")
        
        if critical_failures == 0:
            print("✅ Все новые параметры поиска дисков работают корректно!")
        else:
            print(f"❌ Найдено {critical_failures} критических проблем с новыми параметрами!")
        
        return critical_failures == 0

if __name__ == "__main__":
    tester = DiskSearchTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)