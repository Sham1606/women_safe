"""Multi-recipient alert dispatcher using Twilio and SendGrid."""
import os
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

class AlertDispatcher:
    """Handles multi-recipient alert dispatching."""
    
    def __init__(self):
        # Twilio credentials
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
        self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token) if self.twilio_account_sid else None
        
        # SendGrid credentials
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.sendgrid_client = SendGridAPIClient(self.sendgrid_api_key) if self.sendgrid_api_key else None
        
        # Police/Emergency numbers
        self.police_numbers = ["+100", os.getenv('POLICE_CONTACT')]
        self.police_email = os.getenv('POLICE_EMAIL', 'emergency@police.gov')
        
    def dispatch_alert(self, alert_data):
        """
        Dispatch alert to multiple recipients.
        
        Args:
            alert_data (dict): {
                'alert_id': int,
                'device_uid': str,
                'owner_name': str,
                'owner_phone': str,
                'gps': {'lat': float, 'lng': float},
                'severity': str,
                'reason': str,
                'evidence': [{'type': str, 'path': str}],
                'emergency_contacts': [{'name': str, 'phone': str, 'email': str}]
            }
        """
        print(f"🚨 Dispatching alert #{alert_data['alert_id']}...")
        
        # 1. Send SMS to family/guardians
        self._notify_family(alert_data)
        
        # 2. Alert police/emergency services
        self._notify_police(alert_data)
        
        # 3. Send email with evidence
        self._send_evidence_email(alert_data)
        
        # 4. (Optional) Notify NGO/Community
        # self._notify_ngo(alert_data)
        
        print("✅ Alert dispatched to all recipients")
        
    def _notify_family(self, alert_data):
        """Send SMS to family members."""
        if not self.twilio_client:
            print("⚠️ Twilio not configured, skipping SMS")
            return
            
        # Build Google Maps link
        lat, lng = alert_data['gps']['lat'], alert_data['gps']['lng']
        maps_link = f"https://maps.google.com/?q={lat},{lng}"
        
        # Craft message
        message_body = f"""🚨 EMERGENCY ALERT 🚨

{alert_data['owner_name']} needs immediate help!

Location: {maps_link}
Severity: {alert_data['severity']}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

View evidence and track live:
https://yourwebsite.com/alerts/{alert_data['alert_id']}

Call police immediately: 100
        """
        
        # Send to emergency contacts
        for contact in alert_data.get('emergency_contacts', []):
            try:
                message = self.twilio_client.messages.create(
                    body=message_body,
                    from_=self.twilio_phone,
                    to=contact['phone']
                )
                print(f"✅ SMS sent to {contact['name']} ({contact['phone']}): {message.sid}")
            except Exception as e:
                print(f"❌ SMS failed to {contact['phone']}: {e}")
                
    def _notify_police(self, alert_data):
        """Alert police with automated call and push notification."""
        if not self.twilio_client:
            print("⚠️ Twilio not configured, skipping police call")
            return
            
        lat, lng = alert_data['gps']['lat'], alert_data['gps']['lng']
        
        # TwiML for automated call
        twiml_url = f"http://yourserver.com/twiml/emergency?alert_id={alert_data['alert_id']}"
        
        for police_number in self.police_numbers:
            try:
                call = self.twilio_client.calls.create(
                    url=twiml_url,
                    to=police_number,
                    from_=self.twilio_phone
                )
                print(f"✅ Emergency call to police: {call.sid}")
            except Exception as e:
                print(f"❌ Call failed to {police_number}: {e}")
                
    def _send_evidence_email(self, alert_data):
        """Send email with evidence attachments to police and family."""
        if not self.sendgrid_client:
            print("⚠️ SendGrid not configured, skipping email")
            return
            
        lat, lng = alert_data['gps']['lat'], alert_data['gps']['lng']
        maps_link = f"https://maps.google.com/?q={lat},{lng}"
        
        # Build HTML email
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #d32f2f;">🚨 Emergency Alert #{alert_data['alert_id']}</h2>
            <p><strong>Person:</strong> {alert_data['owner_name']}</p>
            <p><strong>Device:</strong> {alert_data['device_uid']}</p>
            <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p><strong>Severity:</strong> <span style="color: #d32f2f;">{alert_data['severity']}</span></p>
            <p><strong>Reason:</strong> {alert_data['reason']}</p>
            <hr>
            <h3>Location:</h3>
            <p>📍 Coordinates: {lat}, {lng}</p>
            <p><a href="{maps_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View on Google Maps</a></p>
            <hr>
            <h3>Evidence:</h3>
            <ul>
        """
        
        for evidence in alert_data.get('evidence', []):
            evidence_url = f"https://yourwebsite.com/static/evidence/{evidence['path']}"
            html_content += f"<li><a href='{evidence_url}'>{evidence['type']}: {evidence['path']}</a></li>"
            
        html_content += """
            </ul>
            <hr>
            <p><a href="https://yourwebsite.com/alerts/{}">View Full Alert Dashboard</a></p>
            <p style="color: #666; font-size: 12px;">This is an automated alert from the Women's Safety System.</p>
        </body>
        </html>
        """.format(alert_data['alert_id'])
        
        # Send to police
        try:
            message = Mail(
                from_email='noreply@womensafety.com',
                to_emails=self.police_email,
                subject=f"🚨 URGENT: Emergency Alert #{alert_data['alert_id']} - {alert_data['owner_name']}",
                html_content=html_content
            )
            response = self.sendgrid_client.send(message)
            print(f"✅ Email sent to police: {response.status_code}")
        except Exception as e:
            print(f"❌ Email failed: {e}")
            
        # Send to emergency contacts
        for contact in alert_data.get('emergency_contacts', []):
            if contact.get('email'):
                try:
                    message = Mail(
                        from_email='noreply@womensafety.com',
                        to_emails=contact['email'],
                        subject=f"🚨 URGENT: {alert_data['owner_name']} needs help!",
                        html_content=html_content
                    )
                    response = self.sendgrid_client.send(message)
                    print(f"✅ Email sent to {contact['name']}: {response.status_code}")
                except Exception as e:
                    print(f"❌ Email failed to {contact['email']}: {e}")
                    
    def send_test_alert(self):
        """Send test alert for debugging."""
        test_data = {
            'alert_id': 999,
            'device_uid': 'SHIELD-TEST-001',
            'owner_name': 'Test User',
            'owner_phone': '+919876543210',
            'gps': {'lat': 11.9416, 'lng': 79.8083},
            'severity': 'HIGH',
            'reason': 'TEST_ALERT',
            'evidence': [
                {'type': 'AUDIO', 'path': 'test_audio.wav'},
                {'type': 'IMAGE', 'path': 'test_image.jpg'}
            ],
            'emergency_contacts': [
                {'name': 'Emergency Contact', 'phone': '+919876543210', 'email': 'test@example.com'}
            ]
        }
        self.dispatch_alert(test_data)


if __name__ == "__main__":
    # Test the alert dispatcher
    dispatcher = AlertDispatcher()
    dispatcher.send_test_alert()
