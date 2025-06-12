import ollama
import os

class ChatbotModel:
    def __init__(self):
        ollama_host = os.environ.get('OLLAMA_HOST')
        self.client = ollama.Client(host=ollama_host)
        self.model = 'llama3.2'

    def get_response(self, message):
        response = self.client.chat(
            model=self.model,
            messages=[{'role': 'user', 'content': message}]
        )
        return response['message']['content']