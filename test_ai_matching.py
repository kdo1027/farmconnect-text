"""
Test script for AI job matching algorithm
Run this to test the Gemini-based matching locally
"""
from ai_matcher import get_ai_matcher
from data_store import DataStore

def test_ai_matching():
    """Test AI matching with sample farmer profiles"""

    print("=" * 60)
    print("AI Job Matching Test")
    print("=" * 60)
    print()

    # Initialize
    matcher = get_ai_matcher()
    store = DataStore()

    if not matcher:
        print("ERROR: AI matcher not available!")
        print("Please check your GEMINI_API_KEY in .env file")
        print()
        print("Falling back to rule-based matching test...")
        test_rule_based_matching()
        return

    # Get test data
    jobs = store.get_open_jobs()

    if not jobs:
        print("ERROR: No jobs found in database!")
        print("Run 'python create_sample_jobs.py' first")
        return

    print(f"Found {len(jobs)} open jobs")
    print()

    # Test with different farmer profiles
    test_profiles = [
        ("whatsapp:+15555550101", "Maria Garcia")
    ]

    for phone, name in test_profiles:
        user = store.get_user(phone)

        if not user:
            print(f"User {name} ({phone}) not found, skipping...")
            print()
            continue

        prefs = user.get('profile', {})

        print(f"Testing matches for: {name}")
        print(f"  Work types: {prefs.get('work_types', 'Any')}")
        print(f"  Min pay: ${prefs.get('min_pay_rate', 0)}/hour")
        print(f"  Hours: {prefs.get('hours_preference', 'Any')}")
        print()

        # Run matching
        try:
            results = matcher.match_jobs(jobs, prefs)

            if results is None:
                print("  AI matching returned None (error occurred)")
                print()
                continue

            if not results:
                print("  No matching jobs found")
                print()
                continue

            print(f"  Found {len(results)} matching jobs:")
            print()

            for i, job in enumerate(results, 1):
                print(f"  {i}. {job.get('work_type', 'Unknown')}")
                print(f"     Farm: {job.get('farm_name', 'N/A')}")

                # Display pay info
                if job.get('payment_type'):
                    print(f"     Pay: ${job.get('payment_amount', 0)}/{job.get('payment_type', 'hour')}")
                else:
                    print(f"     Pay: ${job.get('pay_rate', 0)}/hour")

                print(f"     Location: {job.get('location', 'N/A')}")
                print(f"     AI Score: {job.get('_ai_score', 'N/A')}")
                print(f"     Reason: {job.get('_ai_reason', 'N/A')}")
                print()

        except Exception as e:
            print(f"  Error during matching: {e}")
            print()

        print("-" * 60)
        print()

    print("Test completed!")


def test_rule_based_matching():
    """Fallback test using rule-based matching"""
    from chatbot import FarmConnectBot

    print("=" * 60)
    print("Rule-Based Matching Test (Fallback)")
    print("=" * 60)
    print()

    bot = FarmConnectBot()
    store = bot.store

    jobs = store.get_open_jobs()

    if not jobs:
        print("ERROR: No jobs found!")
        return

    print(f"Found {len(jobs)} open jobs")
    print()

    # Test with Maria Garcia's profile
    user = store.get_user("whatsapp:+15555550101")

    if not user:
        print("Test user not found. Using default profile.")
        prefs = {
            "work_types": "Harvesting, Planting",
            "min_pay_rate": 15.0
        }
    else:
        prefs = user.get('profile', {})
        print(f"Testing with: {prefs.get('name', 'Unknown')}")

    results = bot._rule_based_match(jobs, prefs)

    print(f"Matched {len(results)} jobs:")
    print()

    for job in results:
        print(f"  - {job.get('work_type')}: ${job.get('pay_rate', 0)}/hr")

    print()
    print("Test completed!")


def show_available_data():
    """Show what data is available for testing"""
    store = DataStore()

    print("=" * 60)
    print("Available Test Data")
    print("=" * 60)
    print()

    # Show users
    print("FARMERS:")
    for phone, user in store.users.items():
        if user.get('type') == 'farmer':
            profile = user.get('profile', {})
            print(f"  {profile.get('name', 'Unknown')} ({phone})")
            print(f"    Work types: {profile.get('work_types', 'N/A')}")
            print(f"    Min pay: ${profile.get('min_pay_rate', 0)}")
    print()

    # Show jobs
    print("OPEN JOBS:")
    jobs = store.get_open_jobs()
    for job in jobs:
        pay = job.get('pay_rate') or job.get('payment_amount', 0)
        print(f"  {job.get('work_type')}: ${pay} at {job.get('farm_name', 'Unknown')}")
    print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--data":
        show_available_data()
    else:
        test_ai_matching()
