import boto3
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')

COGNITO_USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
COGNITO_APP_CLIENT_ID = os.environ.get('COGNITO_APP_CLIENT_ID')
COGNITO_REGION = os.environ.get('COGNITO_REGION', 'us-east-1')

# Inicializa o cliente do Cognito
cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

# --- Rotas da API (Nosso Controlador) ---

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email e senha são obrigatórios."}), 400

    try:
        # Tenta criar o usuário no Cognito User Pool
        response = cognito_client.sign_up(
            ClientId=COGNITO_APP_CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[{'Name': 'email', 'Value': email}]
        )
        return jsonify({"message": "Usuário cadastrado com sucesso. Verifique seu e-mail."}), 201
    except cognito_client.exceptions.UsernameExistsException:
        return jsonify({"message": "Este email já está em uso."}), 409
    except cognito_client.exceptions.InvalidPasswordException:
        return jsonify({"message": "A senha não atende aos requisitos de segurança."}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email e senha são obrigatórios."}), 400

    try:
        # Tenta autenticar o usuário
        response = cognito_client.initiate_auth(
            ClientId=COGNITO_APP_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME': email, 'PASSWORD': password}
        )
        # Se o login for bem-sucedido, o Cognito retorna um token de acesso
        access_token = response['AuthenticationResult']['AccessToken']
        return jsonify({"token": access_token}), 200
    except cognito_client.exceptions.NotAuthorizedException:
        return jsonify({"message": "Email ou senha incorretos."}), 401
    except cognito_client.exceptions.UserNotConfirmedException:
         return jsonify({"message": "Usuário não confirmado. Por favor, verifique seu e-mail."}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# --- Rotas para servir as Views (páginas HTML) ---
@app.route('/')
@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/cadastro.html')
def register_page():
    return render_template('cadastro.html')

# Rota protegida de exemplo
@app.route('/dashboard.html')
def dashboard():
    # Aqui você adicionaria a lógica para verificar o token JWT antes de servir a página
    return "<h1>Bem-vindo ao Dashboard! (Página Protegida)</h1>"


if __name__ == '__main__':
    app.run(debug=True, port=5000)