# ChatGPT Slackbot

## Overview

The ChatGPT Slackbot is an internal tool developed for **[The Daily Upside](https://www.thedailyupside.com)**. This bot integrates OpenAI's ChatGPT with Slack, enabling your team to efficiently interact with AI-powered assistance directly within your Slack workspace. It is tailored for company-specific workflows and is deployed on DigitalOcean, leveraging a managed database for persistent storage and configuration.

## Features

- **Slack Integration**: Seamlessly interact with ChatGPT in Slack channels and direct messages.
- **Threaded Conversations**: Keeps messages and responses in a Slack thread for better organization and context.
- **Message Persistence**: Stores messages and responses in a managed database, allowing the bot to use previous messages in the thread for context in subsequent responses.
- **Data Privacy**: Uses `user=user` when calling the OpenAI API to ensure data is not used for retraining.
- **Database Integration**: Stores configurations, logs, and conversation history in a managed database.

## Custom RAG Implementation

If you want to use a custom Retrieval-Augmented Generation (RAG) with this bot, the `rag` branch includes an implementation using Chroma and embeddings.

## Deployment Instructions

### Prerequisites

- Access to your Slack Bot Token and OpenAI API Key.
- A PostgreSQL database.
- A server that can run a Flask app.

### Setup Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/The-Daily-Upside/chatgpt-slackbot.git
cd chatgpt-slackbot
```

#### 2. Set Up a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Create a `.env` file from the `.env.example` with the following variables:

```plaintext
SLACK_BOT_TOKEN=
SLACK_SIGNING_SECRET=
OPENAI_API_KEY=
DATABASE_URL=
```

Leave the placeholders empty for now. You will configure these after setting up your Slack app.

#### 5. Start the Application

Start the Flask app on your server. This step is necessary because Slack's event subscription requires the app to be running to verify the challenge request.

```bash
python app.py
```

#### 6. Create Your Slack App

1. Go to the [Slack API](https://api.slack.com/apps) and create a new app.
2. Under **Event Subscriptions**, set the **Request URL** to your server's `/events` endpoint (e.g., `https://your-domain.com/events`).
3. Slack will send a challenge request to verify the endpoint. Ensure the app is running so it can respond to the challenge.
4. Once the challenge is verified, you can proceed to configure the app's permissions and tokens.

#### 7. Configure Tokens in `.env`

After creating the Slack app, update the `.env` file with the following values:

```plaintext
SLACK_BOT_TOKEN=your-slack-bot-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=your-database-url
```

Save the file and restart the application.

```bash
python app.py
```

## Sample Slack App Manifest

To set up your Slack app, you can use the following manifest file. This manifest defines the bot's name, description, permissions, and event subscriptions.

```json
{
    "display_information": {
        "name": "ChatGPTBot",
        "description": "ChatGPT Bot",
        "background_color": "#590088"
    },
    "features": {
        "bot_user": {
            "display_name": "ChatGPTBot",
            "always_online": true
        }
    },
    "oauth_config": {
        "scopes": {
            "bot": [
                "app_mentions:read",
                "channels:history",
                "chat:write",
                "im:read",
                "im:history",
                "assistant:write"
            ]
        }
    },
    "settings": {
        "event_subscriptions": {
            "request_url": "https://your-domain.com/events",
            "bot_events": [
                "app_mention",
                "message.im"
            ]
        },
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "token_rotation_enabled": false
    }
}
```

Replace `https://your-domain.com/events` with your actual server URL.

## Usage

Once deployed, your team can interact with the bot in Slack by:

- Mentioning the bot in a channel: `@ChatGPTBot help`
- Sending direct commands in a DM: `generate summary for meeting notes`

## Contributions

Contributions are welcome! If you’d like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push the branch.
4. Open a pull request describing your changes.

Feel free to open issues for bug reports or feature requests.

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.
