# app.py
from flask import Flask, render_template
from config.config import config          # <-- dicionário de configurações
from extensions import init_extensions   
from controllers.auth_controller import auth_controller
from controllers.chatbot_controller import chatbot_controller
from controllers.phish_controller import phish_controller
from utils.auth_decorators import login_required


app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static",
    template_folder="templates",
)

# configuração
app.config.from_object(config["default"])
init_extensions(app)

# blueprints
app.register_blueprint(auth_controller)
app.register_blueprint(chatbot_controller)
app.register_blueprint(phish_controller)

# rotas de visualização
@app.route("/")
@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/confirm")
def confirm_page():
    return render_template("confirm.html")

@app.route("/chatbot")
@login_required
def chatbot_page():
    return render_template("chatbot.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/health")
def health_check():
    from extensions import db
    try:
        db.session.execute("SELECT 1")
        return {"status": "healthy"}, 200
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}, 503


app.run(host="0.0.0.0", port=8000, debug=True)
