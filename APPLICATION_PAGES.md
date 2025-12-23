# 🗺️ Complete Application Structure - Shield System

## 🏛️ All Available Pages

### 🔓 **Public Pages** (No Login Required)

#### 1. **Landing Page** - `/`
- **File:** `backend/templates/index.html` + `frontend/index.html`
- **Features:**
  - Login form
  - Registration form
  - Role selection (Guardian/Police/Admin)
  - JWT authentication
- **Access:** Everyone

#### 2. **Device Simulator** - `/simulator`
- **File:** `backend/templates/device_simulator.html`
- **Features:**
  - Test device events without hardware
  - Send vitals (HR, Temp, SpO2)
  - Upload test audio files
  - Trigger manual SOS
  - Real-time API testing
- **Access:** Everyone
- **Use Case:** Testing and development

#### 3. **Help & Documentation** - `/help`
- **File:** `backend/templates/help.html`
- **Features:**
  - Getting started guide
  - Device management instructions
  - Alert system explained
  - Troubleshooting
  - FAQ
  - Contact support
- **Access:** Everyone

---

### 🔒 **Protected Pages** (Login Required)

#### 4. **Main Dashboard** - `/dashboard`
- **File:** `backend/templates/dashboard.html` + `frontend/dashboard.html`
- **Features:**
  - **Guardian View:**
    - My devices list
    - Device cards with vitals
    - Add device button
    - Battery status
    - Active alerts
  - **Police/Admin View:**
    - System-wide alerts
    - Statistics dashboard
    - Recent activity table
  - **All Roles:**
    - Interactive map with device locations
    - Real-time updates
    - Role-based UI
- **Access:** Guardian, Police, Admin

#### 5. **Alerts Management** - `/alerts`
- **File:** `backend/templates/alerts.html`
- **Features:**
  - Alert list with filters
  - Status badges (NEW, IN_PROGRESS, RESOLVED)
  - Sort by timestamp/severity
  - Alert detail modal
  - Evidence playback (audio/photo)
  - GPS coordinates
  - Status updates (Police/Admin only)
- **Access:** Guardian (own alerts), Police, Admin (all alerts)

#### 6. **Profile** - `/profile`
- **File:** `backend/templates/profile.html`
- **Features:**
  - User information display
  - Name, email, role
  - Account statistics
  - Registered devices count
  - Total alerts
  - Edit profile details
- **Access:** All authenticated users

#### 7. **Notifications** - `/notifications`
- **File:** `backend/templates/notifications.html`
- **Features:**
  - Real-time notification feed
  - Filter by type (Alerts/Devices/System)
  - Mark as read/unread
  - Clear all notifications
  - Time-based grouping
  - Click to view details
- **Access:** All authenticated users

#### 8. **Live Monitor** - `/monitor`
- **File:** `backend/templates/live_monitor.html`
- **Features:**
  - Real-time device feed (updates every 5s)
  - Live vitals chart (Heart Rate & Temperature)
  - System status panel:
    - Active devices count
    - Pending alerts count
    - Events per minute
    - System health indicator
  - Recent events timeline
  - Color-coded device cards
  - Alert animations
- **Access:** All authenticated users

#### 9. **Device Management** - `/devices`
- **File:** `backend/templates/device_management.html`
- **Features:**
  - Complete device list
  - Add new devices
  - View device details
  - Remove devices
  - Device statistics:
    - Total devices
    - Online/offline count
    - Devices with alerts
  - Quick actions:
    - Refresh all
    - Bulk operations
    - Export device data (CSV)
  - Detailed device modal:
    - Device info
    - Battery status
    - GPS location
    - Latest vitals
    - Alert history
- **Access:** Guardian (own devices), Admin (all devices)

#### 10. **Evidence Gallery** - `/evidence`
- **File:** `backend/templates/evidence_gallery.html`
- **Features:**
  - Grid view of all evidence files
  - Filter by:
    - Type (Audio/Photo/Video)
    - Date range
    - Alert ID
  - Evidence thumbnails
  - View/play evidence
  - Download evidence files
  - Linked to alert details
- **Access:** Police, Admin only

#### 11. **Settings** - `/settings`
- **File:** `backend/templates/settings.html`
- **Features:**
  - **Profile Settings:**
    - Edit name, phone
    - Email (read-only)
  - **Notification Preferences:**
    - Email notifications
    - SMS notifications
    - Push notifications
    - Sound alerts
    - Notification types filter
  - **Alert Preferences:**
    - Heart rate threshold
    - Temperature threshold
    - AI confidence threshold
    - Emergency contacts
  - **Security:**
    - Change password
    - Two-factor authentication
    - Active sessions
    - Logout all devices
  - **Device Configuration:**
    - Data sync interval
    - Audio recording quality
    - Auto audio capture
    - GPS tracking toggle
- **Access:** All authenticated users

---

### 🔑 **Admin/Police Only Pages**

