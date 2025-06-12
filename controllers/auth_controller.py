from flask import Blueprint, request, jsonify, session
from models.auth_model import AuthModel

auth_controller = Blueprint('auth_controller', __name__)
auth_model = AuthModel()

@auth_controller.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    given_name = data.get('givenName')
    email = data.get('email')
    password = data.get('password')

    if not all([given_name, email, password]):
        return jsonify({"message": "Name, email and password are required."}), 400

    try:
        auth_model.register_user(email, password, given_name)
        return jsonify({"message": "User registered successfully. Please check your email."}), 201
    except auth_model.cognito_client.exceptions.UsernameExistsException:
        return jsonify({"message": "This email is already in use."}), 409
    except auth_model.cognito_client.exceptions.InvalidParameterException as e:
        return jsonify({"message": f"Invalid parameter error: {str(e)}"}), 400
    except auth_model.cognito_client.exceptions.InvalidPasswordException:
        return jsonify({"message": "Password does not meet security requirements."}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@auth_controller.route('/api/confirm', methods=['POST'])
def confirm_user():
    data = request.get_json()
    email = data.get('email')
    confirmation_code = data.get('confirmationCode')

    if not all([email, confirmation_code]):
        return jsonify({"message": "Email and confirmation code are required."}), 400

    try:
        auth_model.confirm_user(email, confirmation_code)
        return jsonify({"message": "Account confirmed successfully!"}), 200
    except auth_model.cognito_client.exceptions.CodeMismatchException:
        return jsonify({"message": "Invalid confirmation code."}), 400
    except auth_model.cognito_client.exceptions.ExpiredCodeException:
        return jsonify({"message": "Confirmation code has expired. Please request a new one."}), 400
    except auth_model.cognito_client.exceptions.UserNotFoundException:
        return jsonify({"message": "User not found."}), 404
    except auth_model.cognito_client.exceptions.NotAuthorizedException:
        return jsonify({"message": "Account already confirmed or user cannot be confirmed."}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@auth_controller.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    try:
        response = auth_model.login_user(email, password)
        access_token = response['AuthenticationResult']['AccessToken']
        session['auth_token'] = access_token
        return jsonify({"token": access_token}), 200
    except auth_model.cognito_client.exceptions.NotAuthorizedException:
        return jsonify({"message": "Incorrect email or password."}), 401
    except auth_model.cognito_client.exceptions.UserNotConfirmedException:
        return jsonify({"message": "User not confirmed. Please check your email."}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500 