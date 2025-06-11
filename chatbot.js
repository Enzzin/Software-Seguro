document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatWindow = document.getElementById('chat-window');
    const errorMessage = document.getElementById('errorMessage');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        // Mostra a mensagem do usuário
        appendMessage(message, 'user');
        
        userInput.value = '';
        userInput.disabled = true;

        try {
            // Chama a API do backend
            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Ocorreu um erro desconhecido.');
            }

            const data = await response.json();
            
            // Mostra a resposta do bot
            appendMessage(data.reply, 'bot');
            errorMessage.classList.add('d-none');

        } catch (error) {
            errorMessage.textContent = error.message;
            errorMessage.classList.remove('d-none');
        } finally {
            userInput.disabled = false;
            userInput.focus();
        }
    });

    function appendMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', `${sender}-message`);

        const p = document.createElement('p');
        p.textContent = text;
        
        messageDiv.appendChild(p);
        chatWindow.appendChild(messageDiv);
        
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
});