// Alerts Page JavaScript

const API_BASE = window.location.origin;
const token = localStorage.getItem('token');
let currentAlertId = null;
let alertMap = null;

// Load alerts on page load
document.addEventListener('DOMContentLoaded', function() {
    loadAlerts();
    initializeFilters();
});

async function loadAlerts() {
    const container = document.getElementById('alertsContainer');
    container.innerHTML = '<div class="col-12 text-center py-5"><div class="spinner-border"></div></div>';

    try {
        const response = await fetch(`${API_BASE}/api/alerts`, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        
        const alerts = await response.json();
        displayAlerts(alerts);
        updateSummary(alerts);
    } catch (error) {
        container.innerHTML = `<div class="col-12"><div class="alert alert-danger">Error loading alerts: ${error.message}</div></div>`;
    }
}

function displayAlerts(alerts) {
    const container = document.getElementById('alertsContainer');
    
    if (alerts.length === 0) {
        container.innerHTML = '<div class="col-12 text-center py-5"><p class="text-muted">No alerts found</p></div>';
        return;
    }

    container.innerHTML = alerts.map(alert => `
        <div class="col-md-6 col-lg-4">
            <div class="glass-card p-3 alert-card" data-alert-id="${alert.id}" onclick="showAlertDetail(${alert.id})" style="cursor: pointer;">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="mb-0">📱 ${alert.device_uid}</h6>
                    <span class="badge bg-${getStatusColor(alert.status)}">${alert.status}</span>
                </div>
                <p class="mb-1"><strong>Reason:</strong> <span class="badge bg-warning text-dark">${alert.reason}</span></p>
                <p class="mb-1"><strong>Severity:</strong> <span class="badge bg-${getSeverityColor(alert.severity)}">${alert.severity}</span></p>
                <p class="mb-1 small text-muted">
                    <i class="bi bi-clock"></i> ${formatTime(alert.timestamp)}
                </p>
                <p class="mb-0 small text-muted">
                    <i class="bi bi-geo-alt"></i> ${alert.lat ? `${alert.lat.toFixed(4)}, ${alert.lng.toFixed(4)}` : 'No location'}
                </p>
            </div>
        </div>
    `).join('');
}

async function showAlertDetail(alertId) {
    currentAlertId = alertId;
    
    try {
        const response = await fetch(`${API_BASE}/api/alerts/${alertId}`, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        
        const alert = await response.json();
        
        document.getElementById('modalAlertId').textContent = alert.id;
        document.getElementById('modalDevice').textContent = alert.device_uid;
        document.getElementById('modalReason').innerHTML = `<span class="badge bg-warning text-dark">${alert.reason}</span>`;
        document.getElementById('modalSeverity').innerHTML = `<span class="badge bg-${getSeverityColor(alert.severity || 'MEDIUM')}">${alert.severity || 'MEDIUM'}</span>`;
        document.getElementById('modalStatus').innerHTML = `<span class="badge bg-${getStatusColor(alert.status)}">${alert.status}</span>`;
        document.getElementById('modalTime').textContent = formatTime(alert.timestamp);
        document.getElementById('modalCoords').textContent = alert.gps_lat ? `${alert.gps_lat.toFixed(6)}, ${alert.gps_lng.toFixed(6)}` : 'Not available';
        
        // Show evidence
        const evidenceDiv = document.getElementById('modalEvidence');
        if (alert.evidence && alert.evidence.length > 0) {
            evidenceDiv.innerHTML = alert.evidence.map(ev => `
                <div class="mb-2">
                    <strong>${ev.type}:</strong> 
                    ${ev.type === 'AUDIO' ? `<audio controls class="w-100 mt-1"><source src="/static/evidence/${ev.path}"></audio>` : 
                      ev.type === 'IMAGE' ? `<img src="/static/evidence/${ev.path}" class="img-fluid mt-1" style="max-height: 200px;">` : 
                      ev.path}
                </div>
            `).join('');
        } else {
            evidenceDiv.innerHTML = '<p class="text-muted">No evidence files</p>';
        }
        
        // Initialize map
        if (alert.gps_lat && alert.gps_lng) {
            setTimeout(() => initAlertMap(alert.gps_lat, alert.gps_lng), 300);
        }
        
        const modal = new bootstrap.Modal(document.getElementById('alertDetailModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading alert details:', error);
    }
}

function initAlertMap(lat, lng) {
    const mapDiv = document.getElementById('modalMap');
    if (alertMap) {
        alertMap.remove();
    }
    
    alertMap = L.map('modalMap').setView([lat, lng], 15);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(alertMap);
    L.marker([lat, lng]).addTo(alertMap).bindPopup('Alert Location').openPopup();
}

async function updateAlertStatus(status) {
    if (!currentAlertId) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/alerts/${currentAlertId}/status`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({status})
        });
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('alertDetailModal')).hide();
            loadAlerts();
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

function updateSummary(alerts) {
    document.getElementById('totalAlerts').textContent = alerts.length;
    document.getElementById('newCount').textContent = alerts.filter(a => a.status === 'NEW').length;
    document.getElementById('progressCount').textContent = alerts.filter(a => a.status === 'IN_PROGRESS').length;
    document.getElementById('resolvedCount').textContent = alerts.filter(a => a.status === 'RESOLVED').length;
}

function initializeFilters() {
    document.getElementById('applyFilters').addEventListener('click', loadAlerts);
    document.getElementById('refreshAlerts').addEventListener('click', loadAlerts);
}

function getStatusColor(status) {
    const colors = {NEW: 'danger', IN_PROGRESS: 'warning', RESOLVED: 'success'};
    return colors[status] || 'secondary';
}

function getSeverityColor(severity) {
    const colors = {HIGH: 'danger', MEDIUM: 'warning', LOW: 'info'};
    return colors[severity] || 'secondary';
}

function formatTime(timestamp) {
    return new Date(timestamp).toLocaleString();
}
