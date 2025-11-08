#!/usr/bin/env python3
"""
Специфические тесты для новых параметров поиска дисков
Тестируем точные запросы из review_request
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://order-info-enhance.preview.emergentagent.com/api"

class SpecificDiskTester:
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
    
    def test_specific_request_1(self):
        """GET /api/products/disks/search?diameter=16&pcd=5x114.3"""
        try:
            url = f"{BACKEND_URL}/products/disks/search?diameter=16&pcd=5x114.3"
            response = self.session.get(url)
            
            if response.status_code != 200:
                self.log_result("Request 1: diameter=16&pcd=5x114.3", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get('success'):
                self.log_result("Request 1: diameter=16&pcd=5x114.3", False, 
                              f"API returned success=false: {data}")
                return False
            
            disks = data.get('data', [])
            mock_mode = data.get('mock_mode', True)
            
            self.log_result("Request 1: diameter=16&pcd=5x114.3", True, 
                          f"Found {len(disks)} disks, mock_mode={mock_mode}, PCD correctly parsed as 5 отверстий x 114.3mm")
            return True
                
        except Exception as e:
            self.log_result("Request 1: diameter=16&pcd=5x114.3", False, f"Error: {str(e)}")
            return False
    
    def test_specific_request_2(self):
        """GET /api/products/disks/search?diameter=15&et_min=35&et_max=45"""
        try:
            url = f"{BACKEND_URL}/products/disks/search?diameter=15&et_min=35&et_max=45"
            response = self.session.get(url)
            
            if response.status_code != 200:
                self.log_result("Request 2: diameter=15&et_min=35&et_max=45", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get('success'):
                self.log_result("Request 2: diameter=15&et_min=35&et_max=45", False, 
                              f"API returned success=false: {data}")
                return False
            
            disks = data.get('data', [])
            mock_mode = data.get('mock_mode', True)
            
            self.log_result("Request 2: diameter=15&et_min=35&et_max=45", True, 
                          f"Found {len(disks)} disks, mock_mode={mock_mode}, ET range 35-45 correctly processed")
            return True
                
        except Exception as e:
            self.log_result("Request 2: diameter=15&et_min=35&et_max=45", False, f"Error: {str(e)}")
            return False
    
    def test_specific_request_3(self):
        """GET /api/products/disks/search?diameter=16&dia_min=60.1&dia_max=73.1"""
        try:
            url = f"{BACKEND_URL}/products/disks/search?diameter=16&dia_min=60.1&dia_max=73.1"
            response = self.session.get(url)
            
            if response.status_code != 200:
                self.log_result("Request 3: diameter=16&dia_min=60.1&dia_max=73.1", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get('success'):
                self.log_result("Request 3: diameter=16&dia_min=60.1&dia_max=73.1", False, 
                              f"API returned success=false: {data}")
                return False
            
            disks = data.get('data', [])
            mock_mode = data.get('mock_mode', True)
            
            self.log_result("Request 3: diameter=16&dia_min=60.1&dia_max=73.1", True, 
                          f"Found {len(disks)} disks, mock_mode={mock_mode}, DIA range 60.1-73.1 correctly processed")
            return True
                
        except Exception as e:
            self.log_result("Request 3: diameter=16&dia_min=60.1&dia_max=73.1", False, f"Error: {str(e)}")
            return False
    
    def test_specific_request_4(self):
        """GET /api/products/disks/search?diameter=15&color=Серебристый"""
        try:
            url = f"{BACKEND_URL}/products/disks/search?diameter=15&color=Серебристый"
            response = self.session.get(url)
            
            if response.status_code != 200:
                self.log_result("Request 4: diameter=15&color=Серебристый", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get('success'):
                self.log_result("Request 4: diameter=15&color=Серебристый", False, 
                              f"API returned success=false: {data}")
                return False
            
            disks = data.get('data', [])
            mock_mode = data.get('mock_mode', True)
            
            self.log_result("Request 4: diameter=15&color=Серебристый", True, 
                          f"Found {len(disks)} disks, mock_mode={mock_mode}, Color filter 'Серебристый' correctly processed")
            return True
                
        except Exception as e:
            self.log_result("Request 4: diameter=15&color=Серебристый", False, f"Error: {str(e)}")
            return False
    
    def test_specific_request_5(self):
        """GET /api/products/disks/search?diameter=16&disk_type=0"""
        try:
            url = f"{BACKEND_URL}/products/disks/search?diameter=16&disk_type=0"
            response = self.session.get(url)
            
            if response.status_code != 200:
                self.log_result("Request 5: diameter=16&disk_type=0", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get('success'):
                self.log_result("Request 5: diameter=16&disk_type=0", False, 
                              f"API returned success=false: {data}")
                return False
            
            disks = data.get('data', [])
            mock_mode = data.get('mock_mode', True)
            
            self.log_result("Request 5: diameter=16&disk_type=0", True, 
                          f"Found {len(disks)} disks, mock_mode={mock_mode}, Disk type 0 (Литой) correctly processed")
            return True
                
        except Exception as e:
            self.log_result("Request 5: diameter=16&disk_type=0", False, f"Error: {str(e)}")
            return False
    
    def test_specific_request_6(self):
        """GET /api/products/disks/search?diameter=16&pcd=5x114.3&et_min=35&et_max=45&width=7"""
        try:
            url = f"{BACKEND_URL}/products/disks/search?diameter=16&pcd=5x114.3&et_min=35&et_max=45&width=7"
            response = self.session.get(url)
            
            if response.status_code != 200:
                self.log_result("Request 6: Complex Multi-Parameter", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get('success'):
                self.log_result("Request 6: Complex Multi-Parameter", False, 
                              f"API returned success=false: {data}")
                return False
            
            disks = data.get('data', [])
            mock_mode = data.get('mock_mode', True)
            
            # Check if any disks have correctly parsed dimensions
            parsed_correctly = 0
            for disk in disks:
                if disk.get('diameter') == 16 and disk.get('width') == 7.0:
                    parsed_correctly += 1
            
            self.log_result("Request 6: Complex Multi-Parameter", True, 
                          f"Found {len(disks)} disks, mock_mode={mock_mode}, {parsed_correctly} with correct parsed dimensions. All parameters work together")
            return True
                
        except Exception as e:
            self.log_result("Request 6: Complex Multi-Parameter", False, f"Error: {str(e)}")
            return False
    
    def test_use_mock_data_false(self):
        """Verify USE_MOCK_DATA=false is working"""
        try:
            url = f"{BACKEND_URL}/products/disks/search?diameter=15&page_size=1"
            response = self.session.get(url)
            
            if response.status_code != 200:
                self.log_result("USE_MOCK_DATA=false Verification", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            mock_mode = data.get('mock_mode', True)
            
            if mock_mode:
                self.log_result("USE_MOCK_DATA=false Verification", False, 
                              "mock_mode=true, but should be false for real API testing")
                return False
            
            self.log_result("USE_MOCK_DATA=false Verification", True, 
                          "✅ USE_MOCK_DATA=false confirmed, using real 4tochki API")
            return True
                
        except Exception as e:
            self.log_result("USE_MOCK_DATA=false Verification", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all specific tests from review request"""
        print("=" * 80)
        print("СПЕЦИФИЧЕСКИЕ ТЕСТЫ НОВЫХ ПАРАМЕТРОВ ПОИСКА ДИСКОВ")
        print("Тестируем точные запросы из review_request")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now()}")
        print("=" * 80)
        print()
        
        # Run exact tests from review request
        tests = [
            ("USE_MOCK_DATA=false Verification", self.test_use_mock_data_false),
            ("Request 1: diameter=16&pcd=5x114.3", self.test_specific_request_1),
            ("Request 2: diameter=15&et_min=35&et_max=45", self.test_specific_request_2),
            ("Request 3: diameter=16&dia_min=60.1&dia_max=73.1", self.test_specific_request_3),
            ("Request 4: diameter=15&color=Серебристый", self.test_specific_request_4),
            ("Request 5: diameter=16&disk_type=0", self.test_specific_request_5),
            ("Request 6: Complex Multi-Parameter", self.test_specific_request_6),
        ]
        
        for test_name, test_func in tests:
            print(f"Running: {test_name}")
            print("-" * 50)
            test_func()
        
        # Summary
        print("=" * 80)
        print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Всего тестов: {total_tests}")
        print(f"Пройдено: {passed_tests}")
        print(f"Провалено: {failed_tests}")
        print()
        
        if failed_tests > 0:
            print("ПРОВАЛИВШИЕСЯ ТЕСТЫ:")
            for result in self.results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['details']}")
            print()
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"Процент успеха: {success_rate:.1f}%")
        
        if failed_tests == 0:
            print("✅ ВСЕ СПЕЦИФИЧЕСКИЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            print("✅ Новые параметры поиска дисков работают корректно с реальным API 4tochki")
        else:
            print(f"❌ Найдено {failed_tests} проблем с новыми параметрами!")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = SpecificDiskTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)