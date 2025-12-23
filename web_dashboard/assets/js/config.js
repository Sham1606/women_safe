/**
 * Configuration file for Women Safety System Web Dashboard
 */

const CONFIG = {
    // Backend API Base URL
    API_BASE_URL: 'http://localhost:5000/api/v1',
    
    // API Endpoints
    ENDPOINTS: {
        // Auth
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        LOGOUT: '/auth/logout',
        REFRESH: '/auth/refresh',
        ME: '/auth/me',
        CHANGE_PASSWORD: '/auth/change-password',
        
        // Users
        PROFILE: '/users/profile',
        GUARDIANS: '/users/guardians',
        EMERGENCY_CONTACTS: '/users/emergency-contacts',
        
        // Devices
        DEVICES: '/devices',
        DEVICE_STATUS: (id) => `/devices/${id}/status`,
        
        // Alerts
        ALERTS: '/alerts',
        ACTIVE_ALERTS: '/alerts/active',
        ALERT_DETAIL: (id) => `/alerts/${id}`,
        ACKNOWLEDGE_ALERT: (id) => `/alerts/${id}/acknowledge`,
        RESOLVE_ALERT: (id) => `/alerts/${id}/resolve`,
        FALSE_ALARM: (id) => `/alerts/${id}/false-alarm`,
        
        // Evidence
        EVIDENCE_BY_ALERT: (alertId) => `/evidence/alert/${alertId}`,
        EVIDENCE_DOWNLOAD: (id) => `/evidence/${id}/download`,
        
        // Stress Detection
        MODEL_STATUS: '/stress-detection/model-status'
    },
    
    // Local Storage Keys
    STORAGE_KEYS: {
        ACCESS_TOKEN: 'access_token',
        REFRESH_TOKEN: 'refresh_token',
        USER_DATA: 'user_data'
    },
    
    // Alert Auto-Refresh Interval (milliseconds)
    ALERT_REFRESH_INTERVAL: 30000, // 30 seconds
    
    // Status Badge Colors
    STATUS_COLORS: {
        online: 'success',
        offline: 'secondary',
        alert: 'danger',
        maintenance: 'warning'
    },
    
    // Alert Type Labels
    ALERT_TYPES: {
        manual_trigger: 'Manual',
        ai_detected: 'AI Detected'
    },
    
    // Alert Status Labels
    ALERT_STATUS: {
        active: { label: 'Active', class: 'danger' },
        acknowledged: { label: 'Acknowledged', class: 'warning' },
        resolved: { label: 'Resolved', class: 'success' },
        false_alarm: { label: 'False Alarm', class: 'secondary' }
    }
};

// Utility Functions
const Utils = {
    /**
     * Format date to readable string
     */
    formatDate: (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (seconds < 60) return 'Just now';
        if (minutes < 60) return `${minutes} min ago`;
        if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`;
        
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    /**
     * Format location coordinates
     */
    formatLocation: (latitude, longitude) => {
        if (!latitude || !longitude) return 'Location unavailable';
        return `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;
    },
    
    /**
     * Get Google Maps URL
     */
    getMapUrl: (latitude, longitude) => {
        return `https://www.google.com/maps?q=${latitude},${longitude}`;
    },
    
    /**
     * Show success toast message
     */
    showSuccess: (message) => {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 end-0 m-3';
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    },
    
    /**
     * Show error toast message
     */
    showError: (message) => {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 end-0 m-3';
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    },
    
    /**
     * Show loading spinner
     */
    showLoading: (elementId) => {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="spinner-wrapper">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            `;
        }
    },
    
    /**
     * Show empty state
     */
    showEmptyState: (elementId, icon, message) => {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-${icon}"></i>
                    <p>${message}</p>
                </div>
            `;
        }
    }
};