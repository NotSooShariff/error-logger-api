import os
import pytest
import httpx
from fastapi import status
from datetime import datetime, timedelta
from pytz import timezone
from dotenv import load_dotenv

load_dotenv()

# If deploying, change this to your production domain
BASE_URL = "http://127.0.0.1:8000"

# If you changed your credentials in the API, Be sure to change it here too for testing
USERNAME = "admin"
PASSWORD = "password"

IST = timezone('Asia/Kolkata')

# Utility functions
def get_basic_auth_headers(username: str, password: str):
    return httpx.BasicAuth(username, password)

def get_current_time_in_ist():
    return datetime.now(IST)

def get_start_of_day_in_ist():
    now = get_current_time_in_ist()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)

# Sample log data - Change it up to your liking
sample_log = {
    "project_source": "TestProject",
    "timestamp": get_current_time_in_ist().isoformat(),
    "error_message": "Sample error message",
    "additional_info": "Additional info"
}

@pytest.fixture
def client():
    return httpx.Client(base_url=BASE_URL, auth=get_basic_auth_headers(USERNAME, PASSWORD))

# I only added basic tests, Ik these need to be more comprehensive
# Test POST /log
def test_post_log(client):
    response = client.post("/log", json=sample_log)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"

# Test GET /logs
def test_get_logs():
    response = httpx.get(f"{BASE_URL}/logs")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

# Test GET /current
def test_get_current_logs():
    response = httpx.get(f"{BASE_URL}/current")
    assert response.status_code == status.HTTP_200_OK
    logs = response.json()
    assert isinstance(logs, list)
    if logs:
        for log in logs:
            assert datetime.fromisoformat(log["timestamp"]).astimezone(IST) >= get_start_of_day_in_ist()

# Test GET /analytics
def test_get_analytics():
    response = httpx.get(f"{BASE_URL}/analytics")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

# Test authentication failure for POST /log
def test_post_log_authentication_failure():
    response = httpx.post(f"{BASE_URL}/log", json=sample_log, auth=get_basic_auth_headers("wrong_user", "wrong_pass"))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def print_test_results():
    tests = [
        ("test_post_log", test_post_log),
        ("test_get_logs", test_get_logs),
        ("test_get_current_logs", test_get_current_logs),
        ("test_get_analytics", test_get_analytics),
        ("test_post_log_authentication_failure", test_post_log_authentication_failure)
    ]
    
    print("\nTest Results:")
    for name, test in tests:
        try:
            if "post_log" in name:
                if name == "test_post_log_authentication_failure":
                    test()  
                else:
                    test(httpx.Client(base_url=BASE_URL, auth=get_basic_auth_headers(USERNAME, PASSWORD)))
            else:
                test()
            print(f"✅ {name}")
        except AssertionError:
            print(f"❌ {name}")

if __name__ == "__main__":
    print_test_results()
