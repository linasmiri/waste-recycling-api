import json
import urllib.request
import urllib.error
import sys

url = "http://localhost:8000/collectors/"
data = {
    "username": "testuser_auto_1",
    "full_name": "Test User Automator",
    "phone_number": "123456789",
    "password": "testpassword123"
}

headers = {'Content-Type': 'application/json'}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)

print(f"Sending POST request to {url}...")
print(f"Data: {data}")

try:
    with urllib.request.urlopen(req) as response:
        response_body = response.read().decode('utf-8')
        print(f"Response Code: {response.getcode()}")
        print(f"Response Body: {response_body}")
        print("\nSUCCESS: Registration works!")
except urllib.error.HTTPError as e:
    print(f"\nHTTP ERROR: {e.code}")
    print(e.read().decode('utf-8'))
except urllib.error.URLError as e:
    print(f"\nCONNECTION ERROR: {e.reason}")
    print("Is the backend server (window 1) running?")
except Exception as e:
    print(f"\nERROR: {e}")
