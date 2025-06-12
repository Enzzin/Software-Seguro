/* global fetch, URLSearchParams, localStorage */
document.addEventListener('DOMContentLoaded', () => {
    const loginForm    = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const confirmForm  = document.getElementById('confirmForm');

    /* utilitários ------------------------------------------------------------------- */
    const showError = (message, formId) => {
        const errorDiv   = document.querySelector(`#${formId} ~ #errorMessage`);
        const successDiv = document.querySelector(`#${formId} ~ #successMessage`);
        if (errorDiv)   { errorDiv.textContent = message; errorDiv.classList.remove('d-none'); }
        if (successDiv) { successDiv.classList.add('d-none'); }
    };

    const showSuccess = (message, formId) => {
        const successDiv = document.querySelector(`#${formId} ~ #successMessage`);
        const errorDiv   = document.querySelector(`#${formId} ~ #errorMessage`);
        if (successDiv) { successDiv.textContent = message; successDiv.classList.remove('d-none'); }
        if (errorDiv)   { errorDiv.classList.add('d-none'); }
    };

    /* registro ---------------------------------------------------------------------- */
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const givenName      = document.getElementById('givenName').value;
            const email          = document.getElementById('email').value;
            const password       = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            if (password !== confirmPassword) {
                showError('Passwords do not match.', 'registerForm');
                return;
            }

            try {
                const response = await fetch('/api/register', {
                    method : 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept'      : 'application/json'
                    },
                    body   : JSON.stringify({ givenName, email, password })
                });

                const isJson = response.headers.get('content-type')?.includes('application/json');
                const data   = isJson ? await response.json() : null;

                if (!response.ok) throw new Error(data?.message || 'Registration failed.');

                showSuccess('Registration successful! Redirecting...', 'registerForm');
                setTimeout(() => {
                    window.location.href = `/confirm?email=${encodeURIComponent(email)}`;
                }, 1500);
            } catch (err) {
                showError(err.message, 'registerForm');
            }
        });
    }

    /* confirmação ------------------------------------------------------------------- */
    if (confirmForm) {
        const urlParams   = new URLSearchParams(window.location.search);
        const emailFromQS = urlParams.get('email');
        if (emailFromQS) document.getElementById('email').value = emailFromQS;

        confirmForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email            = document.getElementById('email').value;
            const confirmationCode = document.getElementById('confirmationCode').value;

            try {
                const response = await fetch('/api/confirm', {
                    method : 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept'      : 'application/json'
                    },
                    body   : JSON.stringify({ email, confirmationCode })
                });

                const isJson = response.headers.get('content-type')?.includes('application/json');
                const data   = isJson ? await response.json() : null;

                if (!response.ok) throw new Error(data?.message || 'Confirmation failed.');

                showSuccess('Account confirmed! Redirecting...', 'confirmForm');
                setTimeout(() => { window.location.href = '/login'; }, 1500);
            } catch (err) {
                showError(err.message, 'confirmForm');
            }
        });
    }

    /* login ------------------------------------------------------------------------- */
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email    = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/api/login', {
                    method : 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept'      : 'application/json'
                    },
                    body   : JSON.stringify({ email, password })
                });

                const isJson = response.headers.get('content-type')?.includes('application/json');
                const data   = isJson ? await response.json() : null;

                if (!response.ok) throw new Error(data?.message || 'Invalid email or password.');

                /* salva token & redireciona */
                localStorage.setItem('authToken', data.token);
                window.location.href = '/dashboard';
            } catch (err) {
                showError(err.message, 'loginForm');
            }
        });
    }
});
