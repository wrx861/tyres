#!/usr/bin/env python3
"""
Debug script to test 4tochki API connection
"""

import sys
import os
sys.path.append('/app/backend')

# Load environment variables
from dotenv import load_dotenv
from pathlib import Path
load_dotenv('/app/backend/.env')

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
        print(f"Response: {response}")
        
        if response.get('error'):
            error = response['error']
            print(f"❌ API Error: {error}")
            
            # Check if it's an authentication issue
            if error.get('code') is None and error.get('comment') is None:
                print("This looks like an authentication or credentials issue")
                
                # Try to get more info from the SOAP client
                print("\nTesting direct SOAP call...")
                try:
                    raw_response = client.client.service.GetMarkaAvto(
                        login=client.login,
                        password=client.password
                    )
                    print(f"Raw SOAP response: {raw_response}")
                except Exception as soap_e:
                    print(f"SOAP call error: {soap_e}")
                    
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