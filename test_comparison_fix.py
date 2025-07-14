#!/usr/bin/env python3

import requests
import json
import time

def test_comparison_error():
    """Test to reproduce the numpy error during fingerprint comparison"""
    
    base_url = "http://localhost:5000"
    
    # Test data - simulate same template
    test_template = "SGVsbG8gV29ybGQhIFRoaXMgaXMgYSB0ZXN0IHRlbXBsYXRlIGZvciBmaW5nZXJwcmludCBjb21wYXJpc29u"
    
    print("🧪 Testing fingerprint comparison with same template...")
    print(f"Template: {test_template[:50]}...")
    
    try:
        # Test comparison with the same template
        comparison_data = {
            "template1_data": test_template,
            "template2_data": test_template,  # Same template
            "security_level": 1
        }
        
        print("\n📡 Sending comparison request...")
        response = requests.post(
            f"{base_url}/comparar-huellas",
            json=comparison_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Success: {result.get('success')}")
            print(f"✅ Matched: {result.get('matched')}")
            print(f"✅ Score: {result.get('score')}")
            print(f"✅ Message: {result.get('message')}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ Error details: {error_data}")
            except:
                print(f"❌ Raw error: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")

if __name__ == "__main__":
    test_comparison_error() 