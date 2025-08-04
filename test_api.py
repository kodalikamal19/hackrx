#!/usr/bin/env python3
"""
Test script for HackRX API
"""
import requests
import json
import time

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:5001/api/health', timeout=10)
        print(f"Health check status: {response.status_code}")
        print(f"Health check response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_hackrx_endpoint():
    """Test the main HackRX endpoint with sample data"""
    url = 'http://localhost:5001/api/v1/hackrx/run'
    
    # Sample data from the provided example
    test_data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?"
        ]
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        print("Testing HackRX endpoint...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=120)
        
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("Success! Response:")
            print(json.dumps(result, indent=2))
            
            # Validate response structure
            if 'answers' in result and len(result['answers']) == len(test_data['questions']):
                print("✅ Response structure is correct")
                return True
            else:
                print("❌ Response structure is incorrect")
                return False
        else:
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== HackRX API Test Suite ===\n")
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    health_ok = test_health_endpoint()
    print(f"Health check: {'✅ PASS' if health_ok else '❌ FAIL'}\n")
    
    if not health_ok:
        print("Server is not responding. Exiting.")
        return
    
    # Test main endpoint
    print("2. Testing HackRX endpoint...")
    hackrx_ok = test_hackrx_endpoint()
    print(f"HackRX endpoint: {'✅ PASS' if hackrx_ok else '❌ FAIL'}\n")
    
    # Summary
    print("=== Test Summary ===")
    print(f"Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"HackRX endpoint: {'✅ PASS' if hackrx_ok else '❌ FAIL'}")
    
    if health_ok and hackrx_ok:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!")

if __name__ == "__main__":
    main()

