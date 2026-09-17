"""
Singleton Tello Connection Manager.
Ensures only one Tello instance exists to prevent UDP port conflicts
between command execution and video streaming.
"""
from djitellopy import Tello
import logging

logger = logging.getLogger(__name__)

class TelloManager:
    _instance = None
    _tello = None
    _is_connected = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelloManager, cls).__new__(cls)
        return cls._instance

    def get_tello(self) -> Tello:
        """Get the existing Tello instance or create a new one."""
        if self._tello is None:
            logger.info("Creating new Tello instance...")
            self._tello = Tello()
            self._is_connected = False
        return self._tello

    def connect(self) -> bool:
        """Connect to the Tello drone if not already connected."""
        if self._is_connected:
            logger.info("Tello already connected.")
            return True
        
        try:
            tello = self.get_tello()
            logger.info("Connecting to Tello...")
            tello.connect()
            self._is_connected = True
            logger.info("Tello connected successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Tello: {e}")
            self._is_connected = False
            return False

    def disconnect(self):
        """Disconnect and clean up the Tello instance."""
        if self._tello and self._is_connected:
            try:
                logger.info("Disconnecting Tello...")
                self._tello.end()
                self._is_connected = False
                logger.info("Tello disconnected.")
            except Exception as e:
                logger.error(f"Error disconnecting Tello: {e}")
                self._is_connected = False

    def is_connected(self) -> bool:
        """Check if Tello is currently connected."""
        return self._is_connected

    def get_battery(self) -> int:
        """Get battery level if connected."""
        if self._is_connected and self._tello:
            try:
                return self._tello.get_battery()
            except:
                return -1
        return -1

# Global accessor for convenience
def get_tello_manager() -> TelloManager:
    return TelloManager()
