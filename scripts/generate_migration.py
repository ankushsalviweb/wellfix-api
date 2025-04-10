"""
Script to generate an Alembic migration
"""
import os
import sys
from alembic.config import Config
from alembic import command

def main():
    """
    Generate an initial migration for the User and Address models
    """
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory (project root)
    parent_dir = os.path.dirname(current_dir)
    
    # Create the Alembic config
    alembic_cfg = Config(os.path.join(parent_dir, "alembic.ini"))
    
    # Generate the migration
    try:
        command.revision(alembic_cfg, 
                        message="Initial_User_and_Address_models",
                        autogenerate=True)
        print("Migration generated successfully!")
    except Exception as e:
        print(f"Error generating migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 