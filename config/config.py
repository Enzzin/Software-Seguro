import os
from dotenv import load_dotenv

load_dotenv()

# Cognito Configuration
COGNITO_USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
COGNITO_APP_CLIENT_ID = os.environ.get('COGNITO_APP_CLIENT_ID')
COGNITO_APP_CLIENT_SECRET = os.environ.get('COGNITO_APP_CLIENT_SECRET')
COGNITO_REGION = os.environ.get('COGNITO_REGION', 'us-east-1')

# Validate required environment variables
if not all([COGNITO_USER_POOL_ID, COGNITO_APP_CLIENT_ID, COGNITO_APP_CLIENT_SECRET, COGNITO_REGION]):
    raise RuntimeError("Cognito environment variables were not loaded. Please check your .env file") 