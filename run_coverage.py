import os
import subprocess
import sys

# First, run the fix_settings script to ensure environment variables are set correctly
print("Setting up environment variables...")
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "1440"  # Clean value

# Define test directories
test_dirs = [
    "tests/api/v1/",
    "tests/crud/",
    "tests/models/",
    "tests/core/"
]

# Check if a specific test path was provided
test_path = sys.argv[1] if len(sys.argv) > 1 else None

# Set up coverage command
if test_path:
    # Run coverage on specific test path
    cmd = f"python -m pytest {test_path} --cov=wellfix_api --cov-report=term --cov-report=html"
    print(f"Running coverage on specified tests: {test_path}")
else:
    # Run coverage on all test directories
    test_paths = " ".join(test_dirs)
    cmd = f"python -m pytest {test_paths} --cov=wellfix_api --cov-report=term --cov-report=html"
    print("Running coverage on all tests")

# Execute the command
result = subprocess.run(cmd, shell=True)

# Print summary
if result.returncode == 0:
    print("\n✅ Tests completed successfully!")
    print("HTML coverage report generated in the 'htmlcov' directory")
    print("Open 'htmlcov/index.html' in your browser to view the detailed report")
else:
    print("\n❌ Some tests failed. Please fix the issues before proceeding.") 