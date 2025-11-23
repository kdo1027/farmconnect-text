"""
Unit tests for FarmConnect Chatbot
"""
import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot import FarmConnectBot
from data_store import DataStore


class TestRuleBasedMatching:
    """Tests for rule-based job matching algorithm"""

    @pytest.fixture
    def bot_with_temp_store(self):
        """Create a bot with temporary data directory"""
        temp_dir = tempfile.mkdtemp()

        # Patch DataStore to use temp directory
        with patch.object(DataStore, '__init__', lambda self, data_dir=None: None):
            bot = FarmConnectBot()
            bot.store = DataStore.__new__(DataStore)
            bot.store.data_dir = temp_dir
            bot.store.users = {}
            bot.store.jobs = {}
            bot.store.conversations = {}
            bot.store.matches = {}
            bot.ai_matcher = None  # Disable AI matcher for rule-based tests

        yield bot
        shutil.rmtree(temp_dir)

    def test_match_by_work_type(self, bot_with_temp_store, sample_jobs, sample_farmer_profile):
        """Test matching jobs by work type preference"""
        bot = bot_with_temp_store

        # Profile prefers Harvesting, Planting
        matched = bot._rule_based_match(sample_jobs, sample_farmer_profile)

        # Should match Harvesting and Planting
        work_types = [job["work_type"] for job in matched]
        assert "Harvesting" in work_types
        assert "Planting" in work_types
        assert "Irrigation" not in work_types  # Different work type
        assert "General Labor" not in work_types  # Different work type

    def test_match_includes_all_matching_work_types(self, bot_with_temp_store, sample_jobs, sample_farmer_profile):
        """Test that all jobs matching work type preferences are included regardless of pay"""
        bot = bot_with_temp_store

        # Profile prefers Harvesting and Planting
        matched = bot._rule_based_match(sample_jobs, sample_farmer_profile)

        # Should match all Harvesting and Planting jobs regardless of pay
        work_types = [job["work_type"] for job in matched]
        assert "Harvesting" in work_types
        assert "Planting" in work_types

    def test_match_sorted_by_pay(self, bot_with_temp_store, sample_jobs, sample_farmer_profile):
        """Test that matched jobs are sorted by pay rate (highest first)"""
        bot = bot_with_temp_store

        # Modify profile to match all work types
        profile = sample_farmer_profile.copy()
        profile["work_types"] = "Harvesting, Planting, Irrigation, General Labor"

        matched = bot._rule_based_match(sample_jobs, profile)

        # Check sorting (highest pay first)
        pay_rates = [job["pay_rate"] for job in matched]
        assert pay_rates == sorted(pay_rates, reverse=True)

    def test_match_with_no_preferences(self, bot_with_temp_store, sample_jobs):
        """Test matching with empty preferences returns all jobs"""
        bot = bot_with_temp_store

        profile = {
            "work_types": "",  # No preference
        }

        matched = bot._rule_based_match(sample_jobs, profile)

        # Should return all jobs since no work type filter
        assert len(matched) == 4

    def test_match_returns_top_5_only(self, bot_with_temp_store, sample_jobs, sample_farmer_profile):
        """Test that matching returns top 5 jobs only"""
        bot = bot_with_temp_store

        # Create more than 5 matching jobs by allowing all types
        profile = sample_farmer_profile.copy()
        profile["work_types"] = "All types of work"

        matched = bot._rule_based_match(sample_jobs, profile)

        # Should return at most 5 jobs
        assert len(matched) <= 5

    def test_match_v2_per_day_payment(self, bot_with_temp_store, sample_jobs_v2):
        """Test matching with per-day payment format"""
        bot = bot_with_temp_store

        profile = {
            "work_types": "Tomato Harvest, Weeding"
        }

        matched = bot._rule_based_match(sample_jobs_v2, profile)

        # Both should match based on work type
        assert len(matched) == 2

    def test_match_v2_matches_by_work_type_only(self, bot_with_temp_store, sample_jobs_v2):
        """Test that jobs are matched by work type regardless of pay rate"""
        bot = bot_with_temp_store

        profile = {
            "work_types": "Tomato Harvest",
        }

        matched = bot._rule_based_match(sample_jobs_v2, profile)

        # Should match Tomato Harvest job regardless of pay
        job_ids = [job.get("job_id") for job in matched]
        assert "JOB_V2_001" in job_ids

        # Should not match Weeding (different work type)
        assert "JOB_V2_002" not in job_ids

    def test_partial_work_type_match(self, bot_with_temp_store, sample_jobs):
        """Test partial keyword matching for work types"""
        bot = bot_with_temp_store

        profile = {
            "work_types": "harvest",  # Lowercase, partial match
        }

        matched = bot._rule_based_match(sample_jobs, profile)

        # Should match "Harvesting"
        work_types = [job["work_type"] for job in matched]
        assert "Harvesting" in work_types


