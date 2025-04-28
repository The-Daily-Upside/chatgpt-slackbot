import os
import logging
from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from dotenv import load_dotenv
from openai import OpenAI
import psycopg2
from psycopg2.extras import RealDictCursor
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Environment variables
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
BOT_NAME = os.getenv("BOT_NAME", "ChatGPTBot")
PORT = int(os.getenv("PORT", 3000))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # Default to gpt-4o if not set
OPENAI_INSTRUCTIONS = os.getenv("OPENAI_INSTRUCTIONS", "You are a helpful assistant.")  # Default instructions

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Connect to the database
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

# Initialize the database
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS threads (
        id SERIAL PRIMARY KEY,
        thread_ts TEXT NOT NULL,
        channel TEXT NOT NULL,
        user_id TEXT NOT NULL,
        message TEXT NOT NULL,
        role TEXT NOT NULL, -- 'user' or 'assistant'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

# Call this function at the start of your app
initialize_database()

def store_message(thread_ts, channel, user_id, message, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO threads (thread_ts, channel, user_id, message, role)
    VALUES (%s, %s, %s, %s, %s)
    """, (thread_ts, channel, user_id, message, role))
    conn.commit()
    conn.close()

def get_thread_history(thread_ts):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT message, role FROM threads
    WHERE thread_ts = %s
    ORDER BY created_at ASC
    """, (thread_ts,))
    messages = cursor.fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["message"]} for row in messages]

def preprocess_for_slack(text):
    """
    Preprocess text to ensure it uses Slack's Markdown syntax.
    """
    # Replace Markdown-style bold with Slack-style bold
    text = text.replace("**", "*")  # Convert **bold** to *bold*
    text = text.replace("__", "_")  # Convert __italic__ to _italic_

    # Replace Markdown headings with bold text
    text = text.replace("# ", "*").replace("## ", "*").replace("### ", "*")

    # Replace Markdown links with Slack-style links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"<\2|\1>", text)

    return text

# Initialize Slack app
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)

# Initialize Flask app
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# Route for Slack events
@flask_app.route("/events", methods=["POST"])
def slack_events():
    """Handle incoming Slack events."""
    # Log the request
    app.logger.info(f"Received request: {request.json}")
    # Respond to Slack's challenge verification
    if "challenge" in request.json:
        return jsonify({"challenge": request.json["challenge"]})
    # Handle other events
    return handler.handle(request)

def process_event(event, say, logger, is_direct_message=False):
    try:
        logger.info(f"Processing event: {event}")

        # Extract the channel, user, and message text
        channel = event["channel"]
        user = event["user"]
        text = event.get("text", "").strip()
        thread_ts = event.get("thread_ts") or event["ts"]  # Use thread_ts or start a new thread
        logger.info(f"Channel: {channel}, User: {user}, Text: {text}, Thread TS: {thread_ts}")

        # If it's not a direct message, remove the bot mention
        if not is_direct_message:
            bot_user_id = app.client.auth_test()["user_id"]
            text = text.replace(f"<@{bot_user_id}>", "").strip()
            logger.info(f"Processed text after removing bot mention: {text}")

        # Store the user's message in the database
        store_message(thread_ts, channel, user, text, "user")

        # Retrieve thread history from the database
        messages = get_thread_history(thread_ts)

        # Add the current user message to the conversation
        messages.append({"role": "user", "content": text})

        # Call OpenAI API with the conversation history
        logger.info(f"Sending message to OpenAI with context: {messages}")
        response = openai_client.responses.create(
            model=OPENAI_MODEL,
            instructions=OPENAI_INSTRUCTIONS,
            input=messages,
        )

        # Extract the response text
        gpt_response = response.output_text
        logger.info(f"Received response from OpenAI: {gpt_response}")

        # Preprocess the response for Slack Markdown
        gpt_response = preprocess_for_slack(gpt_response)

        # Store the bot's response in the database
        bot_user_id = app.client.auth_test()["user_id"]
        store_message(thread_ts, channel, bot_user_id, gpt_response, "assistant")

        # Send the formatted response back to the Slack channel
        say(
            text=gpt_response,  # Fallback text
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": gpt_response  # OpenAI's response as Markdown
                    }
                }
            ],
            thread_ts=thread_ts  # Reply in the thread
        )
        logger.info(f"Message sent successfully to channel {channel}")

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        say(text="Sorry, something went wrong.")

# Event listener for app mentions
@app.event("app_mention")
def handle_app_mention_events(event, say, logger):
    logger.info("Handling app_mention event")
    process_event(event, say, logger, is_direct_message=False)

@app.event("message")
def handle_message_events(event, say, logger):
    logger.info("Handling message event")
    
    # Filter for direct messages
    if event.get("channel_type") != "im":
        logger.info("Ignoring non-direct message event.")
        return

    process_event(event, say, logger, is_direct_message=True)

if __name__ == "__main__":
    # Run Flask app
    flask_app.run(host="0.0.0.0", port=PORT)