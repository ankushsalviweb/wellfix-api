"""
Script to check the contents of the .env file
"""
import os

def main():
    """
    Check the contents of the .env file and print them
    """
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    print(f"Checking .env file at: {env_path}")
    
    if not os.path.exists(env_path):
        print("Error: .env file not found!")
        return
    
    print("Contents of .env file:")
    with open(env_path, 'r') as f:
        for i, line in enumerate(f, 1):
            print(f"{i}: {line.rstrip()}")

if __name__ == "__main__":
    main() 