import requests
import json
import time
import sys

def test_server_connection():
    print("Testing connection to server...")
    try:
        response = requests.get("http://localhost:8080/tools")
        print("✓ Server is running and responding")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure it's running on port 8080")
        return False

def test_put(key: str, value: str):
    print(f"\nTesting PUT {key}={value}")
    try:
        response = requests.post(
            "http://localhost:8080/tools/kvstore_put",
            json={"key": key, "value": value}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False

def test_get(key: str):
    print(f"\nTesting GET {key}")
    try:
        response = requests.post(
            "http://localhost:8080/tools/kvstore_get",
            json={"key": key}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False

def main():
    print("KVStore Test Client")
    print("==================")
    
    # First check if server is running
    if not test_server_connection():
        sys.exit(1)
    
    # Test basic put/get
    test_put("test1", "value1")
    test_get("test1")
    
    # Test non-existent key
    test_get("nonexistent")
    
    # Test multiple puts
    test_put("test2", "value2")
    test_put("test3", "value3")
    test_get("test2")
    test_get("test3")

if __name__ == "__main__":
    main() 