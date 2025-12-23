// Admin Panel JavaScript

const API_BASE = window.location.origin;
const token = localStorage.getItem('token');

document.addEventListener('DOMContentLoaded', function() {
    loadStatistics();
    setInterval(loadStatistics, 60000); // Refresh every minute
});

async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE}/api/admin/stats`, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        
        const stats = await response.json();
        
        document.getElementById('totalUsers').textContent = stats.total_users || 0;
        document.getElementById('activeDevices').textContent = stats.active_devices || 0;
        document.getElementById('newAlerts').textContent = stats.alerts_by_status?.NEW || 0;
        
        // Recent activity
        if (stats.latest_alerts) {
            const tbody = document.getElementById('recentActivityTable');
            tbody.innerHTML = stats.latest_alerts.map(alert => `
                <tr>
                    <td>${new Date(alert.time).toLocaleTimeString()}</td>
                    <td>${alert.device}</td>
                    <td><span class="badge bg-warning">${alert.reason}</span></td>
                    <td><span class="badge bg-danger">NEW</span></td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Add user form
document.getElementById('addUserForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData);
    
    try {
        const response = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert('User created successfully!');
            bootstrap.Modal.getInstance(document.getElementById('addUserModal')).hide();
            this.reset();
        }
    } catch (error) {
        alert('Error creating user: ' + error.message);
    }
});
