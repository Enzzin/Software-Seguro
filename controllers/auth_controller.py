# controllers/auth_controller.py
"""
Autenticação via AWS Cognito + sessão Flask
------------------------------------------
• Salva o token **e o e-mail do usuário** em session
• Inclui rota /logout para limpar a sessão
"""
from flask import Blueprint, request, jsonify, session, redirect, url_for
from models.auth_model import AuthModel

auth_controller = Blueprint("auth_controller", __name__)
auth_model      = AuthModel()


# ────────────────────────────────────────────────────────────────────
# REGISTRO
# ────────────────────────────────────────────────────────────────────
@auth_controller.route("/api/register", methods=["POST"])
def register_user():
    data         = request.get_json() or {}
    given_name   = data.get("givenName")
    email        = data.get("email")
    password     = data.get("password")

    if not all([given_name, email, password]):
        return jsonify(message="Name, e-mail and password are required."), 400

    try:
        auth_model.register_user(email, password, given_name)
        return jsonify(message="User registered. Check your inbox."), 201
    except auth_model.cognito_client.exceptions.UsernameExistsException:
        return jsonify(message="E-mail already in use."), 409
    except auth_model.cognito_client.exceptions.InvalidPasswordException:
        return jsonify(message="Password does not meet security requirements."), 400
    except Exception as exc:
        return jsonify(message=str(exc)), 500


# ────────────────────────────────────────────────────────────────────
# CONFIRMAÇÃO
# ────────────────────────────────────────────────────────────────────
@auth_controller.route("/api/confirm", methods=["POST"])
def confirm_user():
    data    = request.get_json() or {}
    email   = data.get("email")
    code    = data.get("confirmationCode")

    if not (email and code):
        return jsonify(message="E-mail and confirmation code are required."), 400

    try:
        auth_model.confirm_user(email, code)
        return jsonify(message="Account confirmed!"), 200
    except auth_model.cognito_client.exceptions.CodeMismatchException:
        return jsonify(message="Invalid confirmation code."), 400
    except auth_model.cognito_client.exceptions.ExpiredCodeException:
        return jsonify(message="Code expired. Request a new one."), 400
    except Exception as exc:
        return jsonify(message=str(exc)), 500


# ────────────────────────────────────────────────────────────────────
# LOGIN  (→ aqui gravamos token **e** e-mail na sessão)
# ────────────────────────────────────────────────────────────────────
@auth_controller.route("/api/login", methods=["POST"])
def login_user():
    data      = request.get_json() or {}
    email     = data.get("email")
    password  = data.get("password")

    if not (email and password):
        return jsonify(message="E-mail and password are required."), 400

    try:
        resp      = auth_model.login_user(email, password)
        token     = resp["AuthenticationResult"]["AccessToken"]

        # ──>  salva na sessão ───────────────────────────────────────
        session["auth_token"] = token
        session["email"]      = email                       # <── AQUI
        # se quiser mostrar o nome na navbar:
        session["user_name"]  = email.split("@")[0]
        # ────────────────────────────────────────────────────────────

        return jsonify(token=token), 200
    except auth_model.cognito_client.exceptions.NotAuthorizedException:
        return jsonify(message="Incorrect e-mail or password."), 401
    except auth_model.cognito_client.exceptions.UserNotConfirmedException:
        return jsonify(message="Account not confirmed."), 401
    except Exception as exc:
        return jsonify(message=str(exc)), 500


# ────────────────────────────────────────────────────────────────────
# LOGOUT
# ────────────────────────────────────────────────────────────────────
@auth_controller.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))
