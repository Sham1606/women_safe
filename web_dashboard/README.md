# Women Safety System - Web Dashboard

A modern, responsive web dashboard built with **HTML, CSS, JavaScript, and Bootstrap 5** for managing the Women Safety System.

## Features

### 🔐 Authentication
- User login and registration
- JWT token-based authentication
- Remember me functionality
- Password change
- Automatic session management

### 📊 Dashboard
- Real-time statistics (active devices, alerts, guardians)
- Recent alerts list with quick actions
- Device status overview
- Auto-refresh every 30 seconds

### 📱 Device Management
- Register new ESP32 devices
- View device status (online/offline)
- Battery level monitoring
- GPS location tracking
- Last heartbeat timestamp
- Remove devices

### 🚨 Alert Management
- View all alerts with filtering
- Filter by status, type, and device
- Detailed alert view with:
  - Physiological data (heart rate, temperature)
  - Stress score and confidence
  - GPS location with Google Maps integration
  - Evidence files (photos, audio)
- Alert actions:
  - Acknowledge
  - Resolve
  - Mark as false alarm
- Auto-refresh active alerts

### 👥 Guardian Management
- Add emergency contacts
- View guardian details
- Remove guardians
- Contact information (email, phone)

### 👤 Profile Management
- Update profile information
- Change password
- View account details

## Technology Stack

- **HTML5** - Structure
- **CSS3** - Styling with custom themes
- **JavaScript (ES6)** - Logic and API integration
- **Bootstrap 5.3** - UI framework
- **Bootstrap Icons** - Icon library
- **Fetch API** - HTTP requests

## Project Structure

```
web_dashboard/
├── index.html              # Login page
├── register.html          # Registration page
├── dashboard.html         # Main dashboard
├── devices.html           # Device management
├── alerts.html            # Alert management
├── guardians.html         # Guardian management
├── profile.html           # User profile
├── assets/
    ├── css/
    │   └── style.css          # Custom styles
    └── js/
        ├── config.js          # Configuration & utilities
        ├── auth.js            # Authentication management
        ├── api.js             # API service
        ├── login.js           # Login page logic
        ├── register.js        # Registration page logic
        ├── dashboard.js       # Dashboard page logic
        ├── devices.js         # Devices page logic
        ├── alerts.js          # Alerts page logic
        ├── guardians.js       # Guardians page logic
        └── profile.js         # Profile page logic
```

## Setup Instructions

### 1. Configure Backend API

Edit `assets/js/config.js` and update the API base URL:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:5000/api/v1',  // Change to your backend URL
    // ...
};
```

### 2. Serve the Dashboard

#### Option 1: Python HTTP Server
```bash
cd web_dashboard
python -m http.server 8000
```
Access at: `http://localhost:8000`

#### Option 2: Node.js HTTP Server
```bash
cd web_dashboard
npx http-server -p 8000
```

#### Option 3: VS Code Live Server
1. Install "Live Server" extension
2. Right-click `index.html`
3. Select "Open with Live Server"

### 3. Start Backend API

Ensure the Flask backend is running:
```bash
cd backend
python app.py
```

### 4. Access Dashboard

Open your browser and go to:
- `http://localhost:8000` (or your configured port)
- Login with your credentials or register a new account

## Configuration

### API Endpoints

All API endpoints are configured in `assets/js/config.js`:

```javascript
ENDPOINTS: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    PROFILE: '/users/profile',
    DEVICES: '/devices',
    ALERTS: '/alerts',
    GUARDIANS: '/users/guardians',
    // ...
}
```

### Auto-Refresh Interval

Dashboard and alerts auto-refresh every 30 seconds (configurable):

```javascript
ALERT_REFRESH_INTERVAL: 30000  // milliseconds
```

## Usage Guide

### First Time Setup

1. **Register Account**
   - Go to registration page
   - Fill in details (name, email, phone, role, password)
   - Select role: User, Guardian, or Police
   - Click "Create Account"

2. **Login**
   - Enter email and password
   - Optionally check "Remember me"
   - Click "Sign In"

3. **Register Device**
   - Go to Devices page
   - Click "Register New Device"
   - Enter device name and token (from ESP32)
   - Click "Register Device"

4. **Add Guardians**
   - Go to Guardians page
   - Click "Add Guardian"
   - Enter guardian details
   - Click "Add Guardian"

### Managing Alerts

1. **View Alerts**
   - Go to Alerts page
   - See all alerts with status, type, location
   - Use filters to narrow down results

2. **Alert Actions**
   - Click eye icon to view details
   - For active alerts:
     - Acknowledge: Mark as seen
     - Resolve: Mark as handled
     - False Alarm: Mark as false positive

3. **View Evidence**
   - Open alert details
   - Scroll to Evidence section
   - Click Download to get photos/audio

### Device Monitoring

1. **Check Status**
   - Green badge: Online
   - Gray badge: Offline
   - Red badge: Alert triggered

2. **Battery Level**
   - Progress bar shows current level
   - Red: < 20%
   - Yellow: 20-50%
   - Green: > 50%

3. **Location Tracking**
   - Click GPS coordinates to view on Google Maps
   - Updated on each heartbeat

## Customization

### Styling

Edit `assets/css/style.css` to customize:

```css
:root {
    --primary-color: #0d6efd;     /* Brand color */
    --success-color: #198754;     /* Success states */
    --danger-color: #dc3545;      /* Alerts/errors */
    --warning-color: #ffc107;     /* Warnings */
}
```

### Adding New Pages

1. Create HTML file (e.g., `settings.html`)
2. Add navigation link in navbar
3. Create JavaScript file (e.g., `assets/js/settings.js`)
4. Include config, auth, and api files

## Browser Support

- Chrome/Edge: 90+
- Firefox: 88+
- Safari: 14+
- Opera: 76+

## Security Features

- JWT token authentication
- Automatic token refresh
- Session timeout handling
- Protected routes (redirect to login)
- HTTPS recommended for production

## Troubleshooting

### Login Issues
- Check if backend API is running
- Verify API_BASE_URL in config.js
- Check browser console for errors
- Ensure CORS is enabled on backend

### Data Not Loading
- Check network tab in browser DevTools
- Verify JWT token is stored (localStorage)
- Check API endpoint URLs
- Ensure backend returns correct JSON

### Alert Not Refreshing
- Auto-refresh works when page is visible
- Manually click Refresh button
- Check ALERT_REFRESH_INTERVAL setting

## API Integration

The dashboard communicates with the Flask backend using REST API:

### Authentication
```javascript
// Login
POST /api/v1/auth/login
Body: { email, password }
Response: { access_token, refresh_token }

// Register
POST /api/v1/auth/register
Body: { name, email, password, role }
```

### Devices
```javascript
// List devices
GET /api/v1/devices
Headers: { Authorization: Bearer <token> }

// Register device
POST /api/v1/devices
Body: { device_name, device_token }
```

### Alerts
```javascript
// List alerts
GET /api/v1/alerts?status=active&alert_type=manual

// Get alert details
GET /api/v1/alerts/{id}

// Acknowledge alert
POST /api/v1/alerts/{id}/acknowledge
```

## Production Deployment

### 1. Build for Production

- Minify CSS and JavaScript files
- Update API_BASE_URL to production backend
- Enable HTTPS

### 2. Deploy to Web Server

**Apache:**
```apache
<VirtualHost *:80>
    ServerName womensafety.example.com
    DocumentRoot /var/www/web_dashboard
    
    <Directory /var/www/web_dashboard>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

**Nginx:**
```nginx
server {
    listen 80;
    server_name womensafety.example.com;
    root /var/www/web_dashboard;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### 3. Enable HTTPS

Use Let's Encrypt or your SSL certificate:
```bash
sudo certbot --apache -d womensafety.example.com
```

## Performance Tips

- Use CDN for Bootstrap and icons (already configured)
- Enable browser caching
- Compress assets (gzip)
- Lazy load images
- Implement pagination for large datasets

## Contributing

To add new features:

1. Create new HTML page
2. Add corresponding JavaScript file
3. Update navigation menu
4. Test across browsers
5. Document new features

## License

MIT License

## Support

For issues and questions:
- GitHub Issues: [repository-url]
- Email: support@womensafety.com
