"""
Script to run the Alembic migration
"""
import os
import sys
import subprocess

def main():
    """
    Run the Alembic migration to apply changes to the database
    """
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Set DATABASE_URL environment variable for testing (SQLite in-memory)
        os.environ["DATABASE_URL"] = "sqlite:///./test.db"
        os.environ["JWT_SECRET_KEY"] = "test_key_for_development"
        os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "1440"
        
        # Run the migration
        print("Running Alembic migration...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Migration successful!")
            print(result.stdout)
        else:
            print(f"Migration failed with code {result.returncode}")
            print("Output:")
            print(result.stdout)
            print("Error:")
            print(result.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error running migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 