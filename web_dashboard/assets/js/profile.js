/**
 * Profile page logic
 */

// Require authentication
if (!Auth.requireAuth()) {
    throw new Error('Unauthorized');
}

let profile = null;

/**
 * Load user profile
 */
async function loadProfile() {
    try {
        profile = await API.get(CONFIG.ENDPOINTS.PROFILE);
        
        // Update navbar
        document.getElementById('userName').textContent = profile.name;
        
        // Update profile card
        document.getElementById('profileName').textContent = profile.name;
        document.getElementById('profileEmail').textContent = profile.email;
        document.getElementById('profileRole').textContent = profile.role || 'User';
        document.getElementById('profilePhone').textContent = profile.phone || 'Not provided';
        document.getElementById('profileJoined').textContent = Utils.formatDate(profile.created_at);
        
        // Update form fields
        document.getElementById('updateName').value = profile.name;
        document.getElementById('updateEmail').value = profile.email;
        document.getElementById('updatePhone').value = profile.phone || '';
        
    } catch (error) {
        console.error('Error loading profile:', error);
        Utils.showError('Failed to load profile');
    }
}

/**
 * Handle update profile form
 */
const updateProfileForm = document.getElementById('updateProfileForm');
const profileAlert = document.getElementById('profileAlert');
const updateProfileBtnText = document.getElementById('updateProfileBtnText');
const updateProfileSpinner = document.getElementById('updateProfileSpinner');

updateProfileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('updateName').value;
    const email = document.getElementById('updateEmail').value;
    const phone = document.getElementById('updatePhone').value;
    
    profileAlert.classList.add('d-none');
    updateProfileBtnText.innerHTML = '<i class="bi bi-save"></i> Saving...';
    updateProfileSpinner.classList.remove('d-none');
    updateProfileForm.querySelector('button[type="submit"]').disabled = true;
    
    try {
        await API.put(CONFIG.ENDPOINTS.PROFILE, {
            name,
            email,
            phone: phone || null
        });
        
        // Update stored user data
        Auth.saveUserData({ ...profile, name, email, phone });
        
        profileAlert.textContent = 'Profile updated successfully!';
        profileAlert.classList.remove('alert-danger');
        profileAlert.classList.add('alert-success');
        profileAlert.classList.remove('d-none');
        
        // Reload profile
        setTimeout(() => {
            loadProfile();
        }, 1000);
        
    } catch (error) {
        profileAlert.textContent = error.message;
        profileAlert.classList.remove('alert-success');
        profileAlert.classList.add('alert-danger');
        profileAlert.classList.remove('d-none');
    } finally {
        updateProfileBtnText.innerHTML = '<i class="bi bi-save"></i> Save Changes';
        updateProfileSpinner.classList.add('d-none');
        updateProfileForm.querySelector('button[type="submit"]').disabled = false;
    }
});

/**
 * Handle change password form
 */
const changePasswordForm = document.getElementById('changePasswordForm');
const passwordAlert = document.getElementById('passwordAlert');
const changePasswordBtnText = document.getElementById('changePasswordBtnText');
const changePasswordSpinner = document.getElementById('changePasswordSpinner');

changePasswordForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmNewPassword = document.getElementById('confirmNewPassword').value;
    
    passwordAlert.classList.add('d-none');
    
    // Validate passwords match
    if (newPassword !== confirmNewPassword) {
        passwordAlert.textContent = 'New passwords do not match!';
        passwordAlert.classList.remove('alert-success');
        passwordAlert.classList.add('alert-danger');
        passwordAlert.classList.remove('d-none');
        return;
    }
    
    // Validate password length
    if (newPassword.length < 8) {
        passwordAlert.textContent = 'Password must be at least 8 characters long!';
        passwordAlert.classList.remove('alert-success');
        passwordAlert.classList.add('alert-danger');
        passwordAlert.classList.remove('d-none');
        return;
    }
    
    changePasswordBtnText.innerHTML = '<i class="bi bi-key"></i> Changing...';
    changePasswordSpinner.classList.remove('d-none');
    changePasswordForm.querySelector('button[type="submit"]').disabled = true;
    
    try {
        await API.post(CONFIG.ENDPOINTS.CHANGE_PASSWORD, {
            current_password: currentPassword,
            new_password: newPassword
        });
        
        passwordAlert.textContent = 'Password changed successfully!';
        passwordAlert.classList.remove('alert-danger');
        passwordAlert.classList.add('alert-success');
        passwordAlert.classList.remove('d-none');
        
        // Reset form
        changePasswordForm.reset();
        
    } catch (error) {
        passwordAlert.textContent = error.message || 'Failed to change password';
        passwordAlert.classList.remove('alert-success');
        passwordAlert.classList.add('alert-danger');
        passwordAlert.classList.remove('d-none');
    } finally {
        changePasswordBtnText.innerHTML = '<i class="bi bi-key"></i> Change Password';
        changePasswordSpinner.classList.add('d-none');
        changePasswordForm.querySelector('button[type="submit"]').disabled = false;
    }
});

// Load profile on page load
document.addEventListener('DOMContentLoaded', loadProfile);