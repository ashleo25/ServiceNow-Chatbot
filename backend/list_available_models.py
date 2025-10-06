#!/usr/bin/env python3
"""
List available models in Google AI Studio
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def list_models():
    """List all available models"""
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        return
    
    print(f"🔑 Using API key: {api_key[:15]}...")
    print("📋 Listing available models...\n")
    
    # Try both API versions
    for version in ['v1', 'v1beta']:
        print(f"🔍 Checking API version: {version}")
        
        url = f"https://generativelanguage.googleapis.com/{version}/models"
        params = {'key': api_key}
        
        try:
            response = requests.get(url, params=params)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                if models:
                    print(f"✅ Found {len(models)} models in {version}:")
                    for i, model in enumerate(models[:10], 1):  # Show first 10
                        name = model.get('name', 'Unknown')
                        display_name = model.get('displayName', 'No display name')
                        supported_methods = model.get('supportedGenerationMethods', [])
                        
                        print(f"  {i}. Name: {name}")
                        print(f"     Display: {display_name}")
                        print(f"     Methods: {', '.join(supported_methods)}")
                        print()
                    
                    if len(models) > 10:
                        print(f"     ... and {len(models) - 10} more models")
                else:
                    print(f"❌ No models found in {version}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 60)

if __name__ == "__main__":
    list_models()