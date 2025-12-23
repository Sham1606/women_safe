/**
 * Alerts page logic
 */

// Require authentication
if (!Auth.requireAuth()) {
    throw new Error('Unauthorized');
}

// Get user data
const userData = Auth.getUserData();
if (userData && userData.name) {
    document.getElementById('userName').textContent = userData.name;
}

let alerts = [];
let devices = [];
let currentFilters = {
    status: '',
    type: '',
    device_id: ''
};

/**
 * Load devices for filter dropdown
 */
async function loadDevicesFilter() {
    try {
        devices = await API.get(CONFIG.ENDPOINTS.DEVICES);
        const filterDevice = document.getElementById('filterDevice');
        
        devices.forEach(device => {
            const option = document.createElement('option');
            option.value = device.id;
            option.textContent = device.device_name || `Device ${device.id}`;
            filterDevice.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading devices:', error);
    }
}

/**
 * Load alerts
 */
async function loadAlerts() {
    const tableBody = document.getElementById('alertsTableBody');
    
    try {
        // Build query string from filters
        let queryParams = [];
        if (currentFilters.status) queryParams.push(`status=${currentFilters.status}`);
        if (currentFilters.type) queryParams.push(`alert_type=${currentFilters.type}`);
        if (currentFilters.device_id) queryParams.push(`device_id=${currentFilters.device_id}`);
        
        const queryString = queryParams.length > 0 ? '?' + queryParams.join('&') : '';
        
        alerts = await API.get(CONFIG.ENDPOINTS.ALERTS + queryString);
        
        // Update alert count
        const activeAlerts = await API.get(CONFIG.ENDPOINTS.ACTIVE_ALERTS);
        document.getElementById('alertCount').textContent = activeAlerts.length || 0;
        
        if (alerts.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-5">
                        <div class="empty-state">
                            <i class="bi bi-inbox"></i>
                            <h5>No Alerts Found</h5>
                            <p class="text-muted">No alerts match your current filters</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }
        
        tableBody.innerHTML = '';
        
        alerts.forEach(alert => {
            const statusInfo = CONFIG.ALERT_STATUS[alert.status] || { label: alert.status, class: 'secondary' };
            const alertType = CONFIG.ALERT_TYPES[alert.alert_type] || alert.alert_type;
            const device = devices.find(d => d.id === alert.device_id);
            
            const row = document.createElement('tr');
            row.className = alert.status === 'active' ? 'table-danger' : '';
            row.innerHTML = `
                <td><strong>#${alert.id}</strong></td>
                <td>${Utils.formatDate(alert.timestamp)}</td>
                <td><span class="badge bg-${alert.alert_type === 'manual_trigger' ? 'primary' : 'info'}">${alertType}</span></td>
                <td>${device ? device.device_name || `Device ${device.id}` : 'Unknown'}</td>
                <td>
                    ${alert.latitude && alert.longitude ? 
                        `<a href="${Utils.getMapUrl(alert.latitude, alert.longitude)}" target="_blank" class="text-decoration-none">
                            <i class="bi bi-geo-alt"></i> View
                        </a>` : 
                        '<span class="text-muted">N/A</span>'
                    }
                </td>
                <td><span class="badge bg-${statusInfo.class}">${statusInfo.label}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewAlertDetails(${alert.id})">
                        <i class="bi bi-eye"></i>
                    </button>
                    ${alert.status === 'active' ? `
                        <button class="btn btn-sm btn-outline-warning" onclick="acknowledgeAlert(${alert.id})" title="Acknowledge">
                            <i class="bi bi-check-circle"></i>
                        </button>
                    ` : ''}
                </td>
            `;
            tableBody.appendChild(row);
        });
        
    } catch (error) {
        console.error('Error loading alerts:', error);
        Utils.showError('Failed to load alerts');
    }
}

/**
 * Apply filters
 */
function applyFilters() {
    currentFilters.status = document.getElementById('filterStatus').value;
    currentFilters.type = document.getElementById('filterType').value;
    currentFilters.device_id = document.getElementById('filterDevice').value;
    
    loadAlerts();
}

/**
 * View alert details
 */
async function viewAlertDetails(alertId) {
    const modal = new bootstrap.Modal(document.getElementById('alertDetailsModal'));
    const content = document.getElementById('alertDetailsContent');
    const actions = document.getElementById('alertDetailsActions');
    
    content.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';
    modal.show();
    
    try {
        const alert = await API.get(CONFIG.ENDPOINTS.ALERT_DETAIL(alertId));
        const device = devices.find(d => d.id === alert.device_id);
        const statusInfo = CONFIG.ALERT_STATUS[alert.status] || { label: alert.status, class: 'secondary' };
        
        // Get evidence
        let evidence = [];
        try {
            evidence = await API.get(CONFIG.ENDPOINTS.EVIDENCE_BY_ALERT(alertId));
        } catch (e) {
            console.log('No evidence found');
        }
        
        content.innerHTML = `
            <div class="row">
                <div class="col-md-6 mb-3">
                    <h6>Alert Information</h6>
                    <table class="table table-sm">
                        <tr>
                            <th>Alert ID:</th>
                            <td>#${alert.id}</td>
                        </tr>
                        <tr>
                            <th>Type:</th>
                            <td><span class="badge bg-${alert.alert_type === 'manual_trigger' ? 'primary' : 'info'}">${CONFIG.ALERT_TYPES[alert.alert_type]}</span></td>
                        </tr>
                        <tr>
                            <th>Status:</th>
                            <td><span class="badge bg-${statusInfo.class}">${statusInfo.label}</span></td>
                        </tr>
                        <tr>
                            <th>Device:</th>
                            <td>${device ? device.device_name || `Device ${device.id}` : 'Unknown'}</td>
                        </tr>
                        <tr>
                            <th>Timestamp:</th>
                            <td>${Utils.formatDate(alert.timestamp)}</td>
                        </tr>
                        <tr>
                            <th>Priority:</th>
                            <td><span class="badge bg-danger">${alert.priority || 'High'}</span></td>
                        </tr>
                    </table>
                </div>
                <div class="col-md-6 mb-3">
                    <h6>Physiological Data</h6>
                    <table class="table table-sm">
                        <tr>
                            <th>Heart Rate:</th>
                            <td>${alert.heart_rate ? alert.heart_rate + ' bpm' : 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Temperature:</th>
                            <td>${alert.temperature ? alert.temperature + ' °C' : 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Stress Score:</th>
                            <td>${alert.stress_score ? (alert.stress_score * 100).toFixed(1) + '%' : 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Confidence:</th>
                            <td>${alert.confidence ? (alert.confidence * 100).toFixed(1) + '%' : 'N/A'}</td>
                        </tr>
                    </table>
                    
                    <h6 class="mt-3">Location</h6>
                    ${alert.latitude && alert.longitude ? `
                        <p><strong>Coordinates:</strong><br>${Utils.formatLocation(alert.latitude, alert.longitude)}</p>
                        <a href="${Utils.getMapUrl(alert.latitude, alert.longitude)}" target="_blank" class="btn btn-outline-primary btn-sm">
                            <i class="bi bi-map"></i> View on Google Maps
                        </a>
                    ` : '<p class="text-muted">Location not available</p>'}
                </div>
            </div>
            
            ${evidence.length > 0 ? `
                <div class="row mt-3">
                    <div class="col-12">
                        <h6>Evidence (${evidence.length})</h6>
                        <div class="row">
                            ${evidence.map(e => `
                                <div class="col-md-4 mb-2">
                                    <div class="card">
                                        <div class="card-body">
                                            <p class="mb-1"><strong>Type:</strong> ${e.evidence_type}</p>
                                            <p class="mb-1"><strong>Time:</strong> ${Utils.formatDate(e.captured_at)}</p>
                                            <button class="btn btn-sm btn-primary" onclick="window.open('${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.EVIDENCE_DOWNLOAD(e.id)}', '_blank')">
                                                <i class="bi bi-download"></i> Download
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            ` : ''}
        `;
        
        // Action buttons
        actions.innerHTML = `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            ${alert.status === 'active' ? `
                <button type="button" class="btn btn-warning" onclick="acknowledgeAlertFromModal(${alert.id})">
                    <i class="bi bi-check-circle"></i> Acknowledge
                </button>
                <button type="button" class="btn btn-success" onclick="resolveAlertFromModal(${alert.id})">
                    <i class="bi bi-check2-all"></i> Resolve
                </button>
                <button type="button" class="btn btn-outline-secondary" onclick="markFalseAlarmFromModal(${alert.id})">
                    <i class="bi bi-x-circle"></i> False Alarm
                </button>
            ` : ''}
        `;
        
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load alert details: ${error.message}</div>`;
    }
}

/**
 * Acknowledge alert
 */
async function acknowledgeAlert(alertId) {
    try {
        await API.post(CONFIG.ENDPOINTS.ACKNOWLEDGE_ALERT(alertId), {});
        Utils.showSuccess('Alert acknowledged');
        loadAlerts();
    } catch (error) {
        Utils.showError('Failed to acknowledge alert: ' + error.message);
    }
}

async function acknowledgeAlertFromModal(alertId) {
    await acknowledgeAlert(alertId);
    bootstrap.Modal.getInstance(document.getElementById('alertDetailsModal')).hide();
}

/**
 * Resolve alert
 */
async function resolveAlertFromModal(alertId) {
    try {
        await API.post(CONFIG.ENDPOINTS.RESOLVE_ALERT(alertId), {});
        Utils.showSuccess('Alert resolved');
        bootstrap.Modal.getInstance(document.getElementById('alertDetailsModal')).hide();
        loadAlerts();
    } catch (error) {
        Utils.showError('Failed to resolve alert: ' + error.message);
    }
}

/**
 * Mark as false alarm
 */
async function markFalseAlarmFromModal(alertId) {
    if (!confirm('Mark this as a false alarm?')) return;
    
    try {
        await API.post(CONFIG.ENDPOINTS.FALSE_ALARM(alertId), {});
        Utils.showSuccess('Marked as false alarm');
        bootstrap.Modal.getInstance(document.getElementById('alertDetailsModal')).hide();
        loadAlerts();
    } catch (error) {
        Utils.showError('Failed to mark as false alarm: ' + error.message);
    }
}

// Auto-refresh alerts
let refreshInterval;

function startAutoRefresh() {
    refreshInterval = setInterval(loadAlerts, CONFIG.ALERT_REFRESH_INTERVAL);
}

function stopAutoRefresh() {
    if (refreshInterval) clearInterval(refreshInterval);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadDevicesFilter();
    loadAlerts();
    startAutoRefresh();
});

document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
    }
});