# FarmConnect Testing Guide

This guide covers both **automated testing** (unit/integration tests) and **manual testing** (WhatsApp interaction).

---

## Automated Testing

### Running the Test Suite

The project includes a comprehensive test suite with 51 tests covering all major functionality.

#### Quick Start
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov

# Run specific test file
pytest tests/test_chatbot.py
pytest tests/test_data_store.py
pytest tests/test_ai_matcher.py
```

### Test Coverage

| Test Suite | Tests | Coverage |
|------------|-------|----------|
| **test_ai_matcher.py** | 14 tests | AI matching, Gemini integration, prompt building, response parsing |
| **test_chatbot.py** | 24 tests | Rule-based matching, AI integration, registration flows, menu handling |
| **test_data_store.py** | 10 tests | User operations, job CRUD, matches, conversation state, data persistence |
| **test_bot_integration.py** | 1 test | End-to-end conversation flow |

**Total**: 49 tests with automatic CI/CD ready setup

### Running Individual Test Classes

```bash
# Test AI matcher initialization
pytest tests/test_ai_matcher.py::TestAIJobMatcherInitialization -v

# Test rule-based matching
pytest tests/test_chatbot.py::TestRuleBasedMatching -v

# Test data persistence
pytest tests/test_data_store.py::TestDataPersistence -v
```

### Testing AI Matching

To test AI matching functionality:

```bash
python test_ai_matching.py
```

---

## Manual Testing via WhatsApp

### Quick Setup for Manual Testing

#### Step 1: Create Sample Jobs
```bash
python sample_data/create_sample_jobs.py
```

This creates sample job postings with different work types and pay rates.

#### Step 2: Start the Bot
```bash
python reply_whatsapp.py
```

#### Step 3: Expose with ngrok (in a new terminal)
```bash
ngrok http 3000
```

#### Step 4: Configure Twilio Webhook
1. Copy your ngrok URL (e.g., `https://abc123.ngrok-free.app`)
2. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
3. Under "Sandbox Configuration"
4. Set "When a message comes in" to: `https://YOUR_NGROK_URL/reply_whatsapp`
5. Click Save

---

## Manual Testing Scenarios

### Test Scenario 1: New Farmer Registration

Follow these exact steps on WhatsApp:

#### 1. Start Conversation
**You send:** Any message (e.g., "Hi" or "Hello")

**Bot responds:**
```
🌾 Welcome to FarmConnect! 🌾

We connect agricultural workers with farm employers.

Please select your role:
1️⃣ I'm looking for farm work (Farmer/Laborer)
2️⃣ I'm hiring workers (Farm Owner)

Reply with 1 or 2
```

#### 2. Select Farmer Role
**You send:** `1`

**Bot responds:**
```
✅ Great! Let's get you registered.

📝 Step 1 of 3: Personal Information

What's your full name?
```

#### 3. Enter Your Name
**You send:** `John Smith` (or any name)

**Bot responds:**
```
Nice to meet you, John Smith! 👋

📍 Step 2 of 3: Location

What's your location? (City or area where you're looking for work)
```

#### 4. Enter Location
**You send:** `Sacramento, CA`

**Bot responds:**
```
📸 Step 3 of 3: ID Verification

Please upload a photo of your ID card or driver's license.

This helps us keep FarmConnect safe for everyone.
```

#### 5. Upload ID Photo
**You send:** Take/upload any photo from your phone

**Bot responds:**
```
✅ ID received! Thank you.

Now let's set up your job preferences to find the best matches.

🛠 Work Type Preferences
What type of farm work are you interested in? (Select all that apply)

1️⃣ Harvesting
2️⃣ Planting
3️⃣ Irrigation
4️⃣ Livestock care
5️⃣ General labor
6️⃣ All types of work

Reply with numbers separated by commas (e.g., 1,2,3) or just one number:
```

#### 6. Set Work Type Preference (Multiple Choice)
**You send:** `1,2` (for Harvesting and Planting)

**Bot responds:**
```
📍 Work Location Preference

How far are you willing to travel for work?

1️⃣ Up to 10 miles
2️⃣ Up to 25 miles
3️⃣ Up to 50 miles
4️⃣ Any distance

Reply with 1, 2, 3, or 4:
```

#### 7. Set Travel Distance (Multiple Choice)
**You send:** `2` (Up to 25 miles)

**Bot responds:**
```
⏰ Working Hours Preference

What's your preferred work schedule?

1️⃣ Full-time (40+ hours/week)
2️⃣ Part-time (20-40 hours/week)
3️⃣ Flexible (open to both full-time and part-time)

Reply with 1, 2, or 3:
```

#### 8. Set Hours Preference
**You send:** `1` (Full-time)

**Bot responds with TOP 5 job matches (sorted by salary):**
```
✅ Profile Complete!

We found 5 job matches for you!
(Sorted by highest pay)

━━━━━━━━━━━━━━━━━━━━

*1. Irrigation*
🏡 Sunny Acres Farm
💰 $22/hour
📍 West Sacramento, CA
⏰ full-time
👥 1 workers needed

*2. General Labor*
🏡 Green Valley Farm
💰 $20/hour
📍 Woodland, CA
⏰ full-time
👥 2 workers needed

*3. Harvesting*
🏡 Sunny Acres Farm
💰 $18.5/hour
📍 Sacramento, CA
⏰ full-time
👥 5 workers needed

*4. Planting*
🏡 Sunny Acres Farm
💰 $16/hour
📍 Davis, CA
⏰ part-time
👥  3 workers needed

*5. Harvesting*
🏡 Another Farm
💰 $15/hour
📍 Sacramento, CA
⏰ full-time
👥  2 workers needed

━━━━━━━━━━━━━━━━━━━━

Select a job to view details and apply:

Reply with the job number (1-5) or type 'menu' to return to main menu.
```

