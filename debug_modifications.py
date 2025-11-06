#!/usr/bin/env python3
"""
Debug car modifications API
"""

import sys
import os
sys.path.append('/app/backend')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

from services.fourthchki_client import get_fourthchki_client
import logging

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_car_modifications():
    """Test car modifications API"""
    try:
        print("Testing car modifications...")
        
        client = get_fourthchki_client()
        
        # Use Acura CDX 2016
        brand = "Acura"
        model = "CDX"
        year_begin = "2016"
        year_end = "2016"
        
        print(f"Testing: {brand} {model} {year_begin}-{year_end}")
        
        # Test modifications
        mods_response = client.get_car_modifications(brand, model, year_begin, year_end)
        print(f"Modifications response type: {type(mods_response)}")
        print(f"Modifications response: {mods_response}")
        
        if isinstance(mods_response, dict):
            print(f"Modifications response keys: {list(mods_response.keys())}")
            if 'error' in mods_response:
                print(f"Error: {mods_response['error']}")
            if 'modification_list' in mods_response:
                mods = mods_response['modification_list']
                print(f"Modifications type: {type(mods)}")
                print(f"Modifications: {mods}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_car_modifications()