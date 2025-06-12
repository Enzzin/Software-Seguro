from flask import Flask, render_template
from controllers.auth_controller import auth_controller
from controllers.chatbot_controller import chatbot_controller
from utils.auth_decorators import login_required
from config.config import FLASK_SECRET_KEY

app = Flask(__name__, static_folder='static', static_url_path='', template_folder='templates')
app.secret_key = FLASK_SECRET_KEY

# Register Blueprints
app.register_blueprint(auth_controller)
app.register_blueprint(chatbot_controller)

# View routes
@app.route('/')
@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/register.html')
def register_page():
    return render_template('register.html')
    
@app.route('/confirm.html')
def confirm_page():
    return render_template('confirm.html')

@app.route('/chatbot.html')
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/dashboard.html')
@login_required
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
