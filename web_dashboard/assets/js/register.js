/**
 * Register page logic
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

// Handle registration form submission
const registerForm = document.getElementById('registerForm');
const alertMessage = document.getElementById('alertMessage');
const registerBtnText = document.getElementById('registerBtnText');
const registerSpinner = document.getElementById('registerSpinner');

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form data
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const role = document.getElementById('role').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const terms = document.getElementById('terms').checked;
    
    // Clear previous alerts
    alertMessage.classList.add('d-none');
    
    // Validate password match
    if (password !== confirmPassword) {
        alertMessage.textContent = 'Passwords do not match!';
        alertMessage.classList.remove('alert-success');
        alertMessage.classList.add('alert-danger');
        alertMessage.classList.remove('d-none');
        return;
    }
    
    // Validate password length
    if (password.length < 8) {
        alertMessage.textContent = 'Password must be at least 8 characters long!';
        alertMessage.classList.remove('alert-success');
        alertMessage.classList.add('alert-danger');
        alertMessage.classList.remove('d-none');
        return;
    }
    
    // Validate terms
    if (!terms) {
        alertMessage.textContent = 'You must agree to the Terms & Conditions!';
        alertMessage.classList.remove('alert-success');
        alertMessage.classList.add('alert-danger');
        alertMessage.classList.remove('d-none');
        return;
    }
    
    // Show loading state
    registerBtnText.textContent = 'Creating Account...';
    registerSpinner.classList.remove('d-none');
    registerForm.querySelector('button[type="submit"]').disabled = true;
    
    try {
        // Prepare registration data
        const registrationData = {
            name,
            email,
            password,
            role
        };
        
        // Add phone if provided
        if (phone) {
            registrationData.phone = phone;
        }
        
        // Call register API
        await API.post(CONFIG.ENDPOINTS.REGISTER, registrationData);
        
        // Show success message
        alertMessage.textContent = 'Registration successful! Redirecting to login...';
        alertMessage.classList.remove('alert-danger');
        alertMessage.classList.add('alert-success');
        alertMessage.classList.remove('d-none');
        
        // Redirect to login page
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);
        
    } catch (error) {
        // Show error message
        alertMessage.textContent = error.message || 'Registration failed. Please try again.';
        alertMessage.classList.remove('alert-success');
        alertMessage.classList.add('alert-danger');
        alertMessage.classList.remove('d-none');
        
        // Reset button state
        registerBtnText.textContent = 'Create Account';
        registerSpinner.classList.add('d-none');
        registerForm.querySelector('button[type="submit"]').disabled = false;
    }
});