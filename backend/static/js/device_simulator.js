// Device Simulator JavaScript

let autoSendInterval = null;
const API_BASE = window.location.origin;

// Update slider displays
document.getElementById('heartRate').addEventListener('input', function() {
    document.getElementById('hrDisplay').textContent = this.value;
    document.getElementById('liveHr').textContent = this.value;
});

document.getElementById('temperature').addEventListener('input', function() {
    document.getElementById('tempDisplay').textContent = this.value;
    document.getElementById('liveTemp').textContent = this.value;
});

document.getElementById('spo2').addEventListener('input', function() {
    document.getElementById('spo2Display').textContent = this.value;
    document.getElementById('liveSpo2').textContent = this.value;
});

document.getElementById('battery').addEventListener('input', function() {
    document.getElementById('batteryDisplay').textContent = this.value;
    document.getElementById('liveBattery').textContent = this.value;
});

// Send event
document.getElementById('deviceSimForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    await sendEvent();
});

async function sendEvent() {
    const formData = new FormData();
    
    formData.append('device_uid', document.getElementById('deviceUid').value);
    formData.append('heart_rate', document.getElementById('heartRate').value);
    formData.append('temperature', document.getElementById('temperature').value);
    formData.append('spo2', document.getElementById('spo2').value);
    formData.append('lat', document.getElementById('latitude').value);
    formData.append('lng', document.getElementById('longitude').value);
    formData.append('manual_sos', document.getElementById('manualSos').checked ? 1 : 0);
    
    const audioFile = document.getElementById('audioFile').files[0];
    if (audioFile) {
        formData.append('audio', audioFile);
    }

    try {
        const response = await fetch(`${API_BASE}/api/device/event`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        logResponse(data, response.ok);
    } catch (error) {
        logResponse({error: error.message}, false);
    }
}

function logResponse(data, success) {
    const log = document.getElementById('responseLog');
    const timestamp = new Date().toLocaleTimeString();
    
    const logEntry = document.createElement('div');
    logEntry.className = `alert alert-${success ? 'success' : 'danger'} alert-dismissible fade show mb-2`;
    logEntry.innerHTML = `
        <strong>[${timestamp}]</strong><br>
        Status: ${data.status || 'error'}<br>
        ${data.distress_score !== undefined ? `Distress Score: ${data.distress_score}<br>` : ''}
        ${data.alert_triggered !== undefined ? `Alert Triggered: ${data.alert_triggered ? 'YES' : 'NO'}<br>` : ''}
        ${data.error ? `Error: ${data.error}` : ''}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    log.insertBefore(logEntry, log.firstChild);
    
    // Keep only last 10 entries
    while (log.children.length > 10) {
        log.removeChild(log.lastChild);
    }
}

// Auto-send toggle
document.getElementById('autoSendBtn').addEventListener('click', function() {
    if (autoSendInterval) {
        clearInterval(autoSendInterval);
        autoSendInterval = null;
        this.innerHTML = '<i class="bi bi-arrow-repeat"></i> Start Auto-Send (Every 30s)';
        this.classList.remove('btn-danger');
        this.classList.add('btn-outline-primary');
    } else {
        autoSendInterval = setInterval(sendEvent, 30000);
        this.innerHTML = '<i class="bi bi-stop-circle"></i> Stop Auto-Send';
        this.classList.remove('btn-outline-primary');
        this.classList.add('btn-danger');
        sendEvent(); // Send immediately
    }
});

// Preset scenarios
function loadScenario(type) {
    switch(type) {
        case 'normal':
            document.getElementById('heartRate').value = 75;
            document.getElementById('temperature').value = 36.5;
            document.getElementById('spo2').value = 98;
            document.getElementById('manualSos').checked = false;
            break;
        case 'elevated':
            document.getElementById('heartRate').value = 105;
            document.getElementById('temperature').value = 37.8;
            document.getElementById('spo2').value = 95;
            document.getElementById('manualSos').checked = false;
            break;
        case 'stress':
            document.getElementById('heartRate').value = 130;
            document.getElementById('temperature').value = 39.2;
            document.getElementById('spo2').value = 92;
            document.getElementById('manualSos').checked = false;
            break;
        case 'emergency':
            document.getElementById('heartRate').value = 140;
            document.getElementById('temperature').value = 40.0;
            document.getElementById('spo2').value = 88;
            document.getElementById('manualSos').checked = true;
            break;
    }
    
    // Trigger input events to update displays
    document.getElementById('heartRate').dispatchEvent(new Event('input'));
    document.getElementById('temperature').dispatchEvent(new Event('input'));
    document.getElementById('spo2').dispatchEvent(new Event('input'));
}
