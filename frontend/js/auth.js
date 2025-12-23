const API_URL = 'http://127.0.0.1:5000/api/auth';

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
            window.location.href = 'dashboard.html';
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
            showAlert('Registration successful! Please login.', 'success');
            setTimeout(() => {
                document.getElementById('login-tab').click();
            }, 1000);
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (err) {
        showAlert('Registration failed: ' + err, 'danger');
    }
});

function showAlert(msg, type) {
    const div = document.getElementById('alertMsg');
    div.innerHTML = `<div class="alert alert-${type}">${msg}</div>`;
}
