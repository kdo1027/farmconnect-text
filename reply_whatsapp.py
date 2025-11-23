from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from chatbot import FarmConnectBot
import sys

app = Flask(__name__)
bot = FarmConnectBot()

@app.route("/reply_whatsapp", methods=['POST'])
def reply_whatsapp():
	try:
		# Get incoming message data
		from_number = request.form.get('From', '')
		message_body = request.form.get('Body', '').strip()
		media_url = request.form.get('MediaUrl0', None)  # For image uploads

		print(f"📩 Received from {from_number}: {message_body}")

		# Handle special commands
		if message_body.lower() == 'menu':
			user = bot.store.get_user(from_number)
			if user and user.get('registered'):
				bot.store.clear_conversation_state(from_number)
				response_text = bot.show_main_menu(from_number, user)
			else:
				response_text = bot.show_welcome_menu(from_number)
		elif message_body.lower() == 'help':
			response_text = bot.show_help()
		else:
			# Check if user is at main menu and selecting an option
			user = bot.store.get_user(from_number)
			conv_state = bot.store.get_conversation_state(from_number)

			if user and user.get('registered') and not conv_state and message_body.isdigit():
				response_text = bot.handle_menu_selection(from_number, user, message_body)
			else:
				# Process message through chatbot
				response_text = bot.handle_message(from_number, message_body, media_url)

		# Create TwiML response
		resp = MessagingResponse()
		resp.message(response_text)

		print(f"📤 Sending response: {response_text[:100]}...")  # Show first 100 chars
		print(f"📋 TwiML: {str(resp)[:200]}...")

		return Response(str(resp), mimetype='text/xml')

	except Exception as e:
		print(f"Error processing message: {e}", file=sys.stderr)
		# Send error message to user
		resp = MessagingResponse()
		resp.message("Sorry, something went wrong. Please try again or type 'menu' for main menu.")
		return Response(str(resp), mimetype='text/xml')

@app.route("/", methods=['GET'])
def home():
	return """
	<h1>🌾 FarmConnect WhatsApp Bot</h1>
	<p>Webhook is running!</p>
	<p>Configure your Twilio webhook to point to: <code>/reply_whatsapp</code></p>
	"""

if __name__ == "__main__":
	print("🌾 FarmConnect Bot starting...")
	print("📱 Webhook endpoint: http://localhost:3000/reply_whatsapp")
	print("🌐 Expose with ngrok: ngrok http 3000")
	app.run(port=3000, debug=True)