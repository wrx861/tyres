#!/usr/bin/env python3
"""
Debug tire search API
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

def test_tire_search():
    """Test tire search API"""
    try:
        print("Testing tire search...")
        
        client = get_fourthchki_client()
        
        # Test tire search
        response = client.search_tires(
            season_list=['w'],  # winter
            width_min=185,
            width_max=185,
            height_min=60,
            height_max=60,
            diameter_min=15,
            diameter_max=15,
            page=0,
            page_size=10
        )
        
        print(f"Response type: {type(response)}")
        print(f"Response: {response}")
        
        if isinstance(response, dict):
            print(f"Response keys: {list(response.keys())}")
            if 'error' in response:
                print(f"Error: {response['error']}")
            if 'price_rest_list' in response:
                print(f"Price rest list type: {type(response['price_rest_list'])}")
                print(f"Price rest list: {response['price_rest_list']}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tire_search()