import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI
from dotenv import load_dotenv
import threading
from flask import Flask

# Load environment variables
load_dotenv()

# Initialize OpenAI Client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize Slack App
slack_app = App(token=os.getenv('SLACK_BOT_TOKEN'))

app = Flask(__name__)

# Process message with OpenAI
def generate_response(message):
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful Slack assistant."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content


# Slack message handler
@slack_app.event("app_mention")
def handle_mention(event, say):
    user_message = event['text'].split('>')[1].strip()

    try:
        ai_response = generate_response(user_message)
        say(ai_response)
    except Exception as e:
        say(f"Error processing request: {str(e)}")

@app.route('/')
def health_check():
    return 'Bot is running!', 200

def run_flask():
    """Run Flask app for health checks"""
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def main():
    """Main function to start the bot and health check server."""
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True  # This ensures the Flask thread will stop when the main thread stops
    flask_thread.start()

    # Start the Slack bot
    handler = SocketModeHandler(slack_app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()

if __name__ == "__main__":
    main()