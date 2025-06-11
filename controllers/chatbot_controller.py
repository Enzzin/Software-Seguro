from flask import Blueprint, request, jsonify
from models.chatbot_model import ChatbotModel

chatbot_controller = Blueprint('chatbot_controller', __name__)
chatbot_model = ChatbotModel()

@chatbot_controller.route('/api/chatbot', methods=['POST'])
def ask_chatbot():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "A 'message' is required."}), 400

    user_message = data['message']

    try:
        reply = chatbot_model.get_response(user_message)
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return jsonify({"error": "Não foi possível conectar ao serviço do chatbot. Verifique se o Ollama está em execução."}), 500 