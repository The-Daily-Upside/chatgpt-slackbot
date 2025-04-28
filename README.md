# ChatGPT Slackbot

## Overview

The ChatGPT Slackbot is an internal tool developed for **The Daily Upside**. This bot integrates OpenAI's ChatGPT with Slack, enabling your team to efficiently interact with AI-powered assistance directly within your Slack workspace. It is tailored for company-specific workflows and is deployed on DigitalOcean, leveraging a managed database for persistent storage and configuration.

## Features

- **Slack Integration**: Seamlessly interact with ChatGPT in Slack channels and direct messages.
- **Company-Specific Customization**: Designed to meet the unique needs of your organization.
- **Database Integration**: Stores configurations and logs in a managed database.

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
SLACK_BOT_TOKEN=your-slack-bot-token
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=your-database-url
```

Replace placeholders with your specific credentials.

#### 5. Start the Application

```bash
python app.py
```

## Usage

Once deployed, your team can interact with the bot in Slack by:

- Mentioning the bot in a channel: `@ChatGPTBot help`
- Sending direct commands in a DM: `generate summary for meeting notes`

Contributions
Contributions are welcome! If you’d like to contribute to this project, please follow these steps:

Fork the repository.
Create a new branch for your feature or bug fix:
Commit your changes and push the branch:
Open a pull request describing your changes.
Feel free to open issues for bug reports or feature requests.

License
This project is licensed under the MIT License. See the LICENSE file for details. 