#### 12. **Admin Panel** - `/admin`
- **File:** `backend/templates/admin_panel.html`
- **Features:**
  - System overview dashboard
  - User management
  - Device analytics
  - Alert statistics
  - System health monitoring
  - User roles management
- **Access:** Admin, Police

#### 13. **Analytics Dashboard** - `/analytics`
- **File:** `backend/templates/analytics.html`
- **Features:**
  - Charts and graphs
  - Alert trends over time
  - Device usage statistics
  - Response time metrics
  - Geographical heat maps
  - Export reports
- **Access:** Admin, Police

---

### 🛠️ **Utility Pages**

#### 14. **404 Error Page**
- **File:** `backend/templates/404.html`
- **Features:**
  - Custom error message
  - Back to home button
  - Navigation links
- **Access:** Shown on invalid URLs

#### 15. **Test Suite Interface** - `/test`
- **File:** `backend/templates/test_suite.html`
- **Features:**
  - Run test commands
  - View test results
  - API endpoint testing
  - Developer tools
- **Access:** Developers only

---

## 🧭 **Component Templates**

#### 16. **Base Template** - `base.html`
- **File:** `backend/templates/base.html`
- **Features:**
  - Common layout structure
  - Navigation bar
  - Footer
  - CSS/JS includes
  - All pages extend this

#### 17. **Modals** - `modals.html`
- **File:** `backend/templates/modals.html`
- **Features:**
  - Reusable modal components
  - Alert detail modal
  - Add device modal
  - Confirmation dialogs

---

## 🗂️ Complete Page Navigation Map

```
🏗️ SHIELD SYSTEM
│
├── 🔓 PUBLIC
│   ├── / (Landing Page - Login/Register)
│   ├── /simulator (Device Simulator)
│   └── /help (Help & Documentation)
│
├── 🔒 AUTHENTICATED
│   ├── /dashboard (Main Dashboard)
│   ├── /alerts (Alert Management)
│   ├── /profile (User Profile)
│   ├── /notifications (Notifications Feed)
│   ├── /monitor (Live Monitoring)
│   ├── /devices (Device Management)
│   └── /settings (Settings & Preferences)
│
├── 🔑 ADMIN/POLICE ONLY
│   ├── /admin (Admin Panel)
│   ├── /analytics (Analytics Dashboard)
│   └── /evidence (Evidence Gallery)
│
└── 🛠️ UTILITY
    ├── /test (Test Suite)
    └── 404 (Error Page)
```

---

## 🚦 Access Control Matrix

| Page | Guardian | Police | Admin | Public |
|------|----------|--------|-------|--------|
| Landing Page | ✅ | ✅ | ✅ | ✅ |
| Device Simulator | ✅ | ✅ | ✅ | ✅ |
| Help | ✅ | ✅ | ✅ | ✅ |
| Dashboard | ✅ | ✅ | ✅ | ❌ |
| Alerts | ✅* | ✅ | ✅ | ❌ |
| Profile | ✅ | ✅ | ✅ | ❌ |
| Notifications | ✅ | ✅ | ✅ | ❌ |
| Live Monitor | ✅ | ✅ | ✅ | ❌ |
| Device Management | ✅* | ❌ | ✅ | ❌ |
| Evidence Gallery | ❌ | ✅ | ✅ | ❌ |
| Settings | ✅ | ✅ | ✅ | ❌ |
| Admin Panel | ❌ | ✅ | ✅ | ❌ |
| Analytics | ❌ | ✅ | ✅ | ❌ |

*✅* = Limited access (own data only)

---

## 🎓 User Journey by Role

### **👥 Guardian Journey**

```
1. Login → /
2. View Dashboard → /dashboard
   - See my devices
   - Check vitals
   - View active alerts
3. Add Device → Click "+ Add Device"
4. Monitor Device → /monitor
   - Real-time vitals
   - Live charts
5. Check Alerts → /alerts
   - View alert history
   - See evidence
6. Manage Devices → /devices
   - Edit device info
   - Export data
7. Configure Settings → /settings
   - Set thresholds
   - Add emergency contacts
```

### **👮 Police Journey**

```
1. Login → /
2. View System Dashboard → /dashboard
   - All system alerts
   - Statistics
3. Respond to Alerts → /alerts
   - View all alerts
   - Update status (NEW → IN_PROGRESS → RESOLVED)
   - Access evidence
4. Review Evidence → /evidence
   - Audio recordings
   - Photos
   - GPS data
5. Monitor System → /monitor
   - Real-time feed
   - System health
6. View Analytics → /analytics
   - Response times
   - Alert trends
7. Admin Tasks → /admin
   - User management
   - System settings
```

### **🔑 Admin Journey**

```
1. Login → /
2. System Overview → /dashboard
   - All statistics
   - System health
3. Admin Panel → /admin
   - User management
   - Device analytics
   - System configuration
4. Analytics → /analytics
   - Detailed reports
   - Export data
5. Evidence Management → /evidence
   - Full access
   - Download/delete
6. Alert Management → /alerts
   - Full system view
   - Bulk operations
7. All other pages with full access
```

---

## 🎯 Key Features by Page

### **Most Important Pages:**

1. **Dashboard** - Main hub for all users
2. **Alerts** - Core functionality for emergency response
3. **Device Management** - Device lifecycle management
4. **Live Monitor** - Real-time monitoring and charts
5. **Settings** - User preferences and configuration

### **Secondary Pages:**

6. **Notifications** - Stay informed
7. **Evidence Gallery** - Legal/investigative use
8. **Analytics** - Decision making
9. **Admin Panel** - System management
10. **Profile** - Account management

### **Utility Pages:**

11. **Device Simulator** - Testing without hardware
12. **Help** - User guidance
13. **Test Suite** - Development/QA

---

## 📱 Mobile Responsiveness

All pages are **mobile-responsive** using Bootstrap 5:

- **Landing Page:** Mobile-optimized forms
- **Dashboard:** Stacked cards on mobile
- **Alerts:** Scrollable list view
- **Monitor:** Vertical layout
- **Device Management:** Grid adapts to screen size
- **Settings:** Accordion-style sections

---

## 🎨 UI/UX Features Across All Pages

### **Common Elements:**

- ✅ **Navigation Bar** - Consistent across all pages
- ✅ **Breadcrumbs** - Show current location
- ✅ **Toast Notifications** - Success/error messages
- ✅ **Loading Spinners** - During API calls
- ✅ **Modal Dialogs** - For forms and confirmations
- ✅ **Card Components** - Clean, organized layout
- ✅ **Responsive Tables** - Horizontal scroll on mobile
- ✅ **Search & Filters** - Quick data access
- ✅ **Real-time Updates** - Auto-refresh functionality
- ✅ **Dark Theme** - Eye-friendly colors

### **Animations:**

- 🔴 **Pulsing Red Markers** - For active alerts on map
- ✨ **Fade In/Out** - For modals and notifications
- 🔄 **Spin Animations** - For loading states
- 📈 **Chart Transitions** - Smooth data updates

---

## 🔌 API Integration

Every page connects to backend APIs:

### **Authentication APIs:**
- POST `/api/auth/register`
- POST `/api/auth/login`
- GET `/api/auth/me`

### **Device APIs:**
- GET `/api/device/my-devices`
- POST `/api/device/register`
- POST `/api/device/event`

### **Alert APIs:**
- GET `/api/alerts`
- GET `/api/alerts/<id>`
- PATCH `/api/alerts/<id>/status`

### **Admin APIs:**
- GET `/api/admin/stats`
- GET `/api/admin/users`

---

## 🛠️ Testing Each Page

### **Quick Test Checklist:**

```bash
# Start the server
python run.py

# Access pages in order:

1. http://localhost:5000/                # Landing
2. http://localhost:5000/simulator       # Simulator
3. http://localhost:5000/help            # Help

# Login first with:
Email: guardian@safe.com
Password: guardian123

4. http://localhost:5000/dashboard       # Dashboard
5. http://localhost:5000/alerts          # Alerts
6. http://localhost:5000/profile         # Profile
7. http://localhost:5000/notifications   # Notifications
8. http://localhost:5000/monitor         # Live Monitor
9. http://localhost:5000/devices         # Device Mgmt
10. http://localhost:5000/settings       # Settings

# Login as admin for:
Email: admin@safety.com
Password: admin123

11. http://localhost:5000/admin          # Admin Panel
12. http://localhost:5000/analytics      # Analytics
13. http://localhost:5000/evidence       # Evidence
```

---

## 📝 Summary

### **Total Pages: 15+**

- **Public:** 3 pages
- **Authenticated:** 8 pages
- **Admin/Police:** 3 pages
- **Utility:** 2 pages

### **Total Features:**

- ✅ Complete authentication system
- ✅ Role-based access control
- ✅ Real-time monitoring
- ✅ AI-powered stress detection
- ✅ Interactive maps
- ✅ Evidence management
- ✅ Notification system
- ✅ Device lifecycle management
- ✅ Analytics dashboard
- ✅ Settings & preferences
- ✅ Help & documentation
- ✅ Testing tools

### **Technologies:**

- **Backend:** Flask 3.0, SQLAlchemy, JWT
- **Frontend:** Bootstrap 5, Vanilla JS, Leaflet.js, Chart.js
- **AI:** TensorFlow, Librosa
- **Database:** SQLite (dev), PostgreSQL-ready (prod)

---

## 🚀 Next Steps

1. **Test all pages** using the checklist above
2. **Customize branding** in `base.html`
3. **Configure settings** in `settings.html`
4. **Add real devices** or use simulator
5. **Deploy to production** (see deployment docs)

---

**Your Flask application is now fully furnished with all essential pages! 🎉**
