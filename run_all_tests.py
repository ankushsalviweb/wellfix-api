import os
import subprocess

# Set clean environment variables
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "1440"  # Clean value without comments

# Print the value to verify
print(f"Set ACCESS_TOKEN_EXPIRE_MINUTES to: {os.environ['ACCESS_TOKEN_EXPIRE_MINUTES']}")

# Run all tests
print("\nRunning all tests:")
subprocess.run("python -m pytest tests/", shell=True) 