"""
Script to run tests with proper environment variables
"""
import os
import sys
import subprocess

def main():
    """
    Run the tests with proper environment variables
    """
    # Set environment variables for testing
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["JWT_SECRET_KEY"] = "test_key_for_development"
    os.environ["JWT_ALGORITHM"] = "HS256"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "1440"
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Run the tests
        print("Running tests...")
        cmd = ["pytest", "-v"]
        if len(sys.argv) > 1:
            cmd.extend(sys.argv[1:])
        else:
            cmd.append("tests/")
            
        result = subprocess.run(
            cmd,
            cwd=project_root,
            env=os.environ
        )
        
        # Exit with the same code as the tests
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 