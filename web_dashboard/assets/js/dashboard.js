/**
 * Dashboard page logic
 */

// Require authentication
if (!Auth.requireAuth()) {
    throw new Error('Unauthorized');
}

// Get user data
const userData = Auth.getUserData();

// Update user name in navbar and welcome message
if (userData && userData.name) {
    document.getElementById('userName').textContent = userData.name;
    document.getElementById('userWelcome').textContent = userData.name;
}

// Dashboard data
let dashboardData = {
    devices: [],
    alerts: [],
    activeAlerts: [],
    guardians: []
};

/**
 * Load dashboard data
 */
async function loadDashboard() {
    try {
        // Load all data in parallel
        const [devices, alerts, activeAlerts, guardians] = await Promise.all([
            API.get(CONFIG.ENDPOINTS.DEVICES),
            API.get(CONFIG.ENDPOINTS.ALERTS + '?limit=5'),
            API.get(CONFIG.ENDPOINTS.ACTIVE_ALERTS),
            API.get(CONFIG.ENDPOINTS.GUARDIANS)
        ]);
        
        dashboardData.devices = devices;
        dashboardData.alerts = alerts;
        dashboardData.activeAlerts = activeAlerts;
        dashboardData.guardians = guardians;
        
        // Update UI
        updateStats();
        updateRecentAlerts();
        updateDeviceStatus();
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        Utils.showError('Failed to load dashboard data');
    }
}

/**
 * Update statistics cards
 */
function updateStats() {
    // Count active devices (status = online)
    const activeDevices = dashboardData.devices.filter(d => d.status === 'online').length;
    document.getElementById('activeDevices').textContent = activeDevices;
    
    // Total alerts
    document.getElementById('totalAlerts').textContent = dashboardData.alerts.length || 0;
    
    // Active alerts
    document.getElementById('activeAlerts').textContent = dashboardData.activeAlerts.length || 0;
    document.getElementById('alertCount').textContent = dashboardData.activeAlerts.length || 0;
    
    // Total guardians
    document.getElementById('totalGuardians').textContent = dashboardData.guardians.length || 0;
}

/**
 * Update recent alerts table
 */
function updateRecentAlerts() {
    const tableBody = document.getElementById('recentAlertsTable');
    
    if (!dashboardData.alerts || dashboardData.alerts.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center py-4 text-muted">
                    <i class="bi bi-inbox" style="font-size: 2rem;"></i>
                    <p class="mt-2 mb-0">No alerts yet</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = '';
    
    dashboardData.alerts.slice(0, 5).forEach(alert => {
        const statusInfo = CONFIG.ALERT_STATUS[alert.status] || { label: alert.status, class: 'secondary' };
        const alertType = CONFIG.ALERT_TYPES[alert.alert_type] || alert.alert_type;
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${Utils.formatDate(alert.timestamp)}</td>
            <td><span class="badge bg-${alert.alert_type === 'manual_trigger' ? 'primary' : 'info'}">${alertType}</span></td>
            <td>
                ${alert.latitude && alert.longitude ? 
                    `<a href="${Utils.getMapUrl(alert.latitude, alert.longitude)}" target="_blank" class="text-decoration-none">
                        <i class="bi bi-geo-alt"></i> View Map
                    </a>` : 
                    '<span class="text-muted">N/A</span>'
                }
            </td>
            <td><span class="badge bg-${statusInfo.class}">${statusInfo.label}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewAlert(${alert.id})">
                    <i class="bi bi-eye"></i> View
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

/**
 * Update device status list
 */
function updateDeviceStatus() {
    const deviceList = document.getElementById('deviceStatusList');
    
    if (!dashboardData.devices || dashboardData.devices.length === 0) {
        deviceList.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="bi bi-phone-x" style="font-size: 2rem;"></i>
                <p class="mt-2 mb-0">No devices registered</p>
                <a href="devices.html" class="btn btn-sm btn-primary mt-2">Add Device</a>
            </div>
        `;
        return;
    }
    
    deviceList.innerHTML = '';
    
    dashboardData.devices.forEach(device => {
        const statusColor = CONFIG.STATUS_COLORS[device.status] || 'secondary';
        
        const deviceCard = document.createElement('div');
        deviceCard.className = 'card device-card mb-3 ' + device.status;
        deviceCard.innerHTML = `
            <div class="card-body p-3">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">${device.device_name || 'Device ' + device.id}</h6>
                        <small class="text-muted">${device.device_token.substring(0, 16)}...</small>
                    </div>
                    <span class="badge bg-${statusColor}">
                        <span class="status-dot ${device.status}"></span>
                        ${device.status}
                    </span>
                </div>
                ${device.battery_level ? `
                    <div class="progress mt-2" style="height: 8px;">
                        <div class="progress-bar ${device.battery_level < 20 ? 'bg-danger' : device.battery_level < 50 ? 'bg-warning' : 'bg-success'}" 
                             style="width: ${device.battery_level}%"></div>
                    </div>
                    <small class="text-muted">Battery: ${device.battery_level}%</small>
                ` : ''}
                ${device.last_heartbeat ? `
                    <div class="mt-2">
                        <small class="text-muted"><i class="bi bi-clock"></i> ${Utils.formatDate(device.last_heartbeat)}</small>
                    </div>
                ` : ''}
            </div>
        `;
        deviceList.appendChild(deviceCard);
    });
}

/**
 * View alert details
 */
function viewAlert(alertId) {
    window.location.href = `alerts.html?id=${alertId}`;
}

/**
 * Auto-refresh alerts
 */
let refreshInterval;

function startAutoRefresh() {
    refreshInterval = setInterval(() => {
        loadDashboard();
    }, CONFIG.ALERT_REFRESH_INTERVAL);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    startAutoRefresh();
});

// Stop refresh when page is hidden
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
    }
});