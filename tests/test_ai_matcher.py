"""
Unit tests for AI Matcher
"""
import pytest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_matcher import AIJobMatcher, get_ai_matcher


class TestAIJobMatcherInitialization:
    """Tests for AI matcher initialization"""

    def test_missing_api_key_raises_error(self):
        """Test that missing API key raises ValueError"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=False):
            with pytest.raises(ValueError, match="GEMINI_API_KEY not configured"):
                AIJobMatcher()

    def test_placeholder_api_key_raises_error(self):
        """Test that placeholder API key raises ValueError"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "your_gemini_api_key_here"}, clear=False):
            with pytest.raises(ValueError, match="GEMINI_API_KEY not configured"):
                AIJobMatcher()

    def test_get_ai_matcher_returns_none_on_error(self):
        """Test that get_ai_matcher returns None when API key is invalid"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=False):
            matcher = get_ai_matcher()
            assert matcher is None


class TestPromptBuilding:
    """Tests for prompt building logic"""

    @patch('ai_matcher.genai')
    def test_prompt_includes_farmer_info(self, mock_genai):
        """Test that prompt includes farmer profile information"""
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock()

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}, clear=False):
            matcher = AIJobMatcher()

            farmer_profile = {
                "name": "Test Farmer",
                "location": "Sacramento, CA",
                "work_types": "Harvesting",
                "min_pay_rate": 15.0,
                "max_distance": 25,
                "hours_preference": "full-time"
            }

            jobs = [{"job_id": "TEST_001", "work_type": "Harvesting", "pay_rate": 18.0}]

            prompt = matcher._build_matching_prompt(jobs, farmer_profile)

            assert "Test Farmer" in prompt
            assert "Sacramento, CA" in prompt
            assert "Harvesting" in prompt
            assert "$15.0" in prompt

    @patch('ai_matcher.genai')
    def test_prompt_includes_job_info(self, mock_genai):
        """Test that prompt includes job information"""
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock()

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}, clear=False):
            matcher = AIJobMatcher()

            farmer_profile = {"name": "Test", "min_pay_rate": 10.0}
            jobs = [
                {
                    "job_id": "TEST_001",
                    "work_type": "Harvesting",
                    "pay_rate": 18.0,
                    "farm_name": "Test Farm",
                    "location": "Sacramento, CA"
                }
            ]

            prompt = matcher._build_matching_prompt(jobs, farmer_profile)

            assert "TEST_001" in prompt
            assert "Harvesting" in prompt
            assert "Test Farm" in prompt
            assert "$18.0" in prompt


class TestResponseParsing:
    """Tests for AI response parsing"""

    @patch('ai_matcher.genai')
    def test_parse_valid_json_response(self, mock_genai):
        """Test parsing valid JSON response"""
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock()

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}, clear=False):
            matcher = AIJobMatcher()

            jobs = [
                {"job_id": "JOB_001", "work_type": "Harvesting"},
                {"job_id": "JOB_002", "work_type": "Planting"}
            ]

            response_text = '[{"job_index": 0, "score": 85, "reason": "Good match"}, {"job_index": 1, "score": 70, "reason": "Okay match"}]'

            result = matcher._parse_response(response_text, jobs)

            assert len(result) == 2
            assert result[0]["_ai_score"] == 85
            assert result[0]["job_id"] == "JOB_001"
            assert result[1]["_ai_score"] == 70

    @patch('ai_matcher.genai')
    def test_parse_markdown_wrapped_json(self, mock_genai):
        """Test parsing JSON wrapped in markdown code blocks"""
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock()

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}, clear=False):
            matcher = AIJobMatcher()

            jobs = [{"job_id": "JOB_001", "work_type": "Harvesting"}]

            response_text = '```json\n[{"job_index": 0, "score": 90, "reason": "Excellent"}]\n```'

            result = matcher._parse_response(response_text, jobs)

            assert len(result) == 1
            assert result[0]["_ai_score"] == 90

    @patch('ai_matcher.genai')
    def test_parse_empty_response(self, mock_genai):
        """Test parsing empty array response"""
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock()

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}, clear=False):
            matcher = AIJobMatcher()

            jobs = [{"job_id": "JOB_001", "work_type": "Harvesting"}]
            response_text = "[]"

            result = matcher._parse_response(response_text, jobs)

            assert result == []

    @patch('ai_matcher.genai')
    def test_parse_invalid_json_returns_none(self, mock_genai):
        """Test that invalid JSON returns None"""
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock()

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}, clear=False):
            matcher = AIJobMatcher()

            jobs = [{"job_id": "JOB_001"}]
            response_text = "invalid json"

            result = matcher._parse_response(response_text, jobs)

            assert result is None

    @patch('ai_matcher.genai')
    def test_results_sorted_by_score(self, mock_genai):
        """Test that results are sorted by score descending"""
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock()

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}, clear=False):
            matcher = AIJobMatcher()

            jobs = [
                {"job_id": "JOB_001"},
                {"job_id": "JOB_002"},
                {"job_id": "JOB_003"}
            ]

            # Response with scores in non-sorted order
            response_text = '[{"job_index": 0, "score": 50, "reason": ""}, {"job_index": 1, "score": 90, "reason": ""}, {"job_index": 2, "score": 70, "reason": ""}]'

            result = matcher._parse_response(response_text, jobs)

            assert result[0]["_ai_score"] == 90
            assert result[1]["_ai_score"] == 70
            assert result[2]["_ai_score"] == 50


class TestMatchJobs:
    """Tests for the main match_jobs method"""

    @patch('ai_matcher.genai')
    def test_empty_jobs_returns_empty(self, mock_genai):
        """Test that empty job list returns empty result"""
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock()

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}, clear=False):
            matcher = AIJobMatcher()

            result = matcher.match_jobs([], {"name": "Test"})

            assert result == []

    @patch('ai_matcher.genai')
    def test_api_error_returns_none(self, mock_genai):
        """Test that API error returns None for fallback"""
        mock_genai.configure = MagicMock()
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}, clear=False):
            matcher = AIJobMatcher()

            jobs = [{"job_id": "JOB_001", "work_type": "Test"}]
            result = matcher.match_jobs(jobs, {"name": "Test"})

            assert result is None


class TestPaymentTypeHandling:
    """Tests for different payment type handling in prompts"""

    @patch('ai_matcher.genai')
    def test_per_day_payment_calculation(self, mock_genai):
        """Test per day payment is converted to hourly"""
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock()

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}, clear=False):
            matcher = AIJobMatcher()

            jobs = [{
                "job_id": "JOB_001",
                "work_type": "Harvesting",
                "payment_type": "per day",
                "payment_amount": 160.0  # Should be $20/hr
            }]

            prompt = matcher._build_matching_prompt(jobs, {"name": "Test"})

            assert "$160" in prompt or "160" in prompt
            assert "20.00" in prompt  # Effective hourly rate

    @patch('ai_matcher.genai')
    def test_per_hour_payment(self, mock_genai):
        """Test per hour payment is shown directly"""
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock()

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}, clear=False):
            matcher = AIJobMatcher()

            jobs = [{
                "job_id": "JOB_001",
                "work_type": "Harvesting",
                "payment_type": "per hour",
                "payment_amount": 18.0
            }]

            prompt = matcher._build_matching_prompt(jobs, {"name": "Test"})

            assert "$18" in prompt
