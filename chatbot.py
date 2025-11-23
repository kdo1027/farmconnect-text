"""
FarmConnect WhatsApp Chatbot Logic
Handles conversation flows for farmers and farm owners
"""
from data_store import DataStore
from typing import Optional, Tuple
import os
from twilio.rest import Client
from dotenv import load_dotenv
from ai_matcher import get_ai_matcher

load_dotenv()

class FarmConnectBot:
    def __init__(self):
        self.store = DataStore()
        # Initialize Twilio client for sending messages
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.twilio_client = Client(account_sid, auth_token) if account_sid and auth_token else None
        self.twilio_number = "whatsapp:+14155238886"  # Twilio sandbox number
        # Disable AI matching - use rule-based only
        self.ai_matcher = None  # get_ai_matcher()


    # TODO: for user exists but not registered, show welcome menu to continue registration
    def handle_message(self, from_number: str, message_body: str, media_url: Optional[str] = None) -> str:
        """
        Main message handler - routes to appropriate flow based on user state
        """
        
        user = self.store.get_user(from_number)
        conv_state = self.store.get_conversation_state(from_number)

        # Check conversation state first (handles both new and existing users)
        if conv_state:
            return self.handle_state(from_number, conv_state, message_body, media_url)

        # New user - show welcome menu
        if not user:
            return self.show_welcome_menu(from_number)

        # Registered user - show main menu
        if user.get('registered'):
            return self.show_main_menu(from_number, user)

        # User exists but not registered - continue registration
        return self.show_welcome_menu(from_number)

    def show_welcome_menu(self, from_number: str) -> str:
        """
        Show welcome menu for new users
        """

        msg = """🌾 *Welcome to FarmConnect!* 🌾

            We connect agricultural workers with farm employers.

            Please select your role:
            1️⃣ I'm looking for farm work (Farmer/Laborer)
            2️⃣ I'm hiring workers (Farm Owner)

            Reply with 1 or 2"""
        
        self.store.set_conversation_state(from_number, 'awaiting_role_selection')
        return msg

    def show_main_menu(self, from_number: str, user: dict) -> str:
        """
        Show main menu based on user type
        """

        if user['type'] == 'farmer':
            return self.show_farmer_menu(from_number)
        else:
            return self.show_owner_menu(from_number)

    def show_farmer_menu(self, from_number: str) -> str:
        """
        Main menu for farmers
        """

        msg = """🌾 *Farmer Menu*

            1️⃣ Browse available jobs
            2️⃣ Update my preferences
            3️⃣ View my job applications
            4️⃣ Chat with farm owner
            5️⃣ Help

            Reply with the number of your choice"""
        
        self.store.clear_conversation_state(from_number)
        return msg

    def show_owner_menu(self, from_number: str) -> str:
        """
        Main menu for farm owners
        """

        msg = """🏡 *Farm Owner Menu*

            1️⃣ Post a new job
            2️⃣ View my job postings
            3️⃣ View applicants
            4️⃣ Chat with applicants
            5️⃣ Help

            Reply with the number of your choice"""
        
        self.store.clear_conversation_state(from_number)
        return msg

    # TODO: Recheck & refactor handle_state method
    def handle_state(self, from_number: str, conv_state: dict, message: str, media_url: Optional[str]) -> str:
        """Handle conversation based on current state"""
        state = conv_state['state']
        data = conv_state.get('data', {})

        # Role selection
        if state == 'awaiting_role_selection':
            if message.strip() == '1':
                self.store.create_user(from_number, 'farmer')
                return self.start_farmer_registration(from_number)
            elif message.strip() == '2':
                self.store.create_user(from_number, 'farm_owner')
                return self.start_owner_registration(from_number)
            else:
                return "Please reply with 1 (for Farmer) or 2 (for Farm Owner)"

        # Farmer registration flows
        elif state == 'farmer_reg_name':
            return self.handle_farmer_name(from_number, message)
        elif state == 'farmer_reg_location':
            return self.handle_farmer_location(from_number, message)
        elif state == 'farmer_reg_id':
            return self.handle_farmer_id(from_number, media_url)
        elif state == 'farmer_update_menu':
            return self.handle_update_menu(from_number, message)
        elif state == 'farmer_update_work_type':
            return self.handle_work_type_update(from_number, message)
        elif state == 'farmer_update_pay_rate':
            return self.handle_pay_rate_update(from_number, message)
        elif state == 'farmer_update_distance':
            return self.handle_distance_update(from_number, message)
        elif state == 'farmer_update_hours':
            return self.handle_hours_update(from_number, message)
        elif state == 'farmer_pref_work_type':
            return self.handle_work_type(from_number, message)
        elif state == 'farmer_pref_pay_rate':
            return self.handle_pay_rate(from_number, message)
        elif state == 'farmer_pref_location':
            return self.handle_pref_location(from_number, message)
        elif state == 'farmer_pref_actual_location':
            return self.handle_actual_location_update(from_number, message)
        elif state == 'farmer_pref_hours':
            return self.handle_hours(from_number, message)

        # Farm owner registration flows
        elif state == 'owner_reg_name':
            return self.handle_owner_name(from_number, message)
        elif state == 'owner_reg_farm_name':
            return self.handle_farm_name(from_number, message)
        elif state == 'owner_reg_location':
            return self.handle_owner_location(from_number, message)

        # Job posting flow
        elif state == 'job_work_type':
            return self.handle_job_work_type(from_number, message, data)
        elif state == 'job_workers_needed':
            return self.handle_job_workers(from_number, message, data)
        elif state == 'job_work_hours':
            return self.handle_job_work_hours(from_number, message, data)
        elif state == 'job_payment':
            return self.handle_job_payment(from_number, message, data)
        elif state == 'job_payment_type':
            return self.handle_job_payment_type(from_number, message, data)
        elif state == 'job_location':
            return self.handle_job_location(from_number, message, data)
        elif state == 'job_transportation':
            return self.handle_job_transportation(from_number, message, data)
        elif state == 'job_meeting_point':
            return self.handle_job_meeting_point(from_number, message, data)
        elif state == 'job_description':
            return self.handle_job_description(from_number, message, data)

        # Job browsing and application
        elif state == 'viewing_jobs':
            return self.handle_job_selection(from_number, message, data)
        elif state == 'selecting_from_recommendations':
            return self.handle_job_selection_from_list(from_number, message, data)
        elif state == 'reviewing_recommendation':
            return self.handle_recommendation_action(from_number, message, data)
        elif state == 'job_details_view':
            return self.handle_job_application(from_number, message, data)
        elif state == 'job_action':
            return self.handle_job_action(from_number, message, data)

        # Direct messaging
        elif state == 'chatting':
            return self.handle_chat_message(from_number, message, data)

        return "I didn't understand that. Please try again or type 'menu' for main menu."

    # ========== FARMER REGISTRATION ==========
    def start_farmer_registration(self, from_number: str) -> str:
        """Start farmer registration process"""
        self.store.set_conversation_state(from_number, 'farmer_reg_name')
        return """✅ Great! Let's get you registered.

📝 *Step 1 of 3: Personal Information*

What's your full name?"""

    def handle_farmer_name(self, from_number: str, name: str) -> str:
        """Handle farmer name input"""
        self.store.update_user_profile(from_number, {'name': name})
        self.store.set_conversation_state(from_number, 'farmer_reg_location')
        return f"""Nice to meet you, {name}! 👋

📍 *Step 2 of 3: Location*

What's your location? (City or area where you're looking for work)"""

    def handle_farmer_location(self, from_number: str, location: str) -> str:
        """Handle farmer location input"""
        self.store.update_user_profile(from_number, {'location': location})
        self.store.set_conversation_state(from_number, 'farmer_reg_id')
        return """📸 *Step 3 of 3: ID Verification*

Please upload a photo of your ID card or driver's license.

This helps us keep FarmConnect safe for everyone."""

    def handle_farmer_id(self, from_number: str, media_url: Optional[str]) -> str:
        """Handle farmer ID upload"""
        if not media_url:
            return "Please send a photo of your ID card."

        self.store.update_user_profile(from_number, {'id_verified': True, 'id_photo_url': media_url})
        self.store.update_user(from_number, {'registered': True})

        # Now collect job preferences
        self.store.set_conversation_state(from_number, 'farmer_pref_work_type')
        return """✅ ID received! Thank you.

Now let's set up your job preferences to find the best matches.

🛠 *Work Type Preferences*
What type of farm work are you interested in? (Select all that apply)

1️⃣ Harvesting
2️⃣ Planting
3️⃣ Irrigation
4️⃣ Livestock care
5️⃣ General labor
6️⃣ All types of work

Reply with numbers separated by commas (e.g., 1,2,3) or just one number:"""

    # ========== FARMER PREFERENCES ==========
    def handle_work_type(self, from_number: str, work_types: str) -> str:
        """Handle work type preference - multiple choice"""
        work_type_map = {
            '1': 'Harvesting',
            '2': 'Planting',
            '3': 'Irrigation',
            '4': 'Livestock care',
            '5': 'General labor',
            '6': 'All types of work'
        }

        # Parse the selections
        selections = [s.strip() for s in work_types.replace(' ', '').split(',')]
        selected_types = []

        for sel in selections:
            if sel in work_type_map:
                selected_types.append(work_type_map[sel])

        if not selected_types:
            return """Please select valid options (1-6).

Reply with numbers separated by commas (e.g., 1,2,3):"""

        # Store as comma-separated string
        work_types_str = ', '.join(selected_types)
        self.store.update_user_profile(from_number, {'work_types': work_types_str})

        # Skip pay rate, go directly to location preference
        self.store.set_conversation_state(from_number, 'farmer_pref_location')
        return """📍 *Work Location Preference*

How far are you willing to travel for work?

1️⃣ Up to 10 miles
2️⃣ Up to 25 miles
3️⃣ Up to 50 miles
4️⃣ Any distance

Reply with 1, 2, 3, or 4:"""

    def handle_pay_rate(self, from_number: str, pay_rate: str) -> str:
        """Handle pay rate preference"""
        try:
            rate = float(pay_rate.replace('$', '').strip())
            self.store.update_user_profile(from_number, {'min_pay_rate': rate})
            self.store.set_conversation_state(from_number, 'farmer_pref_location')
            return """📍 *Work Location Preference*

How far are you willing to travel for work? (in miles)

Example: 20"""
        except ValueError:
            return "Please enter a valid number for the hourly rate. Example: 15"

    def handle_pref_location(self, from_number: str, distance: str) -> str:
        """Handle location preference - multiple choice"""
        distance_map = {
            '1': 10,
            '2': 25,
            '3': 50,
            '4': 999  # Any distance
        }

        distance = distance.strip()
        if distance not in distance_map:
            return """Please select a valid option (1-4).

1️⃣ Up to 10 miles
2️⃣ Up to 25 miles
3️⃣ Up to 50 miles
4️⃣ Any distance

Reply with 1, 2, 3, or 4:"""

        miles = distance_map[distance]
        self.store.update_user_profile(from_number, {'max_distance': miles})
        self.store.set_conversation_state(from_number, 'farmer_pref_hours')
        return """⏰ *Working Hours Preference*

What's your preferred work schedule?

1️⃣ Full-time (40+ hours/week)
2️⃣ Part-time (20-40 hours/week)
3️⃣ Flexible (open to both full-time and part-time)

Reply with 1, 2, or 3:"""

    def handle_hours(self, from_number: str, choice: str) -> str:
        """Handle hours preference"""
        hours_map = {
            '1': 'full-time',
            '2': 'part-time',
            '3': 'flexible'
        }
        if choice in hours_map:
            self.store.update_user_profile(from_number, {'hours_preference': hours_map[choice]})
            self.store.clear_conversation_state(from_number)

            # Now show matching jobs
            return self.show_job_recommendations(from_number)
        else:
            return "Please reply with 1, 2, or 3"

    # ========== FARM OWNER REGISTRATION ==========
    def start_owner_registration(self, from_number: str) -> str:
        """Start farm owner registration"""
        self.store.set_conversation_state(from_number, 'owner_reg_name')
        return """✅ Welcome, farm owner!

📝 *Registration - Step 1 of 3*

What's your full name?"""

    def handle_owner_name(self, from_number: str, name: str) -> str:
        """Handle owner name"""
        self.store.update_user_profile(from_number, {'name': name})
        self.store.set_conversation_state(from_number, 'owner_reg_farm_name')
        return """🏡 *Step 2 of 3*

What's your farm/business name?"""

    def handle_farm_name(self, from_number: str, farm_name: str) -> str:
        """Handle farm name"""
        self.store.update_user_profile(from_number, {'farm_name': farm_name})
        self.store.set_conversation_state(from_number, 'owner_reg_location')
        return """📍 *Step 3 of 3*

Where is your farm located? (City/Area)"""

    def handle_owner_location(self, from_number: str, location: str) -> str:
        """Handle owner location"""
        self.store.update_user_profile(from_number, {'location': location})
        self.store.update_user(from_number, {'registered': True})
        self.store.clear_conversation_state(from_number)

        return f"""✅ Registration complete! Welcome to FarmConnect.

You can now post job opportunities and connect with workers.

{self.show_owner_menu(from_number)}"""

    # ========== JOB POSTING ==========
    def start_job_posting(self, from_number: str) -> str:
        """Start job posting flow"""
        self.store.set_conversation_state(from_number, 'job_work_type', {})
        return """📝 *New Job Posting - Step 1 of 8*

🌾 *Type of Work*

What type of work is needed?

Examples: Tomato Harvest, Berry Picking, Planting Corn, Irrigation Setup"""

    def handle_job_work_type(self, from_number: str, work_type: str, data: dict) -> str:
        """Handle job work type"""
        data['work_type'] = work_type
        self.store.set_conversation_state(from_number, 'job_workers_needed', data)
        return """👥 *Step 2 of 8: Workers Needed*

How many workers do you need?

Example: 5"""

    def handle_job_workers(self, from_number: str, workers: str, data: dict) -> str:
        """Handle number of workers needed"""
        try:
            data['workers_needed'] = int(workers)
            self.store.set_conversation_state(from_number, 'job_work_hours', data)
            return """⏰ *Step 3 of 8: Work Hours*

What are the work hours?

Format: START - END (use AM/PM)

Examples:
• 6:00 AM - 2:00 PM
• 7:00 AM - 3:00 PM
• 5:00 AM - 1:00 PM"""
        except ValueError:
            return "Please enter a valid number. Example: 5"

    def handle_job_work_hours(self, from_number: str, hours: str, data: dict) -> str:
        """Handle work hours"""
        data['work_hours'] = hours.strip()
        self.store.set_conversation_state(from_number, 'job_payment_type', data)
        return """💰 *Step 4 of 8: Payment Type*

How will workers be paid?

1️⃣ Per hour
2️⃣ Per day
3️⃣ Per task/piece

Reply with 1, 2, or 3:"""

    def handle_job_payment_type(self, from_number: str, choice: str, data: dict) -> str:
        """Handle payment type"""
        payment_types = {
            '1': 'per hour',
            '2': 'per day',
            '3': 'per task'
        }

        if choice not in payment_types:
            return "Please reply with 1, 2, or 3"

        data['payment_type'] = payment_types[choice]
        self.store.set_conversation_state(from_number, 'job_payment', data)

        payment_example = {
            '1': '18 (for $18/hour)',
            '2': '150 (for $150/day)',
            '3': '2.50 (for $2.50 per basket)'
        }

        return f"""💵 *Step 5 of 8: Payment Amount*

How much will you pay {payment_types[choice]}?

Example: {payment_example[choice]}"""

    def handle_job_payment(self, from_number: str, amount: str, data: dict) -> str:
        """Handle payment amount"""
        try:
            data['payment_amount'] = float(amount.replace('$', '').strip())
            self.store.set_conversation_state(from_number, 'job_location', data)
            return """📍 *Step 6 of 8: Work Location*

Where is the work located?

Example: Green Valley Farm, 123 Farm Road, Sacramento"""
        except ValueError:
            return "Please enter a valid number. Example: 150"

    def handle_job_location(self, from_number: str, location: str, data: dict) -> str:
        """Handle job location"""
        data['location'] = location.strip()
        self.store.set_conversation_state(from_number, 'job_transportation', data)
        return """🚗 *Step 7 of 8: Transportation*

Is transportation provided?

1️⃣ Yes, we provide transportation
2️⃣ No, workers must arrange their own

Reply with 1 or 2:"""

    def handle_job_transportation(self, from_number: str, choice: str, data: dict) -> str:
        """Handle transportation"""
        if choice == '1':
            data['transportation'] = 'provided'
            self.store.set_conversation_state(from_number, 'job_meeting_point', data)
            return """📍 *Step 8 of 8: Meeting Point*

Where should workers meet for pickup?

Include time and location.

Example: Town Square, 5:45 AM pickup"""
        elif choice == '2':
            data['transportation'] = 'not provided'
            data['meeting_point'] = 'N/A - Workers arrange own transport'
            self.store.set_conversation_state(from_number, 'job_description', data)
            return """📋 *Additional Details (Optional)*

Add any other important details about the job:

Examples:
• Experience required
• What to bring
• Lunch provided
• Special requirements

Type your details or 'skip':"""
        else:
            return "Please reply with 1 or 2"

    def handle_job_meeting_point(self, from_number: str, meeting_info: str, data: dict) -> str:
        """Handle meeting point"""
        data['meeting_point'] = meeting_info.strip()
        self.store.set_conversation_state(from_number, 'job_description', data)
        return """📋 *Additional Details (Optional)*

Add any other important details about the job:

Examples:
• Experience required
• What to bring
• Lunch provided
• Special requirements

Type your details or 'skip':"""

    def handle_job_description(self, from_number: str, description: str, data: dict) -> str:
        """Handle job description and create job"""
        user = self.store.get_user(from_number)

        if description.lower() != 'skip':
            data['description'] = description
        else:
            data['description'] = 'See job details above'

        data['owner_phone'] = from_number
        data['owner_name'] = user['profile'].get('name', 'Farm Owner')
        data['farm_name'] = user['profile'].get('farm_name', 'Farm')

        # Backward compatibility - set hours field for matching
        if data['payment_type'] == 'per day':
            data['hours'] = 'full-time'
        elif data['payment_type'] == 'per hour':
            data['hours'] = 'flexible'
        else:
            data['hours'] = 'flexible'

        job_id = self.store.create_job(data)
        self.store.clear_conversation_state(from_number)

        # Notify matching farmers
        self.notify_matching_farmers(job_id, data)

        # Format payment display
        pay_display = f"${data['payment_amount']} {data['payment_type']}"

        return f"""✅ *Job Posted Successfully!*

━━━━━━━━━━━━━━━━━━━━
📋 *Job Summary*

🌾 Work: {data['work_type']}
👥 Workers: {data['workers_needed']} people
⏰ Hours: {data.get('work_hours', 'Not specified')}
💰 Pay: {pay_display}
📍 Location: {data['location']}
🚗 Transport: {data['transportation']}
📍 Meeting: {data['meeting_point']}

━━━━━━━━━━━━━━━━━━━━

Job ID: {job_id}

Matching workers will be notified!

{self.show_owner_menu(from_number)}"""

    # ========== JOB MATCHING & RECOMMENDATIONS ==========
    def show_job_recommendations(self, from_number: str) -> str:
        """Show top 5 job recommendations based on farmer preferences"""
        user = self.store.get_user(from_number)
        prefs = user.get('profile', {})

        # Get all open jobs
        open_jobs = self.store.get_open_jobs()

        # Rule-based matching (returns top 5 sorted by salary)
        matched_jobs = self.match_jobs(open_jobs, prefs, from_number)

        if not matched_jobs:
            return f"""✅ *Profile Complete!*

No job matches found right now. We'll notify you when new jobs matching your preferences are posted.

{self.show_farmer_menu(from_number)}"""

        # Show all matched jobs at once (up to 5)
        return self.show_multiple_job_recommendations(from_number, matched_jobs)

    def show_multiple_job_recommendations(self, from_number: str, matched_jobs: list) -> str:
        """Display top 5 job recommendations at once"""
        msg = f"""✅ *Profile Complete!*

We found {len(matched_jobs)} job match{"es" if len(matched_jobs) > 1 else ""} for you!
(Sorted by highest pay)

━━━━━━━━━━━━━━━━━━━━

"""

        # Display each job in the list
        for i, job in enumerate(matched_jobs, 1):
            # Format payment display
            if job.get('payment_type') == 'per day':
                pay_display = f"${job.get('payment_amount', 'N/A')}/day"
            elif job.get('payment_type') == 'per hour':
                pay_display = f"${job.get('payment_amount', 'N/A')}/hour"
            elif job.get('pay_rate'):
                pay_display = f"${job.get('pay_rate')}/hour"
            else:
                pay_display = "Contact for details"

            msg += f"""*{i}. {job.get('work_type', 'Farm Work')}*
🏡 {job.get('farm_name', 'Farm')}
💰 {pay_display}
📍 {job.get('location', 'N/A')}
⏰ {job.get('hours', job.get('work_hours', 'Full day'))}
👥 {job.get('workers_needed', 'N/A')} workers needed

"""

        msg += """━━━━━━━━━━━━━━━━━━━━

*Select a job to view details and apply:*

Reply with the job number (1-""" + str(len(matched_jobs)) + """) or type 'menu' to return to main menu."""

        # Store matched jobs in conversation state
        job_ids = [j['job_id'] for j in matched_jobs]
        self.store.set_conversation_state(from_number, 'selecting_from_recommendations', {
            'jobs': job_ids
        })

        return msg

    def show_single_job_recommendation(self, from_number: str, matched_jobs: list, index: int, is_first: bool = False) -> str:
        """Display a single job recommendation with full details"""
        if index >= len(matched_jobs):
            # No more jobs
            return f"""✅ *No more job matches available.*

You've reviewed all matching jobs for now. We'll notify you when new jobs are posted.

{self.show_farmer_menu(from_number)}"""

        job = matched_jobs[index]

        # Create header message
        if is_first:
            header = f"""🤖 *AI Matching Complete!*

We found {len(matched_jobs)} job match{"es" if len(matched_jobs) > 1 else ""} for you!

━━━━━━━━━━━━━━━━━━━━
*Job 1 of {len(matched_jobs)}*
━━━━━━━━━━━━━━━━━━━━
"""
        else:
            header = f"""━━━━━━━━━━━━━━━━━━━━
*Next Job Recommendation* ({index + 1} of {len(matched_jobs)})

━━━━━━━━━━━━━━━━━━━━
"""

        # Format payment display
        if job.get('payment_type'):
            pay_display = f"${job.get('payment_amount', 'N/A')} {job.get('payment_type')}"
        elif job.get('pay_rate'):
            # Backward compatibility for old jobs
            pay_display = f"${job.get('pay_rate')}/hour"
        else:
            pay_display = "Contact for details"

        msg = f"""{header}
🏡 *Farm:* {job.get('farm_name', 'Farm')}

🌾 *Type of Work*
{job['work_type']}

👥 *Workers Needed*
{job['workers_needed']} people

⏰ *Work Hours*
{job.get('work_hours', 'Full day')}

💰 *Payment*
{pay_display}

📍 *Work Location*
{job['location']}

🚗 *Transportation*
{job.get('transportation', 'Not specified').capitalize()}

📍 *Meeting Point*
{job.get('meeting_point', 'See location above')}

📋 *Additional Details:*
{job.get('description', 'No additional details')}

━━━━━━━━━━━━━━━━━━━━

*Are you interested in this job?*

1️⃣ Yes, apply for this job
2️⃣ No, show me the next job

Reply with 1 or 2 (or type 'menu' to return to main menu):"""

        # Store matched jobs list and current index in state
        job_ids = [j['job_id'] for j in matched_jobs]
        self.store.set_conversation_state(from_number, 'reviewing_recommendation', {
            'jobs': job_ids,
            'current_index': index
        })

        return msg

    def handle_recommendation_action(self, from_number: str, message: str, data: dict) -> str:
        """Handle accept/decline action for job recommendations"""
        message = message.strip()

        if message.lower() == 'menu':
            user = self.store.get_user(from_number)
            self.store.clear_conversation_state(from_number)
            return self.show_main_menu(from_number, user)

        job_ids = data.get('jobs', [])
        current_index = data.get('current_index', 0)

        if current_index >= len(job_ids):
            self.store.clear_conversation_state(from_number)
            user = self.store.get_user(from_number)
            return self.show_farmer_menu(from_number)

        current_job_id = job_ids[current_index]

        if message == '1':
            # Accept - apply for the job
            job = self.store.get_job(current_job_id)
            if not job:
                return "Job not found. Please try again or type 'menu'."

            match_id = self.store.create_match(current_job_id, from_number, 'accepted')
            user = self.store.get_user(from_number)

            # Notify farm owner
            owner_phone = job.get('owner_phone')
            if owner_phone:
                self.send_message(
                    owner_phone,
                    f"""🎉 *New Job Application!*

{user['profile'].get('name', 'A worker')} has applied for your job: {job['work_type']}

Location: {job['location']}
Pay Rate: ${job['pay_rate']}/hour

Type '4' from the menu to chat with applicants."""
                )

            self.store.clear_conversation_state(from_number)

            # Format payment for confirmation
            if job.get('payment_type'):
                pay_confirm = f"${job.get('payment_amount')} {job.get('payment_type')}"
            else:
                pay_confirm = f"${job.get('pay_rate', 'TBD')}/hour"

            return f"""✅ *Application Submitted!*

The farm owner has been notified and will contact you soon.

*Job Details:*
• Position: {job['work_type']}
• Farm: {job.get('farm_name', 'N/A')}
• Pay: {pay_confirm}
• Hours: {job.get('work_hours', 'See details')}
• Match ID: {match_id}

{self.show_farmer_menu(from_number)}"""

        elif message == '2':
            # Decline - show next job
            next_index = current_index + 1

            # Get all jobs to show next one
            all_matched_jobs = []
            for job_id in job_ids:
                job = self.store.get_job(job_id)
                if job:
                    all_matched_jobs.append(job)

            return self.show_single_job_recommendation(from_number, all_matched_jobs, next_index)

        else:
            return "Please reply with 1 (Apply) or 2 (Show next job), or type 'menu' for main menu."

    def match_jobs(self, jobs: list, prefs: dict, from_number: str = None) -> list:
        """
        Job matching algorithm - uses AI matching if available, falls back to rule-based.
        """
        # Try AI matching first if available
        if self.ai_matcher:
            try:
                print("AI matching in progress...")
                ai_results = self.ai_matcher.match_jobs(jobs, prefs)
                if ai_results is not None:
                    print(f"AI matching returned {len(ai_results)} jobs")
                    return ai_results
                else:
                    print("AI matching returned None, falling back to rule-based")
            except Exception as e:
                print(f"AI matching failed: {e}, falling back to rule-based")

        # Fallback to rule-based matching
        return self._rule_based_match(jobs, prefs)

    def _rule_based_match(self, jobs: list, prefs: dict) -> list:
        """Rule-based job matching algorithm - matches by work type and sorts by salary"""
        matched = []

        for job in jobs:
            # Check work type (simple keyword match)
            pref_types = prefs.get('work_types', '').lower()
            job_type = job.get('work_type', '').lower()

            # If user selected "All types of work", match everything
            if 'all types of work' in pref_types:
                matched.append(job)
                continue

            # If preferences exist, check if they match
            if pref_types:
                # Check if any preferred type matches the job type
                type_match = False
                for pref_type in pref_types.split(','):
                    pref_type = pref_type.strip()
                    if pref_type in job_type or job_type in pref_type:
                        type_match = True
                        break

                if not type_match:
                    continue

            matched.append(job)

        # Sort by effective pay rate (highest first)
        def get_sort_key(job):
            if job.get('payment_type') == 'per day':
                return job.get('payment_amount', 0) / 8
            elif job.get('payment_type') == 'per hour':
                return job.get('payment_amount', 0)
            else:
                return job.get('pay_rate', 0)

        matched.sort(key=get_sort_key, reverse=True)

        # Return top 5 matches only
        return matched[:5]

    def handle_job_selection_from_list(self, from_number: str, message: str, data: dict) -> str:
        """Handle user selecting a job from the list of 5 recommendations"""
        message = message.strip()

        if message.lower() == 'menu':
            user = self.store.get_user(from_number)
            self.store.clear_conversation_state(from_number)
            return self.show_main_menu(from_number, user)

        job_ids = data.get('jobs', [])

        try:
            choice = int(message)
            if 1 <= choice <= len(job_ids):
                job_id = job_ids[choice - 1]
                job = self.store.get_job(job_id)

                if not job:
                    return "Job not found. Please try again or type 'menu'."

                # Format payment display
                if job.get('payment_type') == 'per day':
                    pay_display = f"${job.get('payment_amount', 'N/A')}/day"
                elif job.get('payment_type') == 'per hour':
                    pay_display = f"${job.get('payment_amount', 'N/A')}/hour"
                elif job.get('pay_rate'):
                    pay_display = f"${job.get('pay_rate')}/hour"
                else:
                    pay_display = "Contact for details"

                msg = f"""━━━━━━━━━━━━━━━━━━━━
*Job Details*
━━━━━━━━━━━━━━━━━━━━

🏡 *Farm:* {job.get('farm_name', 'Farm')}

🌾 *Type of Work*
{job.get('work_type', 'Farm Work')}

👥 *Workers Needed*
{job.get('workers_needed', 'N/A')} people

⏰ *Work Hours*
{job.get('work_hours', job.get('hours', 'Full day'))}

💰 *Payment*
{pay_display}

📍 *Work Location*
{job.get('location', 'N/A')}

🚗 *Transportation*
{job.get('transportation', 'Not specified').capitalize()}

📍 *Meeting Point*
{job.get('meeting_point', 'See location above')}

📋 *Additional Details:*
{job.get('description', 'No additional details')}

━━━━━━━━━━━━━━━━━━━━

*Would you like to apply for this job?*

1️⃣ Yes, apply for this job
2️⃣ No, go back to job list

Reply with 1 or 2:"""

                # Store job_id in state for application
                self.store.set_conversation_state(from_number, 'job_details_view', {
                    'job_id': job_id,
                    'all_jobs': job_ids
                })

                return msg
            else:
                return f"Please enter a number between 1 and {len(job_ids)}, or type 'menu'."
        except ValueError:
            if message.lower() == 'menu':
                user = self.store.get_user(from_number)
                self.store.clear_conversation_state(from_number)
                return self.show_main_menu(from_number, user)
            return f"Please enter a valid number (1-{len(job_ids)}) or type 'menu'."

    def handle_job_application(self, from_number: str, message: str, data: dict) -> str:
        """Handle applying for a job after viewing details"""
        message = message.strip()

        if message.lower() == 'menu':
            user = self.store.get_user(from_number)
            self.store.clear_conversation_state(from_number)
            return self.show_main_menu(from_number, user)

        job_id = data.get('job_id')
        all_jobs = data.get('all_jobs', [])

        if message == '1':
            # Apply for the job
            job = self.store.get_job(job_id)
            if not job:
                return "Job not found. Please try again or type 'menu'."

            match_id = self.store.create_match(job_id, from_number, 'accepted')
            user = self.store.get_user(from_number)

            # Notify farm owner
            owner_phone = job.get('owner_phone')
            if owner_phone and self.twilio_client:
                # Format payment display for notification
                if job.get('payment_type') == 'per day':
                    pay_display = f"${job.get('payment_amount', 'N/A')}/day"
                elif job.get('payment_type') == 'per hour':
                    pay_display = f"${job.get('payment_amount', 'N/A')}/hour"
                elif job.get('pay_rate'):
                    pay_display = f"${job.get('pay_rate')}/hour"
                else:
                    pay_display = "Contact for details"

                self.send_message(
                    owner_phone,
                    f"""🎉 *New Job Application!*

{user['profile'].get('name', 'A worker')} has applied for your job: {job.get('work_type', 'Farm Work')}

Location: {job.get('location', 'N/A')}
Pay: {pay_display}

Type '3' from the menu to view applicants."""
                )

            self.store.clear_conversation_state(from_number)

            return f"""✅ *Application Submitted!*

The farm owner has been notified and will contact you soon.

*Job Details:*
• Position: {job.get('work_type', 'Farm Work')}
• Farm: {job.get('farm_name', 'Farm')}
• Pay: {pay_display}
• Match ID: {match_id}

{self.show_farmer_menu(from_number)}"""

        elif message == '2':
            # Go back to job list
            # Recreate the job list display
            matched_jobs = [self.store.get_job(jid) for jid in all_jobs if self.store.get_job(jid)]

            return self.show_multiple_job_recommendations(from_number, matched_jobs)

        else:
            return "Please reply with 1 (Apply) or 2 (Go back)."

    def handle_job_selection(self, from_number: str, message: str, data: dict) -> str:
        """Handle job selection from recommendations"""
        jobs = data.get('jobs', [])

        try:
            choice = int(message.strip())
            if 1 <= choice <= len(jobs):
                job_id = jobs[choice - 1]
                job = self.store.get_job(job_id)

                if not job:
                    return "Job not found. Please try again."

                msg = f"""*Job Details:*

🏡 Farm: {job.get('farm_name', 'N/A')}
🛠 Work Type: {job['work_type']}
💰 Pay: ${job['pay_rate']}/hour
📍 Location: {job['location']}
⏰ Schedule: {job['hours']}
👥 Workers Needed: {job['workers_needed']}

📋 Description:
{job.get('description', 'No description provided')}

Would you like to apply for this job?
1️⃣ Yes, apply
2️⃣ No, go back

Reply with 1 or 2:"""

                self.store.set_conversation_state(from_number, 'job_action', {'job_id': job_id})
                return msg
            else:
                return f"Please select a number between 1 and {len(jobs)}"
        except ValueError:
            if message.lower() == 'menu':
                user = self.store.get_user(from_number)
                return self.show_main_menu(from_number, user)
            return "Please enter a valid job number."

    def handle_job_action(self, from_number: str, message: str, data: dict) -> str:
        """Handle apply/decline action"""
        job_id = data.get('job_id')

        if message.strip() == '1':
            # Accept job
            match_id = self.store.create_match(job_id, from_number, 'accepted')
            job = self.store.get_job(job_id)
            user = self.store.get_user(from_number)

            # Notify farm owner
            owner_phone = job.get('owner_phone')
            if owner_phone:
                self.send_message(
                    owner_phone,
                    f"""🎉 New Job Application!

{user['profile'].get('name', 'A worker')} has applied for your job: {job['work_type']}

Type '4' from the menu to chat with applicants."""
                )

            self.store.clear_conversation_state(from_number)
            user = self.store.get_user(from_number)

            return f"""✅ *Application Submitted!*

The farm owner has been notified. They'll contact you soon.

Match ID: {match_id}

{self.show_farmer_menu(from_number)}"""

        elif message.strip() == '2':
            # Decline
            self.store.clear_conversation_state(from_number)
            user = self.store.get_user(from_number)
            return f"""No problem!

{self.show_farmer_menu(from_number)}"""
        else:
            return "Please reply with 1 (Apply) or 2 (Go back)"

    # ========== DIRECT MESSAGING ==========
    def start_chat(self, from_number: str, with_phone: str) -> str:
        """Start direct chat between farmer and owner"""
        self.store.set_conversation_state(from_number, 'chatting', {'with': with_phone})

        user = self.store.get_user(from_number)
        other_user = self.store.get_user(with_phone)

        return f"""💬 *Chat Started*

You're now chatting with {other_user['profile'].get('name', 'User')}.

Type your message to send. Type 'endchat' to return to main menu."""

    def handle_chat_message(self, from_number: str, message: str, data: dict) -> str:
        """Handle chat message between users"""
        if message.lower() == 'endchat':
            self.store.clear_conversation_state(from_number)
            user = self.store.get_user(from_number)
            return f"""Chat ended.

{self.show_main_menu(from_number, user)}"""

        with_phone = data.get('with')
        user = self.store.get_user(from_number)
        sender_name = user['profile'].get('name', 'User')

        # Forward message to other user
        self.send_message(
            with_phone,
            f"""💬 Message from {sender_name}:

{message}

(Reply to continue conversation, or type 'menu' for main menu)"""
        )

        return "✅ Message sent!"

    def notify_matching_farmers(self, job_id: str, job_data: dict):
        """Notify farmers about new matching job"""
        # Get all registered farmers
        # This is a simplified version - in production you'd want better filtering
        # For now, just notify farmers who might be interested
        pass  # Will implement notification logic

    def send_message(self, to_phone: str, message: str):
        """Send WhatsApp message via Twilio"""
        if not self.twilio_client:
            print(f"Would send to {to_phone}: {message}")
            return

        try:
            self.twilio_client.messages.create(
                from_=self.twilio_number,
                to=to_phone,
                body=message
            )
        except Exception as e:
            print(f"Error sending message: {e}")

    # ========== MENU HANDLERS ==========
    def handle_menu_selection(self, from_number: str, user: dict, choice: str) -> str:
        """Handle main menu selection"""
        if user['type'] == 'farmer':
            if choice == '1':
                return self.show_job_recommendations(from_number)
            elif choice == '2':
                self.store.set_conversation_state(from_number, 'farmer_update_menu')
                return """⚙️ *Update Profile*

What would you like to update?

1️⃣ Work type preferences
2️⃣ Location (city/state)
3️⃣ Minimum pay rate
4️⃣ Travel distance
5️⃣ Hours preference
6️⃣ Back to main menu

Reply with number (1-6):"""
            elif choice == '3':
                matches = self.store.get_farmer_matches(from_number)
                if not matches:
                    return "You haven't applied to any jobs yet.\n\n" + self.show_farmer_menu(from_number)
                msg = "📋 *Your Job Applications:*\n\n"
                for match in matches:
                    job = self.store.get_job(match['job_id'])
                    if job:
                        msg += f"• {job['work_type']} - Status: {match['status']}\n"
                msg += "\n" + self.show_farmer_menu(from_number)
                return msg
            elif choice == '5':
                return self.show_help()
        else:  # farm owner
            if choice == '1':
                return self.start_job_posting(from_number)
            elif choice == '2':
                return self.view_owner_jobs(from_number)
            elif choice == '5':
                return self.show_help()

        return self.show_main_menu(from_number, user)

    def handle_update_menu(self, from_number: str, choice: str) -> str:
        """Handle update submenu selection"""
        if choice == '1':
            self.store.set_conversation_state(from_number, 'farmer_update_work_type')
            user = self.store.get_user(from_number)
            current_types = user.get('profile', {}).get('work_types', 'Not set')
            return f"""🛠 *Update Work Type Preferences*

Current preferences: {current_types}

What type of farm work are you interested in?

Examples: Harvesting, Planting, Irrigation, Livestock care, General labor

Type your preferred work types (separated by commas if multiple):"""
        elif choice == '2':
            self.store.set_conversation_state(from_number, 'farmer_pref_actual_location')
            user = self.store.get_user(from_number)
            current_location = user.get('profile', {}).get('location', 'Not set')
            return f"""📍 *Update Location*

Current location: {current_location}

Where are you located?

Example: Chapel Hill, NC"""
        elif choice == '3':
            self.store.set_conversation_state(from_number, 'farmer_update_pay_rate')
            user = self.store.get_user(from_number)
            current_pay = user.get('profile', {}).get('min_pay_rate', 'Not set')
            return f"""💰 *Update Minimum Pay Rate*

Current minimum: ${current_pay}/hour

What's your minimum acceptable hourly pay rate?

Example: 18"""
        elif choice == '4':
            self.store.set_conversation_state(from_number, 'farmer_update_distance')
            user = self.store.get_user(from_number)
            current_distance = user.get('profile', {}).get('max_distance', 'Not set')
            return f"""🚗 *Update Travel Distance*

Current max distance: {current_distance} miles

How far are you willing to travel for work? (in miles)

Example: 20"""
        elif choice == '5':
            self.store.set_conversation_state(from_number, 'farmer_update_hours')
            user = self.store.get_user(from_number)
            current_hours = user.get('profile', {}).get('hours_preference', 'Not set')
            return f"""⏰ *Update Hours Preference*

Current preference: {current_hours}

What's your preferred work schedule?

1️⃣ Full-time (40+ hours/week)
2️⃣ Part-time (20-40 hours/week)
3️⃣ Flexible (open to both)

Reply with 1, 2, or 3:"""
        elif choice == '6':
            self.store.clear_conversation_state(from_number)
            user = self.store.get_user(from_number)
            return self.show_farmer_menu(from_number)
        else:
            return "Please reply with a number from 1 to 6"

    def handle_work_type_update(self, from_number: str, work_type: str) -> str:
        """Handle work type update - returns to menu after"""
        self.store.update_user_profile(from_number, {'work_types': work_type.strip()})
        self.store.clear_conversation_state(from_number)
        return f"""✅ *Work Type Updated!*

New preferences: {work_type.strip()}

{self.show_farmer_menu(from_number)}"""

    def handle_pay_rate_update(self, from_number: str, pay_rate: str) -> str:
        """Handle pay rate update - returns to menu after"""
        try:
            rate = float(pay_rate.replace('$', '').strip())
            self.store.update_user_profile(from_number, {'min_pay_rate': rate})
            self.store.clear_conversation_state(from_number)
            return f"""✅ *Pay Rate Updated!*

New minimum: ${rate}/hour

{self.show_farmer_menu(from_number)}"""
        except ValueError:
            return "Please enter a valid number for the hourly rate. Example: 18"

    def handle_distance_update(self, from_number: str, distance: str) -> str:
        """Handle travel distance update - returns to menu after"""
        try:
            miles = int(distance)
            self.store.update_user_profile(from_number, {'max_distance': miles})
            self.store.clear_conversation_state(from_number)
            return f"""✅ *Travel Distance Updated!*

New max distance: {miles} miles

{self.show_farmer_menu(from_number)}"""
        except ValueError:
            return "Please enter a valid number. Example: 20"

    def handle_hours_update(self, from_number: str, choice: str) -> str:
        """Handle hours preference update - returns to menu after"""
        hours_map = {
            '1': 'full-time',
            '2': 'part-time',
            '3': 'flexible'
        }
        if choice.strip() in hours_map:
            hours = hours_map[choice.strip()]
            self.store.update_user_profile(from_number, {'hours_preference': hours})
            self.store.clear_conversation_state(from_number)
            return f"""✅ *Hours Preference Updated!*

New preference: {hours}

{self.show_farmer_menu(from_number)}"""
        else:
            return "Please reply with 1 (Full-time), 2 (Part-time), or 3 (Flexible)"

    def handle_actual_location_update(self, from_number: str, location: str) -> str:
        """Handle updating the actual location (city, state)"""
        self.store.update_user_profile(from_number, {'location': location.strip()})
        self.store.clear_conversation_state(from_number)
        return f"""✅ *Location Updated!*

New location: {location.strip()}

{self.show_farmer_menu(from_number)}"""

    def view_owner_jobs(self, from_number: str) -> str:
        """View jobs posted by farm owner"""
        all_jobs = self.store._read_json(self.store.jobs_file)
        owner_jobs = [j for j in all_jobs.values() if j.get('owner_phone') == from_number]

        if not owner_jobs:
            return "You haven't posted any jobs yet.\n\n" + self.show_owner_menu(from_number)

        msg = "📋 *Your Job Postings:*\n\n"
        
        for job in owner_jobs:
            matches = self.store.get_job_matches(job['job_id'])
            msg += f"""*{job['work_type']}*
                    Pay: ${job['pay_rate']}/hr
                    Status: {job['status']}
                    Applications: {len(matches)}
                    ━━━━━━━━━━━

                    """
            
        msg += self.show_owner_menu(from_number)
        return msg

    def show_help(self) -> str:
        """
        Show help message
        """

        return """❓ *FarmConnect Help*

        • Type 'menu' anytime to return to main menu
        • Type 'help' to see this message

        For support, contact: support@farmconnect.com"""
