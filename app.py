import boto3
from flask import Flask, request, jsonify, render_template
import os
import ollama #biblioteca do Ollama
import hmac  
import hashlib 
import base64 
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')

#Configuração do Cognito
COGNITO_USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
COGNITO_APP_CLIENT_ID = os.environ.get('COGNITO_APP_CLIENT_ID')
COGNITO_APP_CLIENT_SECRET = os.environ.get('COGNITO_APP_CLIENT_SECRET') # Carrega o Client Secret
COGNITO_REGION = os.environ.get('COGNITO_REGION', 'us-east-1')

if not all([COGNITO_USER_POOL_ID, COGNITO_APP_CLIENT_ID, COGNITO_APP_CLIENT_SECRET, COGNITO_REGION]):
    raise RuntimeError("Variáveis de ambiente do Cognito não foram carregadas. Verifique seu arquivo .env")

cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

#Função para calcular o Secret Hash
def get_secret_hash(username):
    msg = username + COGNITO_APP_CLIENT_ID
    dig = hmac.new(
        str(COGNITO_APP_CLIENT_SECRET).encode('utf-8'),
        msg=str(msg).encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()

#Rotas da API de Autenticacao

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    given_name = data.get('givenName')
    email = data.get('email')
    password = data.get('password')

    if not all([given_name, email, password]):
        return jsonify({"message": "Nome, email e senha são obrigatórios."}), 400

    try:
        # Calcula o hash secreto para chamada de registro
        secret_hash = get_secret_hash(email)

        user_attributes = [
            {'Name': 'email', 'Value': email},
            {'Name': 'given_name', 'Value': given_name}
        ]
        
        response = cognito_client.sign_up(
            ClientId=COGNITO_APP_CLIENT_ID,
            SecretHash=secret_hash,
            Username=email,
            Password=password,
            UserAttributes=user_attributes
        )
        return jsonify({"message": "Usuário cadastrado com sucesso. Verifique seu e-mail."}), 201
    except cognito_client.exceptions.UsernameExistsException:
        return jsonify({"message": "Este email já está em uso."}), 409
    except cognito_client.exceptions.InvalidParameterException as e:
        return jsonify({"message": f"Erro de parâmetro inválido: {str(e)}"}), 400
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
        secret_hash = get_secret_hash(email)
        
        response = cognito_client.initiate_auth(
            ClientId=COGNITO_APP_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email, 
                'PASSWORD': password,
                'SECRET_HASH': secret_hash
            }
        )
        access_token = response['AuthenticationResult']['AccessToken']
        return jsonify({"token": access_token}), 200
    except cognito_client.exceptions.NotAuthorizedException:
        return jsonify({"message": "Email ou senha incorretos."}), 401
    except cognito_client.exceptions.UserNotConfirmedException:
         return jsonify({"message": "Usuário não confirmado. Por favor, verifique seu e-mail."}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    
# Rota da API do Chatbot (Conexão Local)
# Ollama deve estar rodando localmente na porta padrao
@app.route('/api/chatbot', methods=['POST'])
def ask_chatbot():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "A 'message' is required."}), 400

    user_message = data['message']

    try:
        # Chama o modelo Ollama rodando localmente
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': user_message}]
        )
        
        reply = response['message']['content']
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return jsonify({"error": "Não foi possível conectar ao serviço do chatbot. Verifique se o Ollama está em execução."}), 500

@app.route('/')
@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/cadastro.html')
def register_page():
    return render_template('cadastro.html')
    
@app.route('/chatbot.html')
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/dashboard.html')
def dashboard():
    return "<h1>Bem-vindo ao Dashboard! (Página Protegida)</h1>"


if __name__ == '__main__':
    app.run(debug=True, port=5000)