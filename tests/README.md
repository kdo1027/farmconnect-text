# Unit Tests

This folder contains unit tests for the FarmConnect application.

## Setup

```bash
pip install -r requirements.txt
```

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_data_store.py -v
pytest tests/test_ai_matcher.py -v
pytest tests/test_chatbot.py -v
```

### Run with coverage report
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run specific test class
```bash
pytest tests/test_chatbot.py::TestRuleBasedMatching -v
```

### Run specific test
```bash
pytest tests/test_chatbot.py::TestRuleBasedMatching::test_match_by_work_type -v
```

## Test Structure

```
tests/
├── __init__.py           # Package marker
├── conftest.py           # Shared fixtures
├── test_data_store.py    # DataStore CRUD tests
├── test_ai_matcher.py    # AI matcher unit tests
└── test_chatbot.py       # Chatbot logic & matching tests
```

## Test Coverage

| Module | Description |
|--------|-------------|
| `test_data_store.py` | User/Job/Match CRUD, persistence |
| `test_ai_matcher.py` | Prompt building, response parsing, API handling |
| `test_chatbot.py` | Rule-based matching, AI integration, registration flows |

## Key Test Scenarios

### Matching Algorithm
- Work type filtering
- Pay rate minimum enforcement
- Sorting by pay rate
- V2 payment format (per day/hour/task)
- AI matcher integration with fallback

### Data Operations
- User creation and profile updates
- Job creation and retrieval
- Match tracking
- Conversation state management

### Edge Cases
- Empty inputs
- Missing API keys
- Invalid JSON responses
- High/low pay thresholds

## Notes

- Tests use temporary directories to avoid modifying real data
- AI matcher tests use mocks to avoid API calls
- The `pytest` import warning in IDE will resolve after installing requirements
