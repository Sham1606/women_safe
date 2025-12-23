// Profile Page JavaScript

const API_BASE = window.location.origin;
const token = localStorage.getItem('token');

document.addEventListener('DOMContentLoaded', function() {
    loadProfile();
});

async function loadProfile() {
    try {
        const response = await fetch(`${API_BASE}/api/auth/me`, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        
        const user = await response.json();
        
        document.getElementById('profileName').textContent = user.name;
        document.getElementById('profileRole').textContent = user.role;
        document.getElementById('name').value = user.name;
        document.getElementById('email').value = user.email;
        document.getElementById('phone').value = user.phone || '';
        document.getElementById('role').value = user.role;
        
        // Load stats (if guardian)
        if (user.role === 'GUARDIAN') {
            loadUserStats();
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

async function loadUserStats() {
    try {
        const devicesRes = await fetch(`${API_BASE}/api/device/my-devices`, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        const devices = await devicesRes.json();
        document.getElementById('devicesCount').textContent = devices.length;
        
        const alertsRes = await fetch(`${API_BASE}/api/alerts`, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        const alerts = await alertsRes.json();
        document.getElementById('alertsCount').textContent = alerts.length;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

document.getElementById('profileForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Profile update endpoint would go here
    alert('Profile update feature coming soon!');
});

document.getElementById('passwordForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const newPass = document.getElementById('newPassword').value;
    const confirmPass = document.getElementById('confirmPassword').value;
    
    if (newPass !== confirmPass) {
        alert('Passwords do not match!');
        return;
    }
    
    // Password change endpoint would go here
    alert('Password change feature coming soon!');
});
