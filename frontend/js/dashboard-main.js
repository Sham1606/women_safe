/**
 * Main Dashboard JavaScript
 * Handles role-based dashboard functionality
 */

let map;
let deviceMarkers = {};
let currentUser = null;

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', async function() {
    // Check authentication
    if (!isAuthenticated()) {
        window.location.href = 'index.html';
        return;
    }

    // Get current user
    currentUser = getCurrentUser();
    updateUserInfo();

    // Initialize map
    initializeMap();

    // Load dashboard data
    await loadDashboardData();

    // Initialize WebSocket for real-time alerts
    initializeWebSocket();

    // Setup auto-refresh
    setInterval(refreshDashboard, 30000); // Refresh every 30 seconds
});

function updateUserInfo() {
    document.getElementById('userName').textContent = currentUser.name || 'User';
    document.getElementById('userRole').textContent = currentUser.role.toUpperCase();

    // Show/hide sections based on role
    if (currentUser.role === 'police' || currentUser.role === 'admin') {
        document.getElementById('adminNav').style.display = 'block';
    }
}

function initializeMap() {
    // Initialize Leaflet map
    map = L.map('map').setView([20.5937, 78.9629], 5); // India center

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
}

async function loadDashboardData() {
    try {
        showLoading();

        // Load stats
        await loadStats();

        // Load recent alerts
        await loadRecentAlerts();

        // Load device locations
        await loadDeviceLocations();

        hideLoading();
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        showError('Failed to load dashboard data');
    }
}

async function loadStats() {
    try {
        const stats = await apiGet('/api/v1/dashboard/stats');

        document.getElementById('deviceCount').textContent = stats.device_count || 0;
        document.getElementById('alertCount').textContent = stats.active_alerts || 0;
        document.getElementById('notificationCount').textContent = stats.notifications || 0;
        
        const statusEl = document.getElementById('systemStatus');
        statusEl.textContent = stats.system_status || 'Normal';
        
        // Update status color
        const card = statusEl.closest('.card');
        if (stats.active_alerts > 0) {
            card.classList.remove('bg-success');
            card.classList.add('bg-danger');
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

async function loadRecentAlerts() {
    try {
        const alerts = await apiGet('/api/v1/alerts/recent');
        const tbody = document.querySelector('#recentAlertsTable tbody');
        tbody.innerHTML = '';

        if (alerts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No recent alerts</td></tr>';
            return;
        }

        alerts.forEach(alert => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${formatDateTime(alert.created_at)}</td>
                <td>${alert.device_name}</td>
                <td><span class="badge ${alert.alert_type === 'manual_trigger' ? 'bg-danger' : 'bg-warning'}">
                    ${alert.alert_type.replace('_', ' ').toUpperCase()}
                </span></td>
                <td>${alert.latitude.toFixed(4)}, ${alert.longitude.toFixed(4)}</td>
                <td><span class="badge ${alert.status === 'active' ? 'bg-danger' : 'bg-success'}">
                    ${alert.status.toUpperCase()}
                </span></td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="viewAlertDetails(${alert.id})">
                        <i class="bi bi-eye"></i> View
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Failed to load alerts:', error);
    }
}

async function loadDeviceLocations() {
    try {
        const devices = await apiGet('/api/v1/devices/locations');

        // Clear existing markers
        Object.values(deviceMarkers).forEach(marker => map.removeLayer(marker));
        deviceMarkers = {};

        // Add device markers
        devices.forEach(device => {
            if (device.latitude && device.longitude) {
                const marker = L.marker([device.latitude, device.longitude])
                    .addTo(map)
                    .bindPopup(`
                        <strong>${device.device_name}</strong><br>
                        Status: ${device.status}<br>
                        Battery: ${device.battery_level}%<br>
                        Last Update: ${formatDateTime(device.last_heartbeat)}
                    `);

                deviceMarkers[device.id] = marker;
            }
        });

        // Fit map to show all markers
        if (Object.keys(deviceMarkers).length > 0) {
            const group = L.featureGroup(Object.values(deviceMarkers));
            map.fitBounds(group.getBounds().pad(0.1));
        }
    } catch (error) {
        console.error('Failed to load device locations:', error);
    }
}

function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });

    // Show selected section
    document.getElementById(sectionName + 'Section').style.display = 'block';

    // Update active nav link
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.closest('.nav-link').classList.add('active');
}

async function viewAlertDetails(alertId) {
    try {
        const alert = await apiGet(`/api/v1/alerts/${alertId}`);
        
        // Populate modal with alert details
        document.getElementById('emergencyModalBody').innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Alert Information</h6>
                    <p><strong>Type:</strong> ${alert.alert_type}</p>
                    <p><strong>Time:</strong> ${formatDateTime(alert.created_at)}</p>
                    <p><strong>Device:</strong> ${alert.device_name}</p>
                    <p><strong>Status:</strong> ${alert.status}</p>
                </div>
                <div class="col-md-6">
                    <h6>Location</h6>
                    <p><strong>Coordinates:</strong> ${alert.latitude}, ${alert.longitude}</p>
                    <div id="alertMap" style="height: 200px;"></div>
                </div>
            </div>
            <hr>
            <h6>Evidence</h6>
            <div id="alertEvidence"></div>
        `;

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('emergencyModal'));
        modal.show();

        // Load evidence
        loadAlertEvidence(alertId);
    } catch (error) {
        console.error('Failed to load alert details:', error);
        showError('Failed to load alert details');
    }
}

async function loadAlertEvidence(alertId) {
    try {
        const evidence = await apiGet(`/api/v1/evidence/${alertId}`);
        const container = document.getElementById('alertEvidence');

        if (evidence.length === 0) {
            container.innerHTML = '<p class="text-muted">No evidence available</p>';
            return;
        }

        container.innerHTML = evidence.map(e => `
            <div class="evidence-item">
                ${e.evidence_type === 'photo' ? 
                    `<img src="${e.file_url}" class="img-thumbnail" style="max-width: 200px;">` :
                    `<a href="${e.file_url}" target="_blank" class="btn btn-sm btn-primary">
                        <i class="bi bi-${e.evidence_type === 'video' ? 'play' : 'file-earmark'}"></i>
                        View ${e.evidence_type}
                    </a>`
                }
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load evidence:', error);
    }
}

function acknowledgeAlert() {
    // TODO: Implement alert acknowledgment
    showSuccess('Alert acknowledged');
}

function registerDevice() {
    // TODO: Implement device registration
    alert('Device registration coming soon');
}

async function refreshDashboard() {
    await loadDashboardData();
}

function logout() {
    clearAuth();
    window.location.href = 'index.html';
}

// Utility functions
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

function showLoading() {
    // TODO: Implement loading indicator
}

function hideLoading() {
    // TODO: Hide loading indicator
}

function showError(message) {
    alert('Error: ' + message);
}

function showSuccess(message) {
    alert('Success: ' + message);
}
