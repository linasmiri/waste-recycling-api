import urllib.request
import urllib.error
import json

URL = "http://localhost:8000/admin/collectors"

def test_admin_endpoint():
    print(f"Testing {URL}...")
    try:
        req = urllib.request.Request(URL)
        # We are not sending a token, so we expect 401 Unauthorized
        with urllib.request.urlopen(req) as response:
            print(f"Response: {response.getcode()}")
            print(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Exepcted HTTP authentication error: {e.code}")
        print(e.read().decode())
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_admin_endpoint()
