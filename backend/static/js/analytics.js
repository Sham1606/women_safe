// Analytics JavaScript

const API_BASE = window.location.origin;
const token = localStorage.getItem('token');

let charts = {};

document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    loadAnalytics();
});

function initializeCharts() {
    // Alerts Timeline Chart
    const ctx1 = document.getElementById('alertsTimelineChart').getContext('2d');
    charts.timeline = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Alerts',
                data: [],
                borderColor: 'rgb(220, 53, 69)',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {display: false}
            }
        }
    });

    // Alert Status Chart
    const ctx2 = document.getElementById('alertStatusChart').getContext('2d');
    charts.status = new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: ['New', 'In Progress', 'Resolved'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#dc3545', '#ffc107', '#28a745']
            }]
        }
    });

    // Alert Reasons Chart
    const ctx3 = document.getElementById('alertReasonsChart').getContext('2d');
    charts.reasons = new Chart(ctx3, {
        type: 'bar',
        data: {
            labels: ['Manual SOS', 'Auto Stress', 'Vitals'],
            datasets: [{
                label: 'Count',
                data: [0, 0, 0],
                backgroundColor: '#0d6efd'
            }]
        }
    });
}

async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/api/admin/stats`, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        
        const stats = await response.json();
        
        // Update summary cards
        document.getElementById('totalEventsToday').textContent = stats.total_users || 0;
        document.getElementById('activeDevicesNow').textContent = stats.active_devices || 0;
        
        // Update charts with real data
        if (stats.alerts_by_status) {
            charts.status.data.datasets[0].data = [
                stats.alerts_by_status.NEW || 0,
                stats.alerts_by_status.IN_PROGRESS || 0,
                stats.alerts_by_status.RESOLVED || 0
            ];
            charts.status.update();
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}
