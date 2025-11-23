"""
Unit tests for DataStore
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_store import DataStore


class TestUserOperations:
    """Tests for user CRUD operations"""

    def test_create_user(self, data_store):
        """Test creating a new user"""
        phone = "whatsapp:+15555551234"
        user = data_store.create_user(phone, "farmer")

        assert user is not None
        assert user["phone"] == phone
        assert user["type"] == "farmer"
        assert user["registered"] is False
        assert "created_at" in user

    def test_create_farm_owner(self, data_store):
        """Test creating a farm owner"""
        phone = "whatsapp:+15555555678"
        user = data_store.create_user(phone, "farm_owner")

        assert user["type"] == "farm_owner"

    def test_get_user(self, data_store):
        """Test retrieving a user"""
        phone = "whatsapp:+15555551234"
        data_store.create_user(phone, "farmer")

        user = data_store.get_user(phone)
        assert user is not None
        assert user["phone"] == phone

    def test_get_nonexistent_user(self, data_store):
        """Test retrieving a user that doesn't exist"""
        user = data_store.get_user("whatsapp:+19999999999")
        assert user is None

    def test_update_user_profile(self, data_store, sample_farmer_profile):
        """Test updating user profile"""
        phone = "whatsapp:+15555551234"
        data_store.create_user(phone, "farmer")

        success = data_store.update_user_profile(phone, sample_farmer_profile)
        assert success is True

        user = data_store.get_user(phone)
        assert user["profile"]["name"] == sample_farmer_profile["name"]
        assert user["profile"]["min_pay_rate"] == sample_farmer_profile["min_pay_rate"]

    def test_update_nonexistent_user(self, data_store, sample_farmer_profile):
        """Test updating profile of nonexistent user"""
        success = data_store.update_user_profile("whatsapp:+19999999999", sample_farmer_profile)
        assert success is False


class TestJobOperations:
    """Tests for job CRUD operations"""

    def test_create_job(self, data_store):
        """Test creating a job"""
        job_data = {
            "work_type": "Harvesting",
            "pay_rate": 18.5,
            "location": "Sacramento, CA",
            "hours": "full-time",
            "workers_needed": 5,
            "description": "Test job",
            "owner_phone": "whatsapp:+15555550001",
            "owner_name": "Test Owner",
            "farm_name": "Test Farm"
        }

        job_id = data_store.create_job(job_data)
        assert job_id is not None
        assert job_id.startswith("JOB_")

    def test_get_job(self, data_store):
        """Test retrieving a job"""
        job_data = {
            "work_type": "Harvesting",
            "pay_rate": 18.5,
            "location": "Sacramento, CA"
        }

        job_id = data_store.create_job(job_data)
        job = data_store.get_job(job_id)

        assert job is not None
        assert job["job_id"] == job_id
        assert job["work_type"] == "Harvesting"

    def test_get_open_jobs(self, populated_store):
        """Test getting all open jobs"""
        jobs = populated_store.get_open_jobs()

        assert len(jobs) == 4
        for job in jobs:
            assert job["status"] == "open"

    def test_job_default_status(self, data_store):
        """Test that new jobs default to open status"""
        job_id = data_store.create_job({"work_type": "Test"})
        job = data_store.get_job(job_id)

        assert job["status"] == "open"


class TestMatchOperations:
    """Tests for match CRUD operations"""

    def test_create_match(self, populated_store):
        """Test creating a job match"""
        jobs = populated_store.get_open_jobs()
        job_id = jobs[0]["job_id"]
        farmer_phone = "whatsapp:+15555550101"

        match_id = populated_store.create_match(job_id, farmer_phone, "pending")

        assert match_id is not None
        assert match_id.startswith("MATCH_")

    def test_get_farmer_matches(self, populated_store):
        """Test getting matches for a farmer"""
        jobs = populated_store.get_open_jobs()
        farmer_phone = "whatsapp:+15555550101"

        # Create two matches
        populated_store.create_match(jobs[0]["job_id"], farmer_phone, "pending")
        populated_store.create_match(jobs[1]["job_id"], farmer_phone, "accepted")

        matches = populated_store.get_farmer_matches(farmer_phone)

        assert len(matches) == 2

    def test_get_job_matches(self, populated_store):
        """Test getting all matches for a job"""
        jobs = populated_store.get_open_jobs()
        job_id = jobs[0]["job_id"]

        # Create matches from different farmers
        populated_store.create_match(job_id, "whatsapp:+15555550101", "pending")
        populated_store.create_match(job_id, "whatsapp:+15555550102", "pending")

        matches = populated_store.get_job_matches(job_id)

        assert len(matches) == 2


class TestConversationState:
    """Tests for conversation state management"""

    def test_set_conversation_state(self, data_store):
        """Test setting conversation state"""
        phone = "whatsapp:+15555551234"

        data_store.set_conversation_state(phone, "farmer_registration", {"step": "name"})
        retrieved = data_store.get_conversation_state(phone)

        assert retrieved is not None
        assert retrieved["state"] == "farmer_registration"
        assert retrieved["data"]["step"] == "name"

    def test_clear_conversation_state(self, data_store):
        """Test clearing conversation state"""
        phone = "whatsapp:+15555551234"

        data_store.set_conversation_state(phone, "test", {"step": "1"})
        data_store.clear_conversation_state(phone)

        retrieved = data_store.get_conversation_state(phone)
        assert retrieved is None


class TestDataPersistence:
    """Tests for data persistence"""

    def test_data_persists_after_reload(self, temp_data_dir):
        """Test that data persists after creating new DataStore instance"""
        # Create data with first instance
        store1 = DataStore(data_dir=temp_data_dir)
        phone = "whatsapp:+15555551234"
        store1.create_user(phone, "farmer")
        store1.update_user_profile(phone, {"name": "Persistent User"})

        # Create new instance and verify data
        store2 = DataStore(data_dir=temp_data_dir)
        user = store2.get_user(phone)

        assert user is not None
        assert user["profile"]["name"] == "Persistent User"
