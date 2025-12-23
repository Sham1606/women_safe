/**
 * Login page logic
 */

// Redirect if already authenticated
Auth.redirectIfAuthenticated();

// Toggle password visibility
const togglePassword = document.getElementById('togglePassword');
const passwordInput = document.getElementById('password');
const eyeIcon = document.getElementById('eyeIcon');

togglePassword.addEventListener('click', () => {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    eyeIcon.classList.toggle('bi-eye');
    eyeIcon.classList.toggle('bi-eye-slash');
});

// Handle login form submission
const loginForm = document.getElementById('loginForm');
const alertMessage = document.getElementById('alertMessage');
const loginBtnText = document.getElementById('loginBtnText');
const loginSpinner = document.getElementById('loginSpinner');

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form data
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const rememberMe = document.getElementById('rememberMe').checked;
    
    // Clear previous alerts
    alertMessage.classList.add('d-none');
    
    // Show loading state
    loginBtnText.textContent = 'Signing In...';
    loginSpinner.classList.remove('d-none');
    loginForm.querySelector('button[type="submit"]').disabled = true;
    
    try {
        // Call login API
        const response = await API.post(CONFIG.ENDPOINTS.LOGIN, {
            email,
            password
        });
        
        // Save tokens
        Auth.saveTokens(response.access_token, response.refresh_token);
        
        // Get user profile
        const profile = await API.get(CONFIG.ENDPOINTS.PROFILE);
        Auth.saveUserData(profile);
        
        // Show success message
        alertMessage.textContent = 'Login successful! Redirecting...';
        alertMessage.classList.remove('alert-danger');
        alertMessage.classList.add('alert-success');
        alertMessage.classList.remove('d-none');
        
        // Redirect to dashboard
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
        
    } catch (error) {
        // Show error message
        alertMessage.textContent = error.message || 'Login failed. Please check your credentials.';
        alertMessage.classList.remove('alert-success');
        alertMessage.classList.add('alert-danger');
        alertMessage.classList.remove('d-none');
        
        // Reset button state
        loginBtnText.textContent = 'Sign In';
        loginSpinner.classList.add('d-none');
        loginForm.querySelector('button[type="submit"]').disabled = false;
    }
});