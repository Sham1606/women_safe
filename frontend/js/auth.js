const API_URL = '/api/auth';

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const result = await res.json();
        
        if (res.ok) {
            localStorage.setItem('token', result.access_token);
            localStorage.setItem('user', JSON.stringify(result.user));
            // Redirect to Flask dashboard route
            window.location.href = '/dashboard';
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (err) {
        showAlert('Login failed: ' + err, 'danger');
    }
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    try {
        const res = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const result = await res.json();
        
        if (res.ok) {
            showAlert('Registration successful! Logging you in...', 'success');
            // Auto-login after registration
            setTimeout(() => {
                const loginData = {
                    email: data.email,
                    password: data.password
                };
                fetch(`${API_URL}/login`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(loginData)
                })
                .then(res => res.json())
                .then(result => {
                    if (result.access_token) {
                        localStorage.setItem('token', result.access_token);
                        localStorage.setItem('user', JSON.stringify(result.user));
                        window.location.href = '/dashboard';
                    }
                });
            }, 1000);
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (err) {
        showAlert('Registration failed: ' + err, 'danger');
    }
});

function showAlert(msg, type) {
    const box = document.getElementById('messageBox');
    box.className = `mt-4 text-center p-2 rounded alert alert-${type}`;
    box.textContent = msg;
    box.classList.remove('d-none');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        box.classList.add('d-none');
    }, 5000);
}
