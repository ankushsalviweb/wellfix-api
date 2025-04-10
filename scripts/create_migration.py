"""
Script to generate an Alembic migration while bypassing .env loading
"""
import os
import sys
import importlib
import contextlib
import uuid

def main():
    """
    Generate a migration for the PricingConfig model
    """
    # Temporarily monkey patch the dotenv load_dotenv to do nothing
    import dotenv
    original_load_dotenv = dotenv.load_dotenv
    dotenv.load_dotenv = lambda *args, **kwargs: True
    
    # Also patch the os.environ.get to handle the problematic environment variable
    original_get = os.environ.get
    def patched_get(key, default=None):
        if key == "ACCESS_TOKEN_EXPIRE_MINUTES":
            return "1440"
        elif key == "DATABASE_URL":
            # Use a dummy SQLite in-memory URL for offline mode
            return "sqlite:///:memory:"
        return original_get(key, default)
    os.environ.get = patched_get
    
    try:
        # Now we can safely import alembic without the .env loading issues
        from alembic.config import Config
        from alembic import command
        
        # Get the directory of this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Get the parent directory (project root)
        parent_dir = os.path.dirname(current_dir)
        
        # Create the Alembic config
        alembic_cfg = Config(os.path.join(parent_dir, "alembic.ini"))
        
        # Import the models to make sure they're registered with the Base metadata
        # Force a reload to ensure latest changes are included
        if "wellfix_api.models.pricing" in sys.modules:
            importlib.reload(sys.modules["wellfix_api.models.pricing"])
        else:
            import wellfix_api.models.pricing
        
        # Generate a UUID for the revision ID
        rev_id = str(uuid.uuid4())[:8]
        
        # Generate a migration script with a unique revision ID
        command.revision(alembic_cfg, 
                         message="Add PricingConfig model",
                         rev_id=rev_id,
                         autogenerate=False)
        print(f"Migration generated successfully with revision ID: {rev_id}")
    except Exception as e:
        print(f"Error generating migration: {e}")
        sys.exit(1)
    finally:
        # Restore the original functions
        dotenv.load_dotenv = original_load_dotenv
        os.environ.get = original_get

if __name__ == "__main__":
    main() 