"""View routes for rendering HTML pages."""
from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

views_bp = Blueprint('views', __name__)


@views_bp.route('/')
def index():
    """Landing page with login/register."""
    return render_template('index.html')


@views_bp.route('/dashboard')
@jwt_required(optional=True)
def dashboard():
    """Main dashboard - redirects to appropriate role-based view."""
    identity = get_jwt_identity()
    if not identity:
        return redirect(url_for('views.index'))
    
    claims = get_jwt()
    role = claims.get('role', 'GUARDIAN')
    
    return render_template('dashboard.html', user_role=role)


@views_bp.route('/alerts')
@jwt_required()
def alerts_page():
    """Alert management page."""
    return render_template('alerts.html')


@views_bp.route('/profile')
@jwt_required()
def profile():
    """User profile page."""
    return render_template('profile.html')


@views_bp.route('/admin')
@jwt_required()
def admin_panel():
    """Admin panel - requires ADMIN or POLICE role."""
    claims = get_jwt()
    role = claims.get('role', 'GUARDIAN')
    
    if role not in ['ADMIN', 'POLICE']:
        return redirect(url_for('views.dashboard'))
    
    return render_template('admin_panel.html')


@views_bp.route('/analytics')
@jwt_required()
def analytics():
    """Analytics dashboard."""
    claims = get_jwt()
    role = claims.get('role', 'GUARDIAN')
    
    if role not in ['ADMIN', 'POLICE']:
        return redirect(url_for('views.dashboard'))
    
    return render_template('analytics.html')


@views_bp.route('/simulator')
def device_simulator():
    """Device simulator for testing (public access)."""
    return render_template('device_simulator.html')


@views_bp.route('/notifications')
@jwt_required()
def notifications():
    """Real-time notifications page."""
    return render_template('notifications.html')


@views_bp.route('/monitor')
@jwt_required()
def live_monitor():
    """Live monitoring page with real-time updates."""
    return render_template('live_monitor.html')


@views_bp.route('/evidence')
@jwt_required()
def evidence_gallery():
    """Evidence gallery page."""
    claims = get_jwt()
    role = claims.get('role', 'GUARDIAN')
    
    if role not in ['ADMIN', 'POLICE']:
        return redirect(url_for('views.dashboard'))
    
    return render_template('evidence_gallery.html')


@views_bp.route('/devices')
@jwt_required()
def device_management():
    """Device management page."""
    return render_template('device_management.html')


@views_bp.route('/settings')
@jwt_required()
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
