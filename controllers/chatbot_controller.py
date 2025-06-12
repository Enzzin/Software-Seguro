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
        return jsonify({"error": "Unable to connect to the chatbot service. Please check if Ollama is running."}), 500 