"""View routes for rendering HTML pages."""
from flask import Blueprint, render_template, redirect, url_for, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request

views_bp = Blueprint('views', __name__)


@views_bp.route('/')
def index():
    """Landing page with login/register."""
    return render_template('index.html')


@views_bp.route('/dashboard')
def dashboard():
    """Main dashboard - NO JWT required, handles auth on client side."""
    return render_template('dashboard.html')


@views_bp.route('/alerts')
def alerts_page():
    """Alert management page."""
    return render_template('alerts.html')


@views_bp.route('/profile')
def profile():
    """User profile page."""
    return render_template('profile.html')


@views_bp.route('/admin')
def admin_panel():
    """Admin panel - requires ADMIN or POLICE role."""
    return render_template('admin_panel.html')


@views_bp.route('/analytics')
def analytics():
    """Analytics dashboard."""
    return render_template('analytics.html')


@views_bp.route('/simulator')
def device_simulator():
    """Device simulator for testing (public access)."""
    return render_template('device_simulator.html')


@views_bp.route('/notifications')
def notifications():
    """Real-time notifications page."""
    return render_template('notifications.html')


@views_bp.route('/monitor')
def live_monitor():
    """Live monitoring page with real-time updates."""
    return render_template('live_monitor.html')


@views_bp.route('/evidence')
def evidence_gallery():
    """Evidence gallery page."""
    return render_template('evidence_gallery.html')


@views_bp.route('/devices')
def device_management():
    """Device management page."""
    return render_template('device_management.html')


@views_bp.route('/settings')
def settings():
    """Application settings page."""
    return render_template('settings.html')


@views_bp.route('/help')
def help_page():
    """Help and documentation page."""
    return render_template('help.html')


@views_bp.route('/test')
def test_suite():
    """Test suite interface for developers."""
    return render_template('test_suite.html')
