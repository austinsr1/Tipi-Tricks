#!/usr/bin/python3
import os
import subprocess
import sys
import argparse
import time

SERVICE_NAME = "drive-health-monitor.service"
SERVICE_FILE_PATH = f"/etc/systemd/system/{SERVICE_NAME}"
SCRIPT_PATH = os.path.abspath(__file__)
CHECK_INTERVAL = 86400  # Default: 24 hours (in seconds)

def ensure_smartmontools():
    """Ensure smartmontools is installed, install if missing."""
    try:
        subprocess.run(["smartctl", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        print("smartmontools is not installed. Attempting to install it...")
        try:
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "smartmontools"], check=True)
            print("smartmontools installed successfully.")
        except subprocess.CalledProcessError:
            print("Failed to install smartmontools. Please install it manually with:")
            print("  sudo apt update && sudo apt install -y smartmontools")
            sys.exit(1)

def get_drives():
    """Get a list of drives on the system using lsblk."""
    try:
        result = subprocess.run(['lsblk', '-dn', '-o', 'NAME'], stdout=subprocess.PIPE, text=True, check=True)
        drives = result.stdout.strip().split('\n')
        drives = [f"/dev/{drive}" for drive in drives]
        return drives
    except subprocess.CalledProcessError as e:
        print(f"Error getting drives: {e}")
        return []

def check_drive_health(drive):
    """Check the SMART health of a drive."""
    try:
        result = subprocess.run(['smartctl', '-H', drive], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        if "PASSED" in result.stdout:
            return "PASSED"
        elif "FAILED" in result.stdout:
            return "FAILED"
        else:
            return "UNKNOWN"
    except subprocess.CalledProcessError as e:
        return "ERROR"

def send_gotify_notification(title, message):
    """Send a notification via Gotify."""
    try:
        subprocess.run(["gotify", "push", f"--title={title}", message], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to send Gotify notification: {e}")

def monitor_drives(interval):
    """Continuously monitor drives in a loop."""
    ensure_smartmontools()

    while True:
        print("Checking drive health...")
        drives = get_drives()
        if not drives:
            print("No drives found.")
        else:
            for drive in drives:
                health = check_drive_health(drive)
                if health == "FAILED":
                    message = f"{drive} is failing! Drive failure expected. Save your data immediately!"
                    print(message)
                    send_gotify_notification("Drive Failure Alert", message)
                elif health != "PASSED":
                    print(f"{drive}: Status unknown or error occurred.")
        print(f"Sleeping for {interval} seconds...")
        time.sleep(interval)

def install_service():
    """Create, enable, and start the systemd service."""
    service_content = f"""[Unit]
Description=Drive Health Monitoring Service
After=network.target

[Service]
ExecStart={SCRIPT_PATH} --interval {CHECK_INTERVAL}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""
    try:
        # Write the service file
        with open(SERVICE_FILE_PATH, "w") as service_file:
            service_file.write(service_content)
        print(f"Service file created at {SERVICE_FILE_PATH}")

        # Enable and start the service
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", SERVICE_NAME], check=True)
        subprocess.run(["systemctl", "start", SERVICE_NAME], check=True)
        print(f"Service {SERVICE_NAME} installed and started successfully.")
    except Exception as e:
        print(f"Failed to install the service: {e}")
        sys.exit(1)

def uninstall_service():
    """Stop and remove the systemd service."""
    try:
        if os.path.exists(SERVICE_FILE_PATH):
            subprocess.run(["systemctl", "stop", SERVICE_NAME], check=True)
            subprocess.run(["systemctl", "disable", SERVICE_NAME], check=True)
            os.remove(SERVICE_FILE_PATH)
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            print(f"Service {SERVICE_NAME} stopped and removed successfully.")
        else:
            print(f"Service file {SERVICE_FILE_PATH} does not exist.")
    except Exception as e:
        print(f"Failed to uninstall the service: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Check drive health status.")
    parser.add_argument('--install', action='store_true', help="Install and start the systemd service.")
    parser.add_argument('--uninstall', action='store_true', help="Stop and remove the systemd service.")
    parser.add_argument('--interval', type=int, default=CHECK_INTERVAL, help="Check interval in seconds (default: 24 hours)")
    args = parser.parse_args()

    if args.install:
        install_service()
    elif args.uninstall:
        uninstall_service()
    else:
        monitor_drives(args.interval)

if __name__ == "__main__":
    main()
