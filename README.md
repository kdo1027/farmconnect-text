# FarmConnect WhatsApp Chatbot

A WhatsApp chatbot that connects agricultural workers with farm job opportunities - helping day laborers find work and farmers hire qualified workers

## Features

### For Farmers/Laborers:
1. Easy registration (name, location, ID photo)
2. Set job preferences (work type, pay rate, location, hours)
3. Get AI-powered job recommendations
4. Accept/decline jobs
5. Direct chat with farm owners
6. View job applications

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

1. Sign up at https://www.twilio.com/
2. Get your Account SID and Auth Token from https://console.twilio.com/
3. Set up WhatsApp Sandbox: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
4. (Optional) Get Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### 3. Set Environment Variables

Create a `.env` file:

```
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Run the Bot

```bash
python reply_whatsapp.py
```

The server will start on http://localhost:3000

### 5. Expose Webhook with ngrok

In a new terminal:

```bash
# First, authenticate ngrok (one-time setup)
ngrok config add-authtoken YOUR_NGROK_TOKEN

# Then expose your local server
ngrok http 3000
```

Copy the ngrok HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 6. Configure Twilio Webhook

1. Go to https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. In the "Sandbox Configuration" section
3. Set "When a message comes in" to: `https://YOUR_NGROK_URL/reply_whatsapp`
4. Save

## Usage

### First-Time User

1. Send a message to your Twilio WhatsApp number
2. Choose your role:
   - Reply 1 for Farmer/Laborer
   - Reply 2 for Farm Owner

### Farmer Flow

1. **Registration**
   - Provide name, location, and ID photo

2. **Set Preferences** (All Multiple Choice)
   - Choose work types, travel distance, and work schedule

3. **Browse Jobs**
   - View top 5 matched jobs at once (sorted by highest pay)
   - Select a job by number (1-5) to see full details
   - Apply for job or go back to list

4. **Main Menu Options**
   - 1: Browse available jobs
   - 2: Update preferences
   - 3: View applications
   - 4: Chat with farm owner
   - 5: Help

### Special Commands

- Type **menu** anytime to return to main menu
- Type **help** to get help

## File Structure

```
twilio-test/
├── reply_whatsapp.py           # Flask webhook handler
├── chatbot.py                  # Main chatbot logic
├── data_store.py               # JSON data storage
├── ai_matcher.py               # AI-powered job matching with Gemini API
├── test_ai_matching.py         # Test AI matching functionality locally
├── .env                        # Environment variables (git-ignored)
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── TESTING_GUIDE.md            # Comprehensive testing documentation
├── create_sample_jobs/         # Sample job creation scripts
│   ├── create_sample_jobs.py
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_chatbot.py         # Chatbot tests
│   ├── test_data_store.py      # Data storage tests
│   ├── test_ai_matcher.py      # AI matcher tests
│   └── test_bot_integration.py # Integration tests
└── data/                       # JSON data files (auto-created, git-ignored)
    ├── users.json
    ├── jobs.json
    ├── conversations.json
    └── matches.json
```

## Data Storage

All data is stored in JSON files in the `data/` directory:

- **users.json**: User profiles and registration info
- **jobs.json**: Job postings
- **conversations.json**: Current conversation states
- **matches.json**: Job applications and matches

## Job Matching Algorithm
1. Matches jobs by work type preferences
   - Supports multiple work type selections
   - "All types of work" matches all available jobs
2. Sorts by effective pay rate (highest first)
3. Returns **top 5 matches** only
4. Handles both per-hour and per-day payment types

## Testing

The project includes comprehensive automated testing and manual testing guides.

### Quick Test Commands

```bash
# Run all automated tests
pytest

# Run with coverage report
pytest --cov

# Run specific test file
pytest tests/test_chatbot.py

# Run with verbose output
pytest -v
```

**Test Coverage**: 51 automated tests 

### Detailed Testing Documentation

For comprehensive testing instructions including:
- **Automated Testing**: Running pytest, coverage reports, CI/CD setup
- **Manual WhatsApp Testing**: Step-by-step conversation flows
- **AI Matching Tests**: Testing Gemini integration
- **Troubleshooting**: Common test issues and solutions
- **Advanced Testing**: Continuous testing, parallel execution

See **[TESTING_GUIDE.md](TESTING_GUIDE.md)** for the complete testing guide.

## Troubleshooting

### Bot not responding
- Check if Flask server is running
- Check if ngrok is active
- Verify Twilio webhook URL is correct

### Messages not sending
- Verify Twilio credentials in `.env`
- Check Twilio console for errors
- Ensure account has WhatsApp enabled

### Data not persisting
- Check `data/` directory exists
- Verify file permissions
- Check for JSON syntax errors in data files

## Features Implemented

- [x] Rule-based job matching (sorted by salary)
- [x] Multiple-choice preferences (guaranteed valid responses)
- [x] Top 5 job list display
- [x] Comprehensive test suite (49 tests)
- [x] Support for per-hour and per-day payment types
- [x] JSON-based data persistence
- [x] WhatsApp integration via Twilio
- [x] User registration for farmers and farm owners
- [x] Job posting and browsing
- [x] AI matcher code (available but disabled)

## Next Steps 

- [ ] Add bilingual interface (English/Español) for better accessibility
- [ ] Enhance Farm Owner Features - Improve job posting interface and applicant management
- [ ] Geolocation-based job matching (distance calculations)
- [ ] SMS/WhatsApp notifications for new job matches
- [ ] Rating and review system (farmers ↔️ farm owners)
- [ ] Payment integration
- [ ] Database migration (PostgreSQL/MongoDB)
- [ ] Admin dashboard for monitoring
- [ ] Calendar integration for scheduling
- [ ] Voice message support