const API_URL = '/api';
let currentUser = null;
let currentToken = null;
let map = null;
let markers = {};
let currentActiveAlertId = null;

// Init
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');

    if (!token || !userStr) {
        window.location.href = '/';
        return;
    }

    currentUser = JSON.parse(userStr);
    currentToken = token;

    // Setup Nav
    document.getElementById('userNameDisplay').textContent = currentUser.name;
    document.getElementById('userRoleBadge').textContent = currentUser.role;
    document.getElementById('logoutBtn').addEventListener('click', logout);

    initMap();

    if (currentUser.role === 'GUARDIAN') {
        document.getElementById('guardianView').classList.remove('d-none');
        refreshGuardianData();
        setInterval(refreshGuardianData, 3000);
    } else {
        document.getElementById('adminView').classList.remove('d-none');
        refreshAdminData();
        setInterval(refreshAdminData, 5000);
    }

    document.getElementById('addDeviceForm')?.addEventListener('submit', registerDevice);
});

function initMap() {
    if (map) map.remove();
    map = L.map('mapContainer').setView([20.5937, 78.9629], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
}

function logout() {
    localStorage.clear();
    window.location.href = '/';
}

// GUARDIAN LOGIC
async function refreshGuardianData() {
    try {
        const res = await fetch(`${API_URL}/device/my-devices`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const devices = await res.json();
        renderDevices(devices);
        updateMapMarkers(devices, false);
    } catch (e) { console.error("Guardian pull error:", e); }
}

function renderDevices(devices) {
    const container = document.getElementById('deviceList');
    if (devices.length === 0) {
        container.innerHTML = '<div class="col-12 py-4 text-center text-muted">No devices linked to your account.</div>';
        return;
    }

    container.innerHTML = devices.map(d => {
        const isStressed = d.active_alert.status === 'NEW' || d.active_alert.status === 'IN_PROGRESS';
        const statusClass = isStressed ? 'status-stressed' : 'status-active';
        return `
        <div class="col-12">
            <div class="glass-card p-3 ${statusClass}">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="m-0">${d.uid}</h6>
                    <span class="badge ${d.is_active ? 'bg-success' : 'bg-secondary'} rounded-pill" style="font-size: 0.6rem;">
                        ${d.is_active ? 'ONLINE' : 'OFFLINE'}
                    </span>
                </div>
                <div class="d-flex mb-2">
                    <span class="vitals-badge">❤️ ${d.latest_vitals.hr || '--'}</span>
                    <span class="vitals-badge">🌡️ ${d.latest_vitals.temp || '--'}°C</span>
                    <span class="vitals-badge">🔋 ${d.battery || '--'}%</span>
                </div>
                <div class="x-small text-muted" style="font-size: 0.7rem;">
                    AI SENSE: <span class="${d.latest_vitals.ai_label === 'stressed' ? 'text-danger fw-bold' : 'text-success'}">
                        ${d.latest_vitals.ai_label.toUpperCase()} (${(d.latest_vitals.ai_conf * 100).toFixed(0)}%)
                    </span>
                </div>
                ${isStressed ? `
                    <div class="mt-2 p-2 bg-danger bg-opacity-10 rounded border border-danger border-opacity-25 d-flex justify-content-between align-items-center">
                        <small class="text-danger fw-bold">⚠️ EMERGENCY</small>
                        <button class="btn btn-xs btn-premium px-2 py-0 rounded-pill" style="font-size: 0.7rem;" onclick="viewAlert(${d.active_alert.id})">VIEW</button>
                    </div>
                ` : ''}
            </div>
        </div>
        `;
    }).join('');
}

async function registerDevice(e) {
    e.preventDefault();
    const uid = e.target.device_uid.value;
    try {
        const res = await fetch(`${API_URL}/device/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ device_uid: uid })
        });
        if (res.ok) {
            bootstrap.Modal.getInstance(document.getElementById('addDeviceModal')).hide();
            refreshGuardianData();
        } else { alert('Failed to register device.'); }
    } catch (err) { console.error(err); }
}

// ADMIN LOGIC
async function refreshAdminData() {
    try {
        const resStats = await fetch(`${API_URL}/admin/stats`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const stats = await resStats.json();
        renderStats(stats);

        const resAlerts = await fetch(`${API_URL}/alerts`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const alerts = await resAlerts.json();
        renderAlertTable(alerts);
        updateMapMarkers(alerts, true);
    } catch (e) { console.error("Admin pull error:", e); }
}

function renderStats(stats) {
    document.getElementById('statDevices').textContent = stats.active_devices;
    document.getElementById('statAlerts').textContent = stats.alerts_by_status.NEW || 0;
    document.getElementById('statUsers').textContent = stats.total_users;
}

function renderAlertTable(alerts) {
    const tbody = document.getElementById('alertTableBody');
    tbody.innerHTML = alerts.map(a => `
        <tr onclick="viewAlert(${a.id})" style="cursor: pointer;">
            <td>${new Date(a.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
            <td>${a.device_uid}</td>
            <td><span class="badge bg-${a.status === 'NEW' ? 'danger' : 'success'}">${a.status}</span></td>
        </tr>
    `).join('');
}

// SHARED UTILS
// Custom Marker Icons
function createCustomIcon(isAlert, uid) {
    const color = isAlert ? '#ff3d57' : '#2b5876';
    const icon = isAlert ? '⚠️' : '👤';
    return L.divIcon({
        html: `
            <div class="icon-container">
                ${isAlert ? '<div class="distress-pulse"></div>' : ''}
                <div class="marker-pin" style="background: ${color}">
                    <span>${icon}</span>
                </div>
            </div>
        `,
        className: 'custom-div-icon',
        iconSize: [40, 40],
        iconAnchor: [20, 40]
    });
}

function updateMapMarkers(data, isAdmin = false) {
    let bounds = [];
    data.forEach(item => {
        const id = isAdmin ? `alert_${item.id}` : `dev_${item.uid}`;
        const lat = isAdmin ? item.lat : item.location.lat;
        const lng = isAdmin ? item.lng : item.location.lng;

        if (!lat || !lng) return;
        bounds.push([lat, lng]);

        if (markers[id]) {
            markers[id].setLatLng([lat, lng]);
            // If it's an alert, update icon to pulsing if status changed
            if (isAdmin) markers[id].setIcon(createCustomIcon(item.status === 'NEW', item.device_uid));
        } else {
            const isStressed = isAdmin ? (item.status === 'NEW') : (item.active_alert && item.active_alert.status === 'NEW');
            markers[id] = L.marker([lat, lng], {
                icon: createCustomIcon(isStressed, isAdmin ? item.device_uid : item.uid)
            }).addTo(map)
                .bindPopup(isAdmin ? `<b>ALERT: ${item.device_uid}</b><br>${item.reason}` : `<b>USER: ${item.uid}</b>`);
        }
    });

    if (bounds.length > 0 && !isAdmin) {
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
    }
}

async function viewAlert(id) {
    currentActiveAlertId = id;
    try {
        const res = await fetch(`${API_URL}/alerts/${id}`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const data = await res.json();

        document.getElementById('modalReason').textContent = data.reason;
        document.getElementById('modalTime').textContent = new Date(data.timestamp).toLocaleString();
        document.getElementById('modalStatus').textContent = data.status;

        const evContainer = document.getElementById('modalEvidence');
        if (data.evidence && data.evidence.length > 0) {
            evContainer.innerHTML = data.evidence.map(e => `
                <div class="mb-2">
                    <p class="x-small text-muted mb-1">Evidence Reference Content</p>
                    <audio controls class="w-100" style="height: 30px;">
                        <source src="${API_URL.replace('/api', '')}/static/evidence/${e.path}" type="audio/wav">
                    </audio>
                </div>
            `).join('');
        } else {
            evContainer.innerHTML = '<div class="text-muted small">No evidence captured.</div>';
        }

        const modal = new bootstrap.Modal(document.getElementById('alertDetailModal'));
        modal.show();
    } catch (e) { console.error(e); }
}

async function updateAlertStatusLocally(newStatus) {
    if (!currentActiveAlertId) return;
    try {
        const res = await fetch(`${API_URL}/alerts/${currentActiveAlertId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ status: newStatus })
        });
        if (res.ok) {
            bootstrap.Modal.getInstance(document.getElementById('alertDetailModal')).hide();
            if (currentUser.role === 'GUARDIAN') refreshGuardianData(); else refreshAdminData();
        }
    } catch (e) { console.error(e); }
}
