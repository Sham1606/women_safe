/**
 * Navigation & Role Management Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
});

function initNavigation() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userRole = user.role || 'GUARDIAN';

    // 0. Handle Unauthenticated State
    if (!token) {
        // Hide Main Navbar Links
        const navLinks = document.getElementById('navLinks');
        if (navLinks) navLinks.style.display = 'none';

        // Hide User Dropdown
        const userDropdown = document.querySelector('.dropdown');
        if (userDropdown) userDropdown.style.display = 'none';

        // Redirect protected pages
        const publicPages = ['/', '/help', '/simulator'];
        const currentPath = window.location.pathname;
        if (!publicPages.includes(currentPath)) {
            window.location.href = '/';
        }
        return; // Stop execution if not logged in
    }

    // 1. Update User Profile in Navbar
    if (user.name) {
        const nameDisplay = document.getElementById('userNameDisplay');
        const initialsDisplay = document.getElementById('userInitials');
        const roleDisplay = document.getElementById('userRoleDisplay');

        if (nameDisplay) nameDisplay.textContent = user.name;
        if (initialsDisplay) initialsDisplay.textContent = user.name.charAt(0).toUpperCase();
        if (roleDisplay) roleDisplay.textContent = userRole;
    }

    // 2. Handle Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }

    // 3. Role-Based Link Visibility
    const roleBasedLinks = document.querySelectorAll('.nav-link[data-role]');
    roleBasedLinks.forEach(link => {
        const allowedRoles = link.dataset.role.split(',');
        if (!allowedRoles.includes(userRole)) {
            // Hide the parent list item (li) if checking nav links
            if (link.parentElement.tagName === 'LI') {
                link.parentElement.style.display = 'none';
            } else {
                link.style.display = 'none';
            }
        }
    });

    // 4. Highlight Active Page
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.nav-link');
    links.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('user_role');
    window.location.href = '/';
}
