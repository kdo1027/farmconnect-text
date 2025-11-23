"""
Pytest fixtures for FarmConnect tests
"""
import pytest
import os
import sys
import json
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_store import DataStore
from chatbot import FarmConnectBot


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def data_store(temp_data_dir):
    """Create a DataStore with temporary directory"""
    store = DataStore(data_dir=temp_data_dir)
    return store


@pytest.fixture
def sample_farmer_profile():
    """Sample farmer profile for testing"""
    return {
        "name": "Test Farmer",
        "location": "Sacramento, CA",
        "id_verified": True,
        "id_photo_url": "https://example.com/id.jpg",
        "work_types": "Harvesting, Planting",
        "min_pay_rate": 15.0,
        "max_distance": 25,
        "hours_preference": "full-time"
    }


@pytest.fixture
def sample_jobs():
    """Sample job listings for testing"""
    return [
        {
            "job_id": "JOB_TEST_001",
            "work_type": "Harvesting",
            "pay_rate": 18.5,
            "location": "Sacramento, CA",
            "hours": "full-time",
            "workers_needed": 5,
            "description": "Harvest tomatoes",
            "owner_phone": "whatsapp:+15555550001",
            "owner_name": "Test Owner",
            "farm_name": "Test Farm",
            "status": "open"
        },
        {
            "job_id": "JOB_TEST_002",
            "work_type": "Planting",
            "pay_rate": 16.0,
            "location": "Davis, CA",
            "hours": "part-time",
            "workers_needed": 3,
            "description": "Plant seedlings",
            "owner_phone": "whatsapp:+15555550001",
            "owner_name": "Test Owner",
            "farm_name": "Test Farm",
            "status": "open"
        },
        {
            "job_id": "JOB_TEST_003",
            "work_type": "Irrigation",
            "pay_rate": 22.0,
            "location": "Woodland, CA",
            "hours": "full-time",
            "workers_needed": 1,
            "description": "Manage irrigation systems",
            "owner_phone": "whatsapp:+15555550002",
            "owner_name": "Another Owner",
            "farm_name": "Another Farm",
            "status": "open"
        },
        {
            "job_id": "JOB_TEST_004",
            "work_type": "General Labor",
            "pay_rate": 14.0,  # Below min_pay_rate of 15
            "location": "Sacramento, CA",
            "hours": "full-time",
            "workers_needed": 2,
            "description": "General farm tasks",
            "owner_phone": "whatsapp:+15555550001",
            "owner_name": "Test Owner",
            "farm_name": "Test Farm",
            "status": "open"
        }
    ]


@pytest.fixture
def sample_jobs_v2():
    """Sample jobs with new payment format"""
    return [
        {
            "job_id": "JOB_V2_001",
            "work_type": "Tomato Harvest",
            "payment_type": "per day",
            "payment_amount": 150.0,
            "location": "Sacramento, CA",
            "hours": "full-time",
            "workers_needed": 5,
            "description": "Pick ripe tomatoes",
            "owner_phone": "whatsapp:+15555550001",
            "owner_name": "Test Owner",
            "farm_name": "Test Farm",
            "status": "open"
        },
        {
            "job_id": "JOB_V2_002",
            "work_type": "Weeding",
            "payment_type": "per hour",
            "payment_amount": 20.0,
            "location": "Davis, CA",
            "hours": "part-time",
            "workers_needed": 4,
            "description": "Remove weeds",
            "owner_phone": "whatsapp:+15555550001",
            "owner_name": "Test Owner",
            "farm_name": "Test Farm",
            "status": "open"
        }
    ]


@pytest.fixture
def populated_store(data_store, sample_jobs):
    """DataStore with sample data loaded"""
    # Create farm owner
    data_store.create_user("whatsapp:+15555550001", "farm_owner")
    data_store.update_user_profile("whatsapp:+15555550001", {
        "name": "Test Owner",
        "farm_name": "Test Farm",
        "location": "Sacramento, CA"
    })
    data_store.get_user("whatsapp:+15555550001")['registered'] = True

    # Create farmer
    data_store.create_user("whatsapp:+15555550101", "farmer")
    data_store.update_user_profile("whatsapp:+15555550101", {
        "name": "Test Farmer",
        "location": "Sacramento, CA",
        "id_verified": True,
        "work_types": "Harvesting, Planting",
        "min_pay_rate": 15.0,
        "max_distance": 25,
        "hours_preference": "full-time"
    })
    data_store.get_user("whatsapp:+15555550101")['registered'] = True

    # Create jobs
    for job in sample_jobs:
        data_store.create_job(job)

    return data_store
