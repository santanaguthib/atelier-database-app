"""
Configuration module for Atelier Database Application
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Database configuration"""
    
    # Database settings
    DB_SERVER = os.getenv('DB_SERVER', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'Atelier')
    DB_DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    

    
    # Role descriptions (for display only)
    ROLES = {
        'admin': 'Database Administrator (full access)',
        'manager': 'Manager (read/write access)',
        'tailor': 'Tailor (limited access to orders)',
        'cashier': 'Cashier (sees masked data)'
    }
    
    # Suggested usernames (for convenience)
    SUGGESTED_USERS = {
        'admin': 'atelier_admin',
        'manager': 'manager',
        'tailor': 'tailor_user',
        'cashier': 'cashier'
    }
    
    @classmethod
    def get_connection_string(cls, username, password):
        """Generate connection string with provided credentials"""
        return (
            f"DRIVER={{{cls.DB_DRIVER}}};"
            f"SERVER={cls.DB_SERVER};"
            f"DATABASE={cls.DB_NAME};"
            f"UID={username};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )
