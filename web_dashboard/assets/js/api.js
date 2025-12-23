/**
 * API Service for making HTTP requests
 */

const API = {
    /**
     * Make authenticated API request
     */
    request: async (endpoint, options = {}) => {
        const url = CONFIG.API_BASE_URL + endpoint;
        
        // Default headers
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Add authorization token if available
        const token = Auth.getAccessToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            const data = await response.json();
            
            // Handle unauthorized (token expired)
            if (response.status === 401) {
                Auth.logout();
                throw new Error('Session expired. Please login again.');
            }
            
            // Handle other errors
            if (!response.ok) {
                throw new Error(data.message || data.error || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    },
    
    /**
     * GET request
     */
    get: async (endpoint) => {
        return await API.request(endpoint, {
            method: 'GET'
        });
    },
    
    /**
     * POST request
     */
    post: async (endpoint, data) => {
        return await API.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    /**
     * PUT request
     */
    put: async (endpoint, data) => {
        return await API.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    /**
     * DELETE request
     */
    delete: async (endpoint) => {
        return await API.request(endpoint, {
            method: 'DELETE'
        });
    }
};