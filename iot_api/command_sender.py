"""Command Sender

Sends commands to ESP32 devices.
"""

import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class CommandSender:
    """Send commands to IoT devices"""
    
    def __init__(self):
        self.pending_commands = {}  # device_id -> list of commands
        logger.info("CommandSender initialized")
    
    def send_command(self, device_id: str, command: str, params: Dict = None) -> bool:
        """Queue command for device
        
        Commands:
        - activate_camera: Trigger ESP32-CAM to capture photo/video
        - activate_buzzer: Turn on buzzer/siren
        - fetch_gps: Request GPS coordinates
        - stream_audio: Start audio streaming
        - deactivate_alert: Turn off buzzer
        
        Args:
            device_id: Target device
            command: Command name
            params: Optional command parameters
            
        Returns:
            Success status
        """
        try:
            if device_id not in self.pending_commands:
                self.pending_commands[device_id] = []
            
            command_data = {
                'command': command,
                'params': params or {},
                'timestamp': datetime.now().isoformat()
            }
            
            self.pending_commands[device_id].append(command_data)
            logger.info(f"Command queued for {device_id}: {command}")
            
            return True
            
        except Exception as e:
            logger.error(f"Command queueing failed: {e}")
            return False
    
    def get_pending_commands(self, device_id: str) -> List[Dict]:
        """Get and clear pending commands for device
        
        Args:
            device_id: Device identifier
            
        Returns:
            List of pending commands
        """
        commands = self.pending_commands.get(device_id, [])
        
        # Clear after retrieval
        if device_id in self.pending_commands:
            self.pending_commands[device_id] = []
        
        return commands
    
    def activate_emergency_mode(self, device_id: str) -> bool:
        """Activate full emergency mode on device
        
        Sends multiple commands:
        - Activate camera
        - Activate buzzer
        - Stream GPS
        
        Args:
            device_id: Device identifier
            
        Returns:
            Success status
        """
        try:
            self.send_command(device_id, "activate_camera", {"duration": 30})
            self.send_command(device_id, "activate_buzzer", {"intensity": "high"})
            self.send_command(device_id, "stream_gps", {"interval": 5})
            
            logger.warning(f"Emergency mode activated for device {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Emergency activation failed: {e}")
            return False
