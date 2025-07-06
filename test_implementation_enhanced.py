#!/usr/bin/env python3
"""
Enhanced Test Implementation for Financial Sentiment Dashboard
Tests all major components: Backend API, Frontend, Database, Authentication
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any
import os

class DashboardTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "start_time": None,
                "end_time": None
            }
        }
        self.session = requests.Session()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
        """Log test result"""
        test_result = {
            "name": test_name,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.results["tests"].append(test_result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({response_time:.2f}s)")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_health_check(self) -> bool:
        """Test API health endpoint"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                details = f"Status: {data.get('status')}, Database: {data.get('database')}"
                self.log_test("Health Check", True, details, response_time)
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_test("Health Check", False, str(e), 0)
            return False
    
    def test_authentication(self) -> bool:
        """Test authentication endpoints"""
        try:
            # Test login with valid credentials
            start_time = time.time()
            login_data = {
                "username": "admin",
                "password": os.getenv("ADMIN_PASSWORD", "admin123")
            }
            response = self.session.post(
                f"{self.base_url}/auth/login",
                data=login_data
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    # Store token for protected route tests
                    self.session.headers.update({"Authorization": f"Bearer {data['access_token']}"})
                    self.log_test("Authentication Login", True, "Token received", response_time)
                    
                    # Test protected route
                    start_time = time.time()
                    protected_response = self.session.get(f"{self.base_url}/auth/me")
                    response_time = time.time() - start_time
                    
                    if protected_response.status_code == 200:
                        self.log_test("Protected Route Access", True, "User info retrieved", response_time)
                        return True
                    else:
                        self.log_test("Protected Route Access", False, f"Status: {protected_response.status_code}", response_time)
                        return False
                else:
                    self.log_test("Authentication Login", False, "No token in response", response_time)
                    return False
            else:
                self.log_test("Authentication Login", False, f"Status: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_test("Authentication", False, str(e), 0)
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test all major API endpoints"""
        endpoints = [
            ("/api/sentiment/summary", "Sentiment Summary"),
            ("/api/sentiment/timeline", "Sentiment Timeline"),
            ("/api/correlation/analysis", "Correlation Analysis"),
            ("/api/stocks/prices", "Stock Prices"),
            ("/api/news/latest", "Latest News"),
            ("/api/dashboard/stats", "Dashboard Stats"),
            ("/api/sentiment/summary_by_symbol", "Sentiment by Symbol"),
            ("/api/stocks/prices_by_symbol", "Stock Prices by Symbol")
        ]
        
        all_success = True
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    details = f"Data received: {len(str(data))} chars"
                    self.log_test(f"API {name}", True, details, response_time)
                else:
                    self.log_test(f"API {name}", False, f"Status: {response.status_code}", response_time)
                    all_success = False
            except Exception as e:
                self.log_test(f"API {name}", False, str(e), 0)
                all_success = False
        
        return all_success
    
    def test_metrics_endpoint(self) -> bool:
        """Test metrics endpoint"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/metrics")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                details = f"Requests: {data.get('request_count', 0)}, Errors: {data.get('error_count', 0)}"
                self.log_test("Metrics Endpoint", True, details, response_time)
                return True
            else:
                self.log_test("Metrics Endpoint", False, f"Status: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_test("Metrics Endpoint", False, str(e), 0)
            return False
    
    def test_frontend_accessibility(self) -> bool:
        """Test if frontend is accessible"""
        try:
            frontend_url = "http://localhost:3000"  # Default Vite dev server
            start_time = time.time()
            response = requests.get(frontend_url, timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test("Frontend Accessibility", True, "Frontend is running", response_time)
                return True
            else:
                self.log_test("Frontend Accessibility", False, f"Status: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_test("Frontend Accessibility", False, f"Frontend not accessible: {str(e)}", 0)
            return False
    
    def test_database_connection(self) -> bool:
        """Test database connection through API"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("database") == "connected":
                    self.log_test("Database Connection", True, "Database is connected", response_time)
                    return True
                else:
                    self.log_test("Database Connection", False, "Database not connected", response_time)
                    return False
            else:
                self.log_test("Database Connection", False, f"Health check failed: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_test("Database Connection", False, str(e), 0)
            return False
    
    def test_data_quality(self) -> bool:
        """Test data quality and consistency"""
        try:
            # Test sentiment summary
            response = self.session.get(f"{self.base_url}/api/sentiment/summary")
            if response.status_code == 200:
                data = response.json()
                summary = data.get("summary", [])
                
                if summary:
                    # Check if sentiment scores are within valid range
                    valid_scores = all(
                        -1 <= item.get("avg_score", 0) <= 1 
                        for item in summary
                    )
                    
                    if valid_scores:
                        self.log_test("Data Quality", True, f"Valid sentiment scores in {len(summary)} categories")
                        return True
                    else:
                        self.log_test("Data Quality", False, "Invalid sentiment scores detected")
                        return False
                else:
                    self.log_test("Data Quality", False, "No sentiment data available")
                    return False
            else:
                self.log_test("Data Quality", False, f"API error: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Data Quality", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        print("🚀 Starting Enhanced Dashboard Tests")
        print("=" * 50)
        
        self.results["summary"]["start_time"] = datetime.now().isoformat()
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Database Connection", self.test_database_connection),
            ("Authentication", self.test_authentication),
            ("API Endpoints", self.test_api_endpoints),
            ("Metrics Endpoint", self.test_metrics_endpoint),
            ("Frontend Accessibility", self.test_frontend_accessibility),
            ("Data Quality", self.test_data_quality)
        ]
        
        for test_name, test_func in tests:
            try:
                success = test_func()
                self.results["summary"]["total"] += 1
                if success:
                    self.results["summary"]["passed"] += 1
                else:
                    self.results["summary"]["failed"] += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test error: {str(e)}")
                self.results["summary"]["total"] += 1
                self.results["summary"]["failed"] += 1
        
        self.results["summary"]["end_time"] = datetime.now().isoformat()
        
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {self.results['summary']['total']}")
        print(f"Passed: {self.results['summary']['passed']} ✅")
        print(f"Failed: {self.results['summary']['failed']} ❌")
        
        success_rate = (self.results["summary"]["passed"] / self.results["summary"]["total"]) * 100 if self.results["summary"]["total"] > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Save results to file
        with open("test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: test_results.json")
        
        return self.results

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Dashboard Tester")
    parser.add_argument("--url", default="http://localhost:8000", help="Backend API URL")
    parser.add_argument("--output", default="test_results.json", help="Output file for results")
    
    args = parser.parse_args()
    
    tester = DashboardTester(args.url)
    results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    if results["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main() 