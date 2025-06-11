document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    // Manipulador de erros para mostrar mensagens ao usuário
    const showError = (message) => {
        const errorDiv = document.getElementById('errorMessage');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('d-none');
        }
        const successDiv = document.getElementById('successMessage');
        if (successDiv) {
            successDiv.classList.add('d-none');
        }
    };
    
    // Manipulador de sucesso
    const showSuccess = (message) => {
        const successDiv = document.getElementById('successMessage');
        if (successDiv) {
            successDiv.textContent = message;
            successDiv.classList.remove('d-none');
        }
        const errorDiv = document.getElementById('errorMessage');
        if (errorDiv) {
            errorDiv.classList.add('d-none');
        }
    };

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // Impede o recarregamento da página
            
            // Lê os valores de todos os campos
            const givenName = document.getElementById('givenName').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            if (password !== confirmPassword) {
                showError('As senhas não coincidem. Por favor, tente novamente.');
                return; // Para a execução se as senhas forem diferentes
            }

            try {
                // Usando fetch para chamar nosso backend com todos os dados
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    // Envia o givenName junto com os outros dados
                    body: JSON.stringify({ givenName, email, password }) 
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.message || 'Falha ao cadastrar.');
                }
                
                showSuccess('Cadastro realizado com sucesso! Verifique seu e-mail para confirmar a conta.');
                registerForm.reset();

            } catch (error) {
                showError(error.message);
            }
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.message || 'Email ou senha inválidos.');
                }
                
                localStorage.setItem('authToken', data.token);
                window.location.href = '/dashboard.html';

            } catch (error) {
                showError(error.message);
            }
        });
    }
});