---

### Test Scenario 2: Select and Apply for a Job

#### 9. Select a Job from the List
**You send:** `3` (select the third job - Harvesting at $18.5/hour)

**Bot responds:**
```
━━━━━━━━━━━━━━━━━━━━
Job Details
━━━━━━━━━━━━━━━━━━━━

🏡 Farm: Sunny Acres Farm

🌾 Type of Work
Harvesting

👥 Workers Needed
5 people

⏰ Work Hours
Full day

💰 Payment
$18.5/hour

📍 Work Location
Sacramento, CA

🚗 Transportation
Provided

📍 Meeting Point
Farm entrance, 123 Farm Road

📋 Additional Details:
Harvest tomatoes. Must be able to work in hot weather and lift 40 lbs.

━━━━━━━━━━━━━━━━━━━━

Would you like to apply for this job?

1️⃣ Yes, apply for this job
2️⃣ No, go back to job list

Reply with 1 or 2:
```

#### 10. Apply for Job
**You send:** `1` (to apply)

**Bot responds:**
```
✅ Application Submitted!

The farm owner has been notified and will contact you soon.

Job Details:
• Position: Harvesting
• Farm: Sunny Acres Farm
• Pay: $18.5/hour
• Match ID: MATCH_1_20231120...

🌾 Farmer Menu

1️⃣ Browse available jobs
2️⃣ Update my preferences
3️⃣ View my job applications
4️⃣ Chat with farm owner
5️⃣ Help

Reply with the number of your choice
```

#### 11. Go Back to Job List (Alternative)
**You send:** `2` (instead of applying)

**Bot responds:**
```
Returns to the top 5 job list, allowing you to select a different job
```

---

### Test Scenario 3: Navigate Main Menu

#### 12. View Applications
**You send:** `3`

**Bot responds:**
```
📋 Your Job Applications:

• Harvesting - Status: accepted

🌾 Farmer Menu
...
```

#### 13. Browse More Jobs
**You send:** `1`

**Bot responds:** Shows top 5 available jobs again (sorted by salary)

#### 14. Get Help
**You send:** `5`

**Bot responds:**
```
❓ FarmConnect Help

• Type 'menu' anytime to return to main menu
• Type 'help' to see this message

For support, contact: support@farmconnect.com
```

#### 15. Return to Menu
**You send:** `menu`

**Bot responds:** Shows farmer main menu

---

## Testing Checklist

### Automated Tests
- [x] User registration and profile management
- [x] Job posting and retrieval
- [x] AI-powered job matching (with mocks)
- [x] Rule-based matching fallback
- [x] Conversation state management
- [x] Data persistence across sessions
- [x] Match creation and retrieval
- [x] Edge case handling (empty messages, long messages)

### Manual WhatsApp Tests
- [x] New user welcome message appears
- [x] Can select farmer role (1)
- [x] Registration flow completes (name, location, ID)
- [x] Work type preference shows multiple choice (1-6)
- [x] Can select multiple work types (e.g., 1,2,3)
- [x] Travel distance preference shows multiple choice (1-4)
- [x] Hours preference shows multiple choice (1-3)
- [x] No minimum pay rate question appears
- [x] Top 5 jobs displayed at once (sorted by salary, highest first)
- [x] Can select a job by number (1-5)
- [x] Selected job shows full details
- [x] Can apply for job (1) or go back to list (2)
- [x] Application confirmation received with job details
- [x] Main menu navigation works
- [x] Can view job applications (menu option 3)
- [x] Can browse jobs again (menu option 1) - shows top 5 list
- [x] Help command works
- [x] Menu command returns to main menu from job browsing

---

## Common Test Commands

| Command | What it does |
|---------|-------------|
| `menu` | Return to main menu |
| `help` | Show help message |
| `1`, `2`, `3`, etc. | Select menu options |

---

## Viewing Test Data

After testing, you can check the generated data:

```bash
# View all users
cat data/users.json

# View all jobs
cat data/jobs.json

# View conversation states
cat data/conversations.json

# View job matches/applications
cat data/matches.json
```

---

## Troubleshooting

### Automated Tests

#### Tests fail with import errors
```bash
# Make sure you're in the project root directory
cd /path/to/twilio-test

# Install dependencies
pip install -r requirements.txt

# Run tests again
pytest
```

#### AI matcher tests fail
```bash
# Check if GEMINI_API_KEY is set
cat .env | grep GEMINI_API_KEY

# Tests should pass even without API key (using mocks)
# For live testing, get API key from: https://aistudio.google.com/app/apikey
```

#### Coverage report not generating
```bash
# Install pytest-cov
pip install pytest-cov

# Run with coverage
pytest --cov --cov-report=html
# Open htmlcov/index.html in browser
```

### Manual WhatsApp Testing

#### Bot doesn't respond
1. Check Flask server is running: `python reply_whatsapp.py`
2. Check ngrok is active: `ngrok http 3000`
3. Verify Twilio webhook is configured correctly

#### No job recommendations
1. Make sure you ran: `python create_sample_jobs/create_sample_jobs.py`
2. Check `data/jobs.json` has jobs with `"status": "open"`
3. Verify your work type preferences match available jobs
4. Try selecting "All types of work" (option 6)

#### Error messages
1. Check Flask console for error logs
2. Verify `.env` file has correct Twilio credentials
3. Check ngrok terminal for request logs