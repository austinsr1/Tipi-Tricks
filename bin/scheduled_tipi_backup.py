#!/usr/bin/python3

import os
import subprocess
import time
import configparser
from datetime import datetime

# Define paths and constants
BASE_DIR = "/root/runtipi"
BACKUP_DIR = os.path.join(BASE_DIR, "backup")
CONFIG_FILE = os.path.join(BASE_DIR, "etc", "scheduled_tipi_backup.conf")
DEFAULT_MAX_BACKUPS = 7

# Directories and files to include in the backup
ITEMS_TO_BACKUP = [
    "app-data",
    "apps",
    "data",
    "docker-compose.yml",
    "logs",
    "media",
    "repos",
    "runtipi-cli",
    "traefik",
    "user-config",
    "VERSION"
]

def create_backup():
    # Ensure backup directory exists
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    # Get the current time for the backup filename
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_filename = f"Tipi_{current_time}.tar.gz"
    backup_filepath = os.path.join(BACKUP_DIR, backup_filename)

    # Create tarball with --one-file-system option using subprocess
    cmd = ["tar", "--one-file-system", "-czf", backup_filepath]
    cmd.extend([os.path.join(BASE_DIR, item) for item in ITEMS_TO_BACKUP])
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error creating backup: {result.stderr.decode('utf-8')}")
    else:
        print(f"Backup created: {backup_filepath}")
        manage_backups()

def manage_backups():
    # Read the config file to get the maximum number of backups to keep
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        max_backups = int(config.get("settings", "max_backups", fallback=DEFAULT_MAX_BACKUPS))
    else:
        max_backups = DEFAULT_MAX_BACKUPS

    # List all backup files and sort them by modification time
    backup_files = [f for f in os.listdir(BACKUP_DIR) if f.startswith("Tipi_") and f.endswith(".tar.gz")]
    backup_files.sort(key=lambda f: os.path.getmtime(os.path.join(BACKUP_DIR, f)))

    # Remove old backups if necessary
    while len(backup_files) > max_backups:
        oldest_backup = backup_files.pop(0)
        os.remove(os.path.join(BACKUP_DIR, oldest_backup))
        print(f"Removed old backup: {oldest_backup}")

if __name__ == "__main__":
    manage_backups()
    create_backup()
