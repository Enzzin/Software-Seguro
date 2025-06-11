import boto3
import hmac
import hashlib
import base64
from config.config import (
    COGNITO_APP_CLIENT_ID,
    COGNITO_APP_CLIENT_SECRET,
    COGNITO_REGION
)

class AuthModel:
    def __init__(self):
        self.cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

    def get_secret_hash(self, username):
        msg = username + COGNITO_APP_CLIENT_ID
        dig = hmac.new(
            str(COGNITO_APP_CLIENT_SECRET).encode('utf-8'),
            msg=str(msg).encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()

    def register_user(self, email, password, given_name):
        secret_hash = self.get_secret_hash(email)
        user_attributes = [
            {'Name': 'email', 'Value': email},
            {'Name': 'given_name', 'Value': given_name}
        ]
        
        return self.cognito_client.sign_up(
            ClientId=COGNITO_APP_CLIENT_ID,
            SecretHash=secret_hash,
            Username=email,
            Password=password,
            UserAttributes=user_attributes
        )

    def confirm_user(self, email, confirmation_code):
        secret_hash = self.get_secret_hash(email)
        return self.cognito_client.confirm_sign_up(
            ClientId=COGNITO_APP_CLIENT_ID,
            SecretHash=secret_hash,
            Username=email,
            ConfirmationCode=confirmation_code
        )

    def login_user(self, email, password):
        secret_hash = self.get_secret_hash(email)
        return self.cognito_client.initiate_auth(
            ClientId=COGNITO_APP_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password,
                'SECRET_HASH': secret_hash
            }
        ) 