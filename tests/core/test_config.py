import os
import unittest
from unittest.mock import patch

from wellfix_api.core.config import Settings

class TestConfig(unittest.TestCase):
    """Test the configuration loading and validation."""
    
    @patch.dict(os.environ, {
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
        "JWT_SECRET_KEY": "test_secret_key",
        "JWT_ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "60"
    })
    def test_settings_load_from_env(self):
        """Test that settings are loaded from environment variables."""
        settings = Settings()
        
        self.assertEqual(settings.DATABASE_URL, "postgresql://test:test@localhost:5432/test")
        self.assertEqual(settings.JWT_SECRET_KEY, "test_secret_key")
        self.assertEqual(settings.JWT_ALGORITHM, "HS256")
        self.assertEqual(settings.ACCESS_TOKEN_EXPIRE_MINUTES, 60)
    
    @patch.dict(os.environ, {
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test", 
        "JWT_SECRET_KEY": "test_secret_key"
    })
    def test_settings_defaults(self):
        """Test that default values are used for optional settings."""
        settings = Settings()
        
        # These are the default values from the Settings class
        self.assertEqual(settings.JWT_ALGORITHM, "HS256")
        self.assertEqual(settings.ACCESS_TOKEN_EXPIRE_MINUTES, 60 * 24)  # 1 day
        self.assertEqual(settings.PROJECT_NAME, "WellFix API")

if __name__ == "__main__":
    unittest.main() 