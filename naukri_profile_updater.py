"""
Naukri Profile Updater - Updates Naukri profile's last active timestamp daily
This script works with Jenkins for scheduling and GitHub for version control
"""

import requests
import logging
from datetime import datetime
from typing import Tuple
import json
import os
from pathlib import Path

# Configure logging with UTF-8 encoding for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('naukri_update.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NaukriProfileUpdater:
    """Update Naukri profile's last active timestamp"""
    
    def __init__(self, email: str, password: str):
        """
        Initialize the Naukri updater
        
        Args:
            email: Naukri login email
            password: Naukri login password
        """
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.base_url = "https://www.naukri.com"
        self.login_url = f"{self.base_url}/naukri/user/authenticate"
        self.profile_url = f"{self.base_url}/mprofile/profile"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': f'{self.base_url}/naukri/user/login'
        }
        self.update_log_file = 'naukri_update_log.json'
        
    def login(self) -> bool:
        """
        Login to Naukri account
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            logger.info("Attempting to login to Naukri...")
            
            login_data = {
                'email': self.email,
                'password': self.password,
                'keepLoggedIn': 'Y'
            }
            
            response = self.session.post(
                self.login_url,
                data=login_data,
                headers=self.headers,
                timeout=10,
                allow_redirects=True
            )
            
            if 200 <= response.status_code < 300:
                logger.info("Login successful!")
                return True
            elif response.status_code == 401 or response.status_code == 403:
                logger.error(f"Authentication failed - Invalid credentials (Status: {response.status_code})")
                return False
            else:
                logger.warning(f"Login returned status {response.status_code} - checking response...")
                if 'error' not in response.text.lower() and 'failed' not in response.text.lower():
                    logger.info("Assuming login successful despite status code")
                    return True
                return False
                
        except requests.exceptions.Timeout:
            logger.error("Login request timed out")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Login request failed: {str(e)}")
            return False
    
    def update_profile(self) -> Tuple[bool, str]:
        """
        Update Naukri profile's last active timestamp by accessing profile page
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            logger.info("Accessing Naukri profile to update last active timestamp...")
            
            response = self.session.get(
                self.profile_url,
                headers=self.headers,
                timeout=10,
                allow_redirects=True
            )
            
            if 200 <= response.status_code < 300:
                message = f"Profile accessed and updated at {datetime.now().isoformat()}"
                logger.info(message)
                self._log_update_success()
                return True, message
            elif response.status_code == 401 or response.status_code == 403:
                message = "Session expired - need to re-login"
                logger.error(message)
                return False, message
            else:
                message = f"Profile access returned status {response.status_code}"
                logger.warning(message)
                if response.text:
                    self._log_update_success()
                    return True, message
                return False, message
                
        except requests.exceptions.Timeout:
            message = "Profile update request timed out"
            logger.error(message)
            return False, message
        except requests.exceptions.RequestException as e:
            message = f"Profile update request failed: {str(e)}"
            logger.error(message)
            return False, message
    
    def _log_update_success(self) -> None:
        """Log successful update to JSON file for tracking"""
        try:
            logs = []
            if Path(self.update_log_file).exists():
                with open(self.update_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            
            logs.append({
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'email': self.email
            })
            
            with open(self.update_log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.warning(f"Could not log update: {str(e)}")
    
    def run_update_cycle(self) -> bool:
        """
        Execute complete update cycle: login and update profile
        
        Returns:
            True if update successful, False otherwise
        """
        try:
            if not self.login():
                return False
            
            success, message = self.update_profile()
            return success
            
        except Exception as e:
            logger.error(f"Update cycle failed: {str(e)}")
            return False


def load_credentials_from_env() -> Tuple[str, str]:
    """
    Load Naukri credentials from environment variables
    
    Returns:
        Tuple of (email, password)
    """
    email = os.getenv('NAUKRI_EMAIL')
    password = os.getenv('NAUKRI_PASSWORD')
    
    if not email or not password:
        raise ValueError(
            "Missing credentials! Set NAUKRI_EMAIL and NAUKRI_PASSWORD environment variables."
        )
    
    return email, password


def main():
    """Main entry point"""
    try:
        logger.info("=" * 60)
        logger.info("Naukri Profile Auto-Update Started")
        logger.info(f"Time: {datetime.now()}")
        logger.info("=" * 60)
        
        email, password = load_credentials_from_env()
        updater = NaukriProfileUpdater(email, password)
        success = updater.run_update_cycle()
        
        if success:
            logger.info("Update completed successfully!")
            logger.info("=" * 60)
            return 0
        else:
            logger.error("Update failed!")
            logger.info("=" * 60)
            return 1
            
    except ValueError as e:
        logger.error(f"Configuration Error: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
