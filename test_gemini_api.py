#!/usr/bin/env python3
"""
Test script for HackRX API with Gemini
"""
import requests
import json
import time

# Test configuration
API_BASE_URL = "http://localhost:5001"
TEST_PDF_URL = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

def test_health_endpoint():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        print(f"Health Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health test failed: {e}")
        return False

def test_hackrx_endpoint():
    """Test the main HackRX endpoint"""
    print("\nTesting HackRX endpoint...")
    
    # Test data
    test_data = {
        "documents": TEST_PDF_URL,
        "questions": [
            "What is this document about?",
            "What is the main topic discussed?"
        ]
    }
    
    try:
        print(f"Sending request to {API_BASE_URL}/api/v1/hackrx/run")
        print(f"Test data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/hackrx/run",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutes timeout
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Number of answers: {len(result.get('answers', []))}")
            print(f"Number of questions: {len(test_data['questions'])}")
            
            for i, answer in enumerate(result.get('answers', [])):
                print(f"\nQuestion {i+1}: {test_data['questions'][i]}")
                print(f"Answer {i+1}: {answer}")
            
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting HackRX API Tests with Gemini")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    
    if not health_ok:
        print("❌ Health check failed. Stopping tests.")
        return
    
    # Test main endpoint
    hackrx_ok = test_hackrx_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"HackRX Endpoint: {'✅ PASS' if hackrx_ok else '❌ FAIL'}")
    
    if health_ok and hackrx_ok:
        print("\n🎉 All tests passed! Gemini API integration successful.")
    else:
        print("\n⚠️  Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()

