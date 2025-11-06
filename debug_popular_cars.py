#!/usr/bin/env python3
"""
Debug popular car modifications
"""

import sys
import os
sys.path.append('/app/backend')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

from services.fourthchki_client import get_fourthchki_client
import logging

def test_popular_cars():
    """Test modifications for popular cars"""
    try:
        client = get_fourthchki_client()
        
        # Test popular car combinations
        test_cars = [
            ("Toyota", "Camry", "2020"),
            ("BMW", "3 Series", "2019"),
            ("Mercedes-Benz", "C-Class", "2018"),
            ("Volkswagen", "Golf", "2017"),
            ("Ford", "Focus", "2016"),
            ("LADA (ВАЗ)", "Granta", "2020"),
        ]
        
        for brand, model, year in test_cars:
            print(f"\nTesting: {brand} {model} {year}")
            
            try:
                # Check if model exists
                models_response = client.get_car_models(brand)
                models = models_response.get('model_list', {})
                if isinstance(models, dict) and 'string' in models:
                    models = models['string']
                
                if model not in models:
                    print(f"  Model {model} not found for {brand}")
                    continue
                
                # Get modifications
                mods_response = client.get_car_modifications(brand, model, year, year)
                modifications = mods_response.get('modification_list')
                
                if modifications is None:
                    print(f"  No modifications (None)")
                elif isinstance(modifications, list):
                    print(f"  Found {len(modifications)} modifications: {modifications[:2]}")
                elif isinstance(modifications, dict):
                    print(f"  Modifications dict: {modifications}")
                else:
                    print(f"  Modifications type: {type(modifications)}")
                    
            except Exception as e:
                print(f"  Error: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_popular_cars()