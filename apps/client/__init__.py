'''

Serves as a middleman between Discord Bot and Quart API

Main purpose is to eliminate congestion and ease readability of Discord Bot
Handles all outgoing HTTPS requests and subsequent response data processing

Should be configured at runtime via environment variables

Configuration:
    - API Key (stored in .env file)
    - Client Secret (stored in .env file)
    - Client ID (provided by connected Discord Application)

Configuration should be authenticated every 10 minutes, and persistent between verifications

Should also perform infraction checks on users to ensure use of the application is permitted

'''
