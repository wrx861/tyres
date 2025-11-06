#!/usr/bin/env python3
"""
Debug script to test 4tochki API connection
"""

import sys
import os
sys.path.append('/app/backend')

from services.fourthchki_client import get_fourthchki_client
import logging

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_api_connection():
    """Test basic API connection"""
    try:
        print("Testing 4tochki API connection...")
        print(f"Login: {os.environ.get('FOURTHCHKI_LOGIN')}")
        print(f"API URL: {os.environ.get('FOURTHCHKI_API_URL')}")
        
        client = get_fourthchki_client()
        print("✅ SOAP client initialized successfully")
        
        # Test getting car brands (simplest call)
        print("\nTesting GetMarkaAvto...")
        response = client.get_car_brands()
        print(f"Response type: {type(response)}")
        print(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        if 'error' in response:
            print(f"❌ API Error: {response['error']}")
            return False
        else:
            print(f"✅ API call successful")
            if 'marka_list' in response:
                brands = response['marka_list']
                print(f"Found {len(brands)} brands")
                if brands:
                    print(f"First few brands: {brands[:5]}")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_api_connection()