#!/usr/bin/env python3
"""
Debug car years API
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

def test_car_years():
    """Test car years API"""
    try:
        print("Testing car years...")
        
        client = get_fourthchki_client()
        
        # First get brands
        brands_response = client.get_car_brands()
        brands = brands_response.get('marka_list', {})
        if isinstance(brands, dict) and 'string' in brands:
            brands = brands['string']
        
        print(f"First brand: {brands[0]}")
        
        # Get models for first brand
        models_response = client.get_car_models(brands[0])
        models = models_response.get('model_list', {})
        if isinstance(models, dict) and 'string' in models:
            models = models['string']
        
        print(f"First model: {models[0]}")
        
        # Test years
        years_response = client.get_car_years(brands[0], models[0])
        print(f"Years response type: {type(years_response)}")
        print(f"Years response: {years_response}")
        
        if isinstance(years_response, dict):
            print(f"Years response keys: {list(years_response.keys())}")
            if 'error' in years_response:
                print(f"Error: {years_response['error']}")
            if 'year_list' in years_response:
                years = years_response['year_list']
                print(f"Years type: {type(years)}")
                print(f"Years: {years}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_car_years()