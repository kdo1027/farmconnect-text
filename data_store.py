"""
Data storage module for FarmConnect chatbot using JSON files
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class DataStore:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self.users_file = os.path.join(data_dir, 'users.json')
        self.jobs_file = os.path.join(data_dir, 'jobs.json')
        self.conversations_file = os.path.join(data_dir, 'conversations.json')
        self.matches_file = os.path.join(data_dir, 'matches.json')

        # Initialize files if they don't exist
        self._init_file(self.users_file, {})
        self._init_file(self.jobs_file, {})
        self._init_file(self.conversations_file, {})
        self._init_file(self.matches_file, {})

    def _init_file(self, filepath, default_data):
        """Initialize JSON file with default data if it doesn't exist"""
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                json.dump(default_data, f, indent=2)

    def _read_json(self, filepath):
        """Read JSON file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_json(self, filepath, data):
        """Write to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    # User Management
    def get_user(self, phone_number: str) -> Optional[Dict]:
        """Get user by phone number"""
        users = self._read_json(self.users_file)
        return users.get(phone_number)

    def create_user(self, phone_number: str, user_type: str) -> Dict:
        """Create new user (farmer or farm_owner)"""
        users = self._read_json(self.users_file)
        users[phone_number] = {
            'phone': phone_number,
            'type': user_type,
            'created_at': datetime.now().isoformat(),
            'registered': False,
            'profile': {}
        }
        self._write_json(self.users_file, users)
        return users[phone_number]

    def update_user(self, phone_number: str, updates: Dict):
        """Update user information"""
        users = self._read_json(self.users_file)
        if phone_number in users:
            users[phone_number].update(updates)
            self._write_json(self.users_file, users)

    def update_user_profile(self, phone_number: str, profile_data: Dict):
        """Update user profile"""
        users = self._read_json(self.users_file)
        if phone_number in users:
            users[phone_number]['profile'].update(profile_data)
            self._write_json(self.users_file, users)
            return True
        return False

    # Job Management
    def create_job(self, job_data: Dict) -> str:
        """Create new job posting"""
        jobs = self._read_json(self.jobs_file)
        job_id = f"JOB_{len(jobs) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        jobs[job_id] = {
            'job_id': job_id,
            'created_at': datetime.now().isoformat(),
            'status': 'open',
            **job_data
        }
        self._write_json(self.jobs_file, jobs)
        return job_id

    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        jobs = self._read_json(self.jobs_file)
        return jobs.get(job_id)

    def get_open_jobs(self) -> List[Dict]:
        """Get all open jobs"""
        jobs = self._read_json(self.jobs_file)
        return [job for job in jobs.values() if job.get('status') == 'open']

    def update_job(self, job_id: str, updates: Dict):
        """Update job information"""
        jobs = self._read_json(self.jobs_file)
        if job_id in jobs:
            jobs[job_id].update(updates)
            self._write_json(self.jobs_file, jobs)

    # Conversation State Management
    def get_conversation_state(self, phone_number: str) -> Optional[Dict]:
        """Get conversation state for user"""
        conversations = self._read_json(self.conversations_file)
        return conversations.get(phone_number)

    def set_conversation_state(self, phone_number: str, state: str, data: Dict = None):
        """Set conversation state for user"""
        conversations = self._read_json(self.conversations_file)
        conversations[phone_number] = {
            'state': state,
            'data': data or {},
            'updated_at': datetime.now().isoformat()
        }
        self._write_json(self.conversations_file, conversations)

    def clear_conversation_state(self, phone_number: str):
        """Clear conversation state"""
        conversations = self._read_json(self.conversations_file)
        if phone_number in conversations:
            del conversations[phone_number]
            self._write_json(self.conversations_file, conversations)

    # Job Matching
    def create_match(self, job_id: str, farmer_phone: str, status: str = 'pending'):
        """Create job match"""
        matches = self._read_json(self.matches_file)
        match_id = f"MATCH_{len(matches) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        matches[match_id] = {
            'match_id': match_id,
            'job_id': job_id,
            'farmer_phone': farmer_phone,
            'status': status,
            'created_at': datetime.now().isoformat()
        }
        self._write_json(self.matches_file, matches)
        return match_id

    def get_farmer_matches(self, farmer_phone: str) -> List[Dict]:
        """Get all matches for a farmer"""
        matches = self._read_json(self.matches_file)
        return [match for match in matches.values() if match['farmer_phone'] == farmer_phone]

    def get_job_matches(self, job_id: str) -> List[Dict]:
        """Get all matches for a job"""
        matches = self._read_json(self.matches_file)
        return [match for match in matches.values() if match['job_id'] == job_id]

    def update_match(self, match_id: str, updates: Dict):
        """Update match status"""
        matches = self._read_json(self.matches_file)
        if match_id in matches:
            matches[match_id].update(updates)
            self._write_json(self.matches_file, matches)
