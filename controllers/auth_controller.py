from flask import Blueprint, request, jsonify
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
        return jsonify({"message": "Nome, email e senha são obrigatórios."}), 400

    try:
        auth_model.register_user(email, password, given_name)
        return jsonify({"message": "Usuário cadastrado com sucesso. Verifique seu e-mail."}), 201
    except auth_model.cognito_client.exceptions.UsernameExistsException:
        return jsonify({"message": "Este email já está em uso."}), 409
    except auth_model.cognito_client.exceptions.InvalidParameterException as e:
        return jsonify({"message": f"Erro de parâmetro inválido: {str(e)}"}), 400
    except auth_model.cognito_client.exceptions.InvalidPasswordException:
        return jsonify({"message": "A senha não atende aos requisitos de segurança."}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@auth_controller.route('/api/confirm', methods=['POST'])
def confirm_user():
    data = request.get_json()
    email = data.get('email')
    confirmation_code = data.get('confirmationCode')

    if not all([email, confirmation_code]):
        return jsonify({"message": "Email e código de confirmação são obrigatórios."}), 400

    try:
        auth_model.confirm_user(email, confirmation_code)
        return jsonify({"message": "Conta confirmada com sucesso!"}), 200
    except auth_model.cognito_client.exceptions.CodeMismatchException:
        return jsonify({"message": "Código de confirmação inválido."}), 400
    except auth_model.cognito_client.exceptions.ExpiredCodeException:
        return jsonify({"message": "O código de confirmação expirou. Solicite um novo."}), 400
    except auth_model.cognito_client.exceptions.UserNotFoundException:
        return jsonify({"message": "Usuário não encontrado."}), 404
    except auth_model.cognito_client.exceptions.NotAuthorizedException:
        return jsonify({"message": "A conta já foi confirmada ou o usuário não pode ser confirmado."}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@auth_controller.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email e senha são obrigatórios."}), 400

    try:
        response = auth_model.login_user(email, password)
        access_token = response['AuthenticationResult']['AccessToken']
        return jsonify({"token": access_token}), 200
    except auth_model.cognito_client.exceptions.NotAuthorizedException:
        return jsonify({"message": "Email ou senha incorretos."}), 401
    except auth_model.cognito_client.exceptions.UserNotConfirmedException:
        return jsonify({"message": "Usuário não confirmado. Por favor, verifique seu e-mail."}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500 