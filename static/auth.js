document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const confirmForm = document.getElementById('confirmForm');

    // Function to display error messages for a specific form
    const showError = (message, formId) => {
        const errorDiv = document.querySelector(`#${formId} ~ #errorMessage`);
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('d-none'); 
        }

        const successDiv = document.querySelector(`#${formId} ~ #successMessage`);
        if (successDiv) {
            successDiv.classList.add('d-none');
        }
    };
    
    // Function to display success messages for a specific form
    const showSuccess = (message, formId) => {
        const successDiv = document.querySelector(`#${formId} ~ #successMessage`);
        if (successDiv) {
            successDiv.textContent = message;
            successDiv.classList.remove('d-none');
        }

        const errorDiv = document.querySelector(`#${formId} ~ #errorMessage`);
        if (errorDiv) {
            errorDiv.classList.add('d-none');
        }
    };

    // Registration form logic
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const givenName = document.getElementById('givenName').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            if (password !== confirmPassword) {
                showError('Passwords do not match.', 'registerForm');
                return;
            }

            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ givenName, email, password }) 
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.message);
                
                showSuccess('Registration successful! Redirecting to confirmation...', 'registerForm');
                setTimeout(() => {
                    window.location.href = `/confirm.html?email=${encodeURIComponent(email)}`;
                }, 2000);

            } catch (error) {
                showError(error.message, 'registerForm');
            }
        });
    }

    // Confirmation form logic
    if (confirmForm) {
        const urlParams = new URLSearchParams(window.location.search);
        const emailFromUrl = urlParams.get('email');
        if (emailFromUrl) {
            document.getElementById('email').value = emailFromUrl;
        }

        confirmForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const confirmationCode = document.getElementById('confirmationCode').value;

            try {
                const response = await fetch('/api/confirm', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, confirmationCode })
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.message);
                
                showSuccess('Account confirmed successfully! Redirecting to login...', 'confirmForm');
                setTimeout(() => {
                    window.location.href = '/login.html';
                }, 2000);

            } catch (error) {
                showError(error.message, 'confirmForm');
            }
        });
    }

    // Login form logic
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
                    throw new Error(data.message || 'Invalid email or password.');
                }
                
                localStorage.setItem('authToken', data.token);
                window.location.href = '/dashboard.html';

            } catch (error) {
                showError(error.message, 'loginForm');
            }
        });
    }
});