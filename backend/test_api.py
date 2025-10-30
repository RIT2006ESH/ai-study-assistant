import requests
import json

BASE_URL = "http://localhost:8000"

print("🧪 Testing AI Study Assistant API\n")

# Test 1: Health check
print("1. Testing health endpoint...")
response = requests.get(f"{BASE_URL}/health")
if response.status_code == 200:
    print("✅ Health check passed")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"❌ Health check failed: {response.status_code}")

print("\n" + "="*50 + "\n")

# Test 2: Root endpoint
print("2. Testing root endpoint...")
response = requests.get(f"{BASE_URL}/")
if response.status_code == 200:
    print("✅ Root endpoint passed")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"❌ Root endpoint failed: {response.status_code}")

print("\n" + "="*50 + "\n")

# Test 3: Register a test user
print("3. Testing user registration...")
user_data = {
    "email": "testuser@example.com",
    "username": "testuser123",
    "password": "TestPass123!",
    "full_name": "Test User"
}

response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
if response.status_code == 200:
    print("✅ User registration passed")
    print(json.dumps(response.json(), indent=2))
elif response.status_code == 400 and "already exists" in response.text:
    print("⚠️  User already exists (this is okay)")
else:
    print(f"❌ Registration failed: {response.status_code}")
    print(response.text)

print("\n" + "="*50 + "\n")

# Test 4: Login
print("4. Testing login...")
login_data = {
    "username": "testuser123",
    "password": "TestPass123!"
}

response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
if response.status_code == 200:
    print("✅ Login passed")
    token = response.json().get("access_token")
    print(f"Token received: {token[:50]}...")
else:
    print(f"❌ Login failed: {response.status_code}")
    print(response.text)

print("\n✅ Basic API tests complete!")