class TestAIMatcherIntegration:
    """Tests for AI matcher integration with chatbot"""

    @pytest.fixture
    def bot_with_mock_ai(self):
        """Create a bot with mocked AI matcher"""
        temp_dir = tempfile.mkdtemp()

        with patch.object(DataStore, '__init__', lambda self, data_dir=None: None):
            bot = FarmConnectBot()
            bot.store = DataStore.__new__(DataStore)
            bot.store.data_dir = temp_dir
            bot.store.users = {}
            bot.store.jobs = {}
            bot.store.conversations = {}
            bot.store.matches = {}

            # Mock AI matcher
            bot.ai_matcher = MagicMock()

        yield bot
        shutil.rmtree(temp_dir)

    def test_uses_ai_matcher_when_available(self, bot_with_mock_ai, sample_jobs, sample_farmer_profile):
        """Test that AI matcher is used when available"""
        bot = bot_with_mock_ai

        # Setup mock to return specific results
        ai_results = [sample_jobs[0].copy()]
        ai_results[0]["_ai_score"] = 95
        bot.ai_matcher.match_jobs.return_value = ai_results

        result = bot.match_jobs(sample_jobs, sample_farmer_profile)

        bot.ai_matcher.match_jobs.assert_called_once()
        assert len(result) == 1
        assert result[0]["_ai_score"] == 95

    def test_falls_back_on_ai_error(self, bot_with_mock_ai, sample_jobs, sample_farmer_profile):
        """Test fallback to rule-based when AI fails"""
        bot = bot_with_mock_ai

        # Make AI matcher raise an exception
        bot.ai_matcher.match_jobs.side_effect = Exception("API Error")

        result = bot.match_jobs(sample_jobs, sample_farmer_profile)

        # Should fall back to rule-based matching
        assert len(result) > 0
        assert "_ai_score" not in result[0]

    def test_falls_back_on_ai_none_result(self, bot_with_mock_ai, sample_jobs, sample_farmer_profile):
        """Test fallback to rule-based when AI returns None"""
        bot = bot_with_mock_ai

        bot.ai_matcher.match_jobs.return_value = None

        result = bot.match_jobs(sample_jobs, sample_farmer_profile)

        # Should fall back to rule-based matching
        assert len(result) > 0


class TestFarmerRegistration:
    """Tests for farmer registration flow"""

    @pytest.fixture
    def bot(self, temp_data_dir):
        """Create a bot with temporary data directory"""
        with patch('chatbot.DataStore') as MockStore:
            store_instance = DataStore(data_dir=temp_data_dir)
            MockStore.return_value = store_instance

            with patch('chatbot.get_ai_matcher', return_value=None):
                bot = FarmConnectBot()
                bot.store = store_instance

        return bot

    def test_new_user_sees_welcome(self, bot):
        """Test that new users see welcome menu"""
        phone = "whatsapp:+15555559999"
        response = bot.handle_message(phone, "Hi")

        assert "Welcome to FarmConnect" in response
        assert ("1️⃣" in response or "1." in response)  # Has menu options

    def test_farmer_registration_starts(self, bot):
        """Test farmer registration flow starts correctly"""
        phone = "whatsapp:+15555559999"

        # First message - welcome
        bot.handle_message(phone, "Hi")

        # Select farmer role
        response = bot.handle_message(phone, "1")

        assert "name" in response.lower()

    def test_farmer_name_step(self, bot):
        """Test name entry step"""
        phone = "whatsapp:+15555559999"

        bot.handle_message(phone, "Hi")
        bot.handle_message(phone, "1")  # Select farmer
        response = bot.handle_message(phone, "John Doe")

        assert "location" in response.lower() or "city" in response.lower()


class TestFarmOwnerRegistration:
    """Tests for farm owner registration flow"""

    @pytest.fixture
    def bot(self, temp_data_dir):
        """Create a bot with temporary data directory"""
        with patch('chatbot.DataStore') as MockStore:
            store_instance = DataStore(data_dir=temp_data_dir)
            MockStore.return_value = store_instance

            with patch('chatbot.get_ai_matcher', return_value=None):
                bot = FarmConnectBot()
                bot.store = store_instance

        return bot

    def test_farm_owner_registration_starts(self, bot):
        """Test farm owner registration flow starts correctly"""
        phone = "whatsapp:+15555558888"

        # First message - welcome
        bot.handle_message(phone, "Hi")

        # Select farm owner role
        response = bot.handle_message(phone, "2")

        assert "name" in response.lower()


class TestMenuHandling:
    """Tests for menu commands"""

    @pytest.fixture
    def bot(self, temp_data_dir):
        """Create a bot with temporary data directory"""
        with patch('chatbot.DataStore') as MockStore:
            store_instance = DataStore(data_dir=temp_data_dir)
            MockStore.return_value = store_instance

            with patch('chatbot.get_ai_matcher', return_value=None):
                bot = FarmConnectBot()
                bot.store = store_instance

        return bot

    def test_menu_command_shows_welcome_for_new_user(self, bot):
        """Test that menu command shows welcome for unregistered user"""
        phone = "whatsapp:+15555557777"
        response = bot.handle_message(phone, "menu")

        assert "Welcome" in response


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_empty_message(self, temp_data_dir):
        """Test handling empty message"""
        with patch('chatbot.DataStore') as MockStore:
            store_instance = DataStore(data_dir=temp_data_dir)
            MockStore.return_value = store_instance

            with patch('chatbot.get_ai_matcher', return_value=None):
                bot = FarmConnectBot()
                bot.store = store_instance

        phone = "whatsapp:+15555556666"
        response = bot.handle_message(phone, "")

        # Should not crash, should return some response
        assert response is not None
        assert len(response) > 0

    def test_very_long_message(self, temp_data_dir):
        """Test handling very long message"""
        with patch('chatbot.DataStore') as MockStore:
            store_instance = DataStore(data_dir=temp_data_dir)
            MockStore.return_value = store_instance

            with patch('chatbot.get_ai_matcher', return_value=None):
                bot = FarmConnectBot()
                bot.store = store_instance

        phone = "whatsapp:+15555555555"
        long_message = "a" * 1000
        response = bot.handle_message(phone, long_message)

        # Should not crash
        assert response is not None
