import ollama

class ChatbotModel:
    def __init__(self):
        self.model = 'llama3.2'

    def get_response(self, message):
        response = ollama.chat(
            model=self.model,
            messages=[{'role': 'user', 'content': message}]
        )
        return response['message']['content'] 