/**
 * Devices page logic
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

let devices = [];

/**
 * Load devices list
 */
async function loadDevices() {
    const devicesList = document.getElementById('devicesList');
    
    try {
        devices = await API.get(CONFIG.ENDPOINTS.DEVICES);
        
        if (devices.length === 0) {
            devicesList.innerHTML = `
                <div class="col-12">
                    <div class="empty-state">
                        <i class="bi bi-phone-x"></i>
                        <h4>No Devices Registered</h4>
                        <p class="text-muted">Register your ESP32 safety device to get started</p>
                        <button class="btn btn-primary mt-3" data-bs-toggle="modal" data-bs-target="#addDeviceModal">
                            <i class="bi bi-plus-circle"></i> Register Device
                        </button>
                    </div>
                </div>
            `;
            return;
        }
        
        devicesList.innerHTML = '';
        
        devices.forEach(device => {
            const statusColor = CONFIG.STATUS_COLORS[device.status] || 'secondary';
            const lastSeen = device.last_heartbeat ? Utils.formatDate(device.last_heartbeat) : 'Never';
            
            const col = document.createElement('div');
            col.className = 'col-lg-4 col-md-6 mb-4';
            col.innerHTML = `
                <div class="card border-0 shadow-sm device-card ${device.status}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div>
                                <h5 class="card-title mb-1">${device.device_name || 'Device ' + device.id}</h5>
                                <small class="text-muted">ID: ${device.id}</small>
                            </div>
                            <span class="badge bg-${statusColor}">
                                <span class="status-dot ${device.status}"></span>
                                ${device.status}
                            </span>
                        </div>
                        
                        <div class="mb-3">
                            <small class="text-muted d-block">Device Token:</small>
                            <code class="small">${device.device_token.substring(0, 32)}...</code>
                        </div>
                        
                        ${device.battery_level !== null ? `
                            <div class="mb-3">
                                <div class="d-flex justify-content-between mb-1">
                                    <small>Battery Level</small>
                                    <small class="fw-bold">${device.battery_level}%</small>
                                </div>
                                <div class="progress" style="height: 10px;">
                                    <div class="progress-bar ${device.battery_level < 20 ? 'bg-danger' : device.battery_level < 50 ? 'bg-warning' : 'bg-success'}" 
                                         style="width: ${device.battery_level}%"></div>
                                </div>
                            </div>
                        ` : ''}
                        
                        <div class="mb-3">
                            <small class="text-muted"><i class="bi bi-clock"></i> Last Seen: ${lastSeen}</small>
                        </div>
                        
                        ${device.latitude && device.longitude ? `
                            <div class="mb-3">
                                <a href="${Utils.getMapUrl(device.latitude, device.longitude)}" target="_blank" class="text-decoration-none">
                                    <i class="bi bi-geo-alt"></i> ${Utils.formatLocation(device.latitude, device.longitude)}
                                </a>
                            </div>
                        ` : ''}
                        
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary btn-sm" onclick="viewDeviceDetails(${device.id})">
                                <i class="bi bi-info-circle"></i> View Details
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="deleteDevice(${device.id})">
                                <i class="bi bi-trash"></i> Remove Device
                            </button>
                        </div>
                    </div>
                    <div class="card-footer bg-white text-muted small">
                        Registered: ${Utils.formatDate(device.created_at)}
                    </div>
                </div>
            `;
            devicesList.appendChild(col);
        });
        
    } catch (error) {
        console.error('Error loading devices:', error);
        Utils.showError('Failed to load devices');
    }
}

/**
 * View device details
 */
