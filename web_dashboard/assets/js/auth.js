/**
 * Authentication management
 */

const Auth = {
    /**
     * Save tokens to localStorage
     */
    saveTokens: (accessToken, refreshToken = null) => {
        localStorage.setItem(CONFIG.STORAGE_KEYS.ACCESS_TOKEN, accessToken);
        if (refreshToken) {
            localStorage.setItem(CONFIG.STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
        }
    },
    
    /**
     * Get access token
     */
    getAccessToken: () => {
        return localStorage.getItem(CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
    },
    
    /**
     * Get refresh token
     */
    getRefreshToken: () => {
        return localStorage.getItem(CONFIG.STORAGE_KEYS.REFRESH_TOKEN);
    },
    
    /**
     * Save user data
     */
    saveUserData: (userData) => {
        localStorage.setItem(CONFIG.STORAGE_KEYS.USER_DATA, JSON.stringify(userData));
    },
    
    /**
     * Get user data
     */
    getUserData: () => {
        const data = localStorage.getItem(CONFIG.STORAGE_KEYS.USER_DATA);
        return data ? JSON.parse(data) : null;
    },
    
    /**
     * Check if user is authenticated
     */
    isAuthenticated: () => {
        return !!Auth.getAccessToken();
    },
    
    /**
     * Logout user
     */
    logout: () => {
        localStorage.removeItem(CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.USER_DATA);
        window.location.href = 'index.html';
    },
    
    /**
     * Protect page (redirect to login if not authenticated)
     */
    requireAuth: () => {
        if (!Auth.isAuthenticated()) {
            window.location.href = 'index.html';
            return false;
        }
        return true;
    },
    
    /**
     * Redirect to dashboard if already authenticated
     */
    redirectIfAuthenticated: () => {
        if (Auth.isAuthenticated()) {
            window.location.href = 'dashboard.html';
        }
    }
};

// Setup global logout button handler
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (confirm('Are you sure you want to logout?')) {
                Auth.logout();
            }
        });
    }
});