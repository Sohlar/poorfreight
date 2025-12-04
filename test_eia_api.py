"""
Test script to find correct EIA API endpoint for diesel prices
"""

import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

API_KEY = os.getenv('EIA_API_KEY')

print("=" * 60)
print("TESTING EIA API")
print("=" * 60)

# Test 1: Check if API key works by getting API root
print("\n1. Testing API root...")
url = f"https://api.eia.gov/v2/?api_key={API_KEY}"
response = requests.get(url)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ API key valid")
else:
    print(f"❌ API error: {response.text}")

# Test 2: Try petroleum route
print("\n2. Exploring petroleum route...")
url = f"https://api.eia.gov/v2/petroleum?api_key={API_KEY}"
response = requests.get(url)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if 'response' in data and 'routes' in data['response']:
        print("Available routes:")
        for route in data['response']['routes'][:10]:
            print(f"  - {route.get('id')}: {route.get('name')}")
else:
    print(f"❌ Error: {response.text[:200]}")

# Test 3: Try petroleum/pri (prices) route
print("\n3. Exploring petroleum prices route...")
url = f"https://api.eia.gov/v2/petroleum/pri?api_key={API_KEY}"
response = requests.get(url)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if 'response' in data and 'routes' in data['response']:
        print("Available price routes:")
        for route in data['response']['routes'][:10]:
            print(f"  - {route.get('id')}: {route.get('name')}")
else:
    print(f"❌ Error: {response.text[:200]}")

# Test 4: Try direct diesel endpoint (EMD_EPD2D_PTE_NUS_DPG)
print("\n4. Testing diesel price series directly...")
url = f"https://api.eia.gov/v2/petroleum/pri/gnd/data/?api_key={API_KEY}&frequency=weekly&data[0]=value&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5"
response = requests.get(url)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ Success! Got response")
    if 'response' in data and 'data' in data['response']:
        records = data['response']['data']
        print(f"Records found: {len(records)}")
        if len(records) > 0:
            print(f"Sample record: {json.dumps(records[0], indent=2)}")
    else:
        print(f"Response structure: {list(data.keys())}")
else:
    print(f"❌ Error: {response.text[:500]}")

# Test 5: Try simpler query
print("\n5. Trying simpler query...")
url = f"https://api.eia.gov/v2/petroleum/pri/gnd/data/?api_key={API_KEY}"
response = requests.get(url)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if 'response' in data:
        print("Response keys:", list(data['response'].keys()))
        if 'data' in data['response']:
            print(f"Records: {len(data['response']['data'])}")
            if len(data['response']['data']) > 0:
                print(f"First record: {data['response']['data'][0]}")
else:
    print(f"❌ Error: {response.text[:500]}")

print("\n" + "=" * 60)