async function viewDeviceDetails(deviceId) {
    const device = devices.find(d => d.id === deviceId);
    if (!device) return;
    
    const modal = new bootstrap.Modal(document.getElementById('deviceDetailsModal'));
    const content = document.getElementById('deviceDetailsContent');
    
    content.innerHTML = `
        <div class="row">
            <div class="col-md-6 mb-3">
                <h6>Device Information</h6>
                <table class="table table-sm">
                    <tr>
                        <th>Device ID:</th>
                        <td>${device.id}</td>
                    </tr>
                    <tr>
                        <th>Name:</th>
                        <td>${device.device_name || 'N/A'}</td>
                    </tr>
                    <tr>
                        <th>Status:</th>
                        <td><span class="badge bg-${CONFIG.STATUS_COLORS[device.status]}">${device.status}</span></td>
                    </tr>
                    <tr>
                        <th>Battery:</th>
                        <td>${device.battery_level !== null ? device.battery_level + '%' : 'N/A'}</td>
                    </tr>
                    <tr>
                        <th>Last Heartbeat:</th>
                        <td>${device.last_heartbeat ? Utils.formatDate(device.last_heartbeat) : 'Never'}</td>
                    </tr>
                    <tr>
                        <th>Registered:</th>
                        <td>${Utils.formatDate(device.created_at)}</td>
                    </tr>
                </table>
            </div>
            <div class="col-md-6 mb-3">
                <h6>Location</h6>
                ${device.latitude && device.longitude ? `
                    <p><strong>Coordinates:</strong><br>${Utils.formatLocation(device.latitude, device.longitude)}</p>
                    <a href="${Utils.getMapUrl(device.latitude, device.longitude)}" target="_blank" class="btn btn-outline-primary btn-sm">
                        <i class="bi bi-map"></i> View on Google Maps
                    </a>
                ` : '<p class="text-muted">Location data not available</p>'}
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <h6>Device Token</h6>
                <div class="alert alert-info">
                    <code>${device.device_token}</code>
                </div>
                <p class="small text-muted">Use this token in your ESP32 device configuration</p>
            </div>
        </div>
    `;
    
    modal.show();
}

/**
 * Delete device
 */
async function deleteDevice(deviceId) {
    if (!confirm('Are you sure you want to remove this device? This action cannot be undone.')) {
        return;
    }
    
    try {
        await API.delete(`${CONFIG.ENDPOINTS.DEVICES}/${deviceId}`);
        Utils.showSuccess('Device removed successfully');
        loadDevices();
    } catch (error) {
        Utils.showError('Failed to remove device: ' + error.message);
    }
}

/**
 * Handle add device form
 */
const addDeviceForm = document.getElementById('addDeviceForm');
const deviceAlert = document.getElementById('deviceAlert');
const addDeviceBtnText = document.getElementById('addDeviceBtnText');
const addDeviceSpinner = document.getElementById('addDeviceSpinner');

addDeviceForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const deviceName = document.getElementById('deviceName').value;
    const deviceToken = document.getElementById('deviceToken').value;
    
    deviceAlert.classList.add('d-none');
    addDeviceBtnText.textContent = 'Registering...';
    addDeviceSpinner.classList.remove('d-none');
    addDeviceForm.querySelector('button[type="submit"]').disabled = true;
    
    try {
        await API.post(CONFIG.ENDPOINTS.DEVICES, {
            device_name: deviceName,
            device_token: deviceToken
        });
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addDeviceModal'));
        modal.hide();
        
        // Reset form
        addDeviceForm.reset();
        
        Utils.showSuccess('Device registered successfully!');
        loadDevices();
        
    } catch (error) {
        deviceAlert.textContent = error.message;
        deviceAlert.classList.remove('alert-success');
        deviceAlert.classList.add('alert-danger');
        deviceAlert.classList.remove('d-none');
    } finally {
        addDeviceBtnText.textContent = 'Register Device';
        addDeviceSpinner.classList.add('d-none');
        addDeviceForm.querySelector('button[type="submit"]').disabled = false;
    }
});

// Reset alert when modal is hidden
document.getElementById('addDeviceModal').addEventListener('hidden.bs.modal', () => {
    deviceAlert.classList.add('d-none');
    addDeviceForm.reset();
});

// Load devices on page load
document.addEventListener('DOMContentLoaded', loadDevices);