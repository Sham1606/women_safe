# 🛡️ Shield System: End-to-End UI Walkthrough

Follow these steps to experience the full proactive safety system, from initial setup to emergency response.

---

## 🔐 Phase 1: Authentication & Identity
**Goal:** Verify the multi-role security system.

1.  **Navigate to Home:** Open `http://127.0.0.1:5000/`. You should see the premium glass-card login screen.
2.  **Test Secure Login:**
    *   **Guardian Login:** Use `guardian@safe.com` / `guardian123`.
    *   **Admin Login:** Use `admin@safety.com` / `admin123`.
3.  **Unified Registration:**
    *   Switch to the **JOIN** tab.
    *   Enter a name, email, and a unique **Device UID** (e.g., `SHIELD-TEST-99`).
    *   Click **Create Account**. You will be registered and your device linked in one step!

---

## 📡 Phase 2: Guardian Command Center
**Goal:** Monitor live vitals and device status.

1.  **Live Map:** Upon login as a Guardian, the map will automatically zoom (`fitBounds`) to show your active devices.
2.  **Dynamic Markers:** You should see a **blue user icon marker** at the last known location of your device.
3.  **Vitals Monitoring:** The "My Devices" panel on the right shows:
    *   **❤️ Heart Rate** & **🌡️ Temperature**.
    *   **🔋 Battery** Level.
    *   **🧠 AI SENSE**: Displays real-time stress probability and AI label.

---

## 🚨 Phase 3: The Emergency Flow (Triggering SHIELD)
**Goal:** See the system react to danger.

1.  **Simulate Stress:** Use Postman or the device script to send an event with a high heart rate (`> 100`) or a "stressed" audio label to `http://127.0.0.1:5000/api/device/event`.
2.  **Visual Alert:**
    *   The map marker will instantly turn **RED** and start **PULSATING** with a sonar effect.
    *   The device card in the sidebar will turn **RED** with a "⚠️ EMERGENCY" tag.
3.  **View Evidence:**
    *   Click the **VIEW** button on the device card.
    *   A modal opens showing the **Reason** (AI Stress vs Manual SOS) and captured **Audio Evidence**.
    *   Play the audio directly in the dashboard to hear the distress signal.

---

## 🏛️ Phase 4: Law Enforcement / Admin View
**Goal:** Oversee the entire system.

1.  **Login as Admin:** Use `admin@safety.com` / `admin123`.
2.  **System Stats:** See the glass-card summaries for:
    *   Total Users in the system.
    *   Total Active Devices.
    *   Global Alert Count.
3.  **Recent Activity:** A real-time table shows the latest 5 alerts across all users.
4.  **Resolve Alerts:** Admins can click individual alerts and mark them as **RESOLVED** to clear the distress signal.

---

## 🚫 Phase 5: Resilience Test
**Goal:** Verify error handling.

1.  **Type a Fake URL:** Go to `http://127.0.0.1:5000/nowhere`.
2.  **The 404 Experience:** You should see the custom "Distress Signal Lost" page, allowing you to quickly return to safety via the button.

---

### 🛠️ Quick Troubleshooting
*   **Map is blank?** Ensure you have an active internet connection (for Leaflet tiles) and that your browser allows location access.
*   **No Vitals?** Send a test event to `/api/device/event` to populate the database.
*   **Token Expired?** Simply logout and log back in to refresh your secure session.
