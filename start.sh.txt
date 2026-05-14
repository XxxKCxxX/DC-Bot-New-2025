#!/bin/bash

# Navigate to the repository directory (optional if running from within it)
# cd /path/to/your/repo

while true
do
    echo "Checking for updates..."
    # Pull the latest changes from the current branch
    git pull origin $(git rev-parse --abbrev-ref HEAD)

    echo "Starting the Python program..."
    # Replace 'main.py' with your entry point script
    python3 main.py

    # Optional: Add a small delay to prevent rapid-fire looping if 
    # the script crashes immediately on startup.
    echo "Program crashed or exited. Restarting in 5 seconds..."
    sleep 5
done