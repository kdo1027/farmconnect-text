"""
AI-based job matching using Google Gemini
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AIJobMatcher:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            raise ValueError("GEMINI_API_KEY not configured in .env file")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def match_jobs(self, jobs: list, farmer_profile: dict) -> list:
        """
        Use Gemini to match jobs with farmer preferences.
        Returns jobs sorted by match score (best matches first).
        """
        if not jobs:
            return []

        # Prepare the prompt
        prompt = self._build_matching_prompt(jobs, farmer_profile)

        try:
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text, jobs)
            return result
        except Exception as e:
            print(f"AI matching error: {e}")
            # Return empty list on error - caller should fallback to rule-based
            return None

    def _build_matching_prompt(self, jobs: list, farmer_profile: dict) -> str:
        """Build the prompt for Gemini to analyze job matches."""

        # Format farmer preferences
        farmer_info = f"""
FARMER PROFILE:
- Name: {farmer_profile.get('name', 'Unknown')}
- Location: {farmer_profile.get('location', 'Unknown')}
- Preferred work types: {farmer_profile.get('work_types', 'Any')}
- Minimum pay rate: ${farmer_profile.get('min_pay_rate', 0)}/hour
- Maximum travel distance: {farmer_profile.get('max_distance', 'Any')} miles
- Hours preference: {farmer_profile.get('hours_preference', 'Any')}
"""

        # Format jobs
        jobs_info = "AVAILABLE JOBS:\n"
        for i, job in enumerate(jobs):
            # Calculate effective hourly rate
            if job.get('payment_type') == 'per day':
                effective_rate = job.get('payment_amount', 0) / 8
                pay_display = f"${job.get('payment_amount', 0)}/day (${effective_rate:.2f}/hr effective)"
            elif job.get('payment_type') == 'per hour':
                effective_rate = job.get('payment_amount', 0)
                pay_display = f"${effective_rate}/hour"
            elif job.get('payment_type') == 'per task':
                effective_rate = job.get('payment_amount', 0)
                pay_display = f"${effective_rate}/task (piece rate)"
            else:
                effective_rate = job.get('pay_rate', 0)
                pay_display = f"${effective_rate}/hour"

            jobs_info += f"""
Job {i + 1} (ID: {job.get('job_id', i)}):
- Farm: {job.get('farm_name', 'Unknown')}
- Work Type: {job.get('work_type', 'General')}
- Pay: {pay_display}
- Location: {job.get('location', 'Unknown')}
- Schedule: {job.get('hours', 'Not specified')}
- Workers Needed: {job.get('workers_needed', 1)}
- Description: {job.get('description', 'No description')}
- Transportation: {job.get('transportation', 'Not specified')}
"""

        prompt = f"""You are a job matching assistant for agricultural workers. Analyze the farmer's profile and available jobs to find the best matches.

{farmer_info}

{jobs_info}

TASK: Score each job from 0-100 based on how well it matches the farmer's preferences. Consider:
1. Pay rate vs minimum required (must meet minimum to be considered)
2. Work type alignment with preferences
3. Location/distance considerations
4. Schedule compatibility
5. Overall job quality and fit

IMPORTANT RULES:
- Jobs that don't meet the minimum pay rate should score 0
- Exact work type matches score higher than related types
- Consider semantic similarity (e.g., "Tomato Harvest" matches "Harvesting")
- **Hours preference interpretation:**
  - "full-time": Worker wants 40+ hours/week only
  - "part-time": Worker wants 20-40 hours/week only
  - "flexible": Worker is OPEN TO BOTH full-time AND part-time jobs (matches all schedules)

Return ONLY a JSON array with job matches, sorted by score (highest first). Format:
[
  {{"job_index": 0, "score": 85, "reason": "Brief explanation"}},
  {{"job_index": 2, "score": 72, "reason": "Brief explanation"}}
]

Only include jobs with score > 0. Return empty array [] if no jobs match.
"""
        return prompt

    def _parse_response(self, response_text: str, jobs: list) -> list:
        """Parse Gemini's response and return matched jobs."""
        try:
            # Extract JSON from response (handle markdown code blocks)
            text = response_text.strip()
            if text.startswith('```'):
                # Remove markdown code block
                lines = text.split('\n')
                text = '\n'.join(lines[1:-1])

            matches = json.loads(text)

            # Convert to list of jobs sorted by score
            matched_jobs = []
            for match in matches:
                job_index = match.get('job_index', 0)
                if 0 <= job_index < len(jobs):
                    job = jobs[job_index].copy()
                    job['_ai_score'] = match.get('score', 0)
                    job['_ai_reason'] = match.get('reason', '')
                    matched_jobs.append(job)

            # Sort by score (highest first)
            matched_jobs.sort(key=lambda x: x.get('_ai_score', 0), reverse=True)
            return matched_jobs

        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response: {e}")
            print(f"Response was: {response_text}")
            return None


def get_ai_matcher():
    """Factory function to get AI matcher instance."""
    try:
        return AIJobMatcher()
    except ValueError as e:
        print(f"AI Matcher not available: {e}")
        return None
