#!/usr/bin/python3

import os
import time
import subprocess
import argparse

MOUNT_CHECK_INTERVAL = 60  # Seconds between mount checks
GOTIFY_API_URL = "https://example.com/gotify"  # Replace with your Gotify API URL
CONFIG_FILE = "/root/runtipi/etc/monitor_shares.conf"

def parse_args():
    parser = argparse.ArgumentParser(description="Monitor and manage non-system mount points with Gotify notifications.")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode for detailed output")
    return parser.parse_args()

def debug_log(message):
    if args.debug:
        print(f"[DEBUG] {message}")

def get_mount_points():
    """ Fetches only user-defined non-system mount points from /etc/fstab """
    debug_log("Fetching non-system mount points from /etc/fstab")
    
    mount_points = []
    with open("/etc/fstab", "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                parts = line.split()
                if len(parts) < 3:
                    continue
                
                mount_point = parts[1]
                fs_type = parts[2]

                # Exclude system partitions and bind mounts
                if fs_type not in ["ext4", "vfat", "swap", "none"]:  
                    mount_points.append(mount_point)

    debug_log(f"Identified non-system mount points: {mount_points}")
    return mount_points

def is_mounted(mount_point):
    mounted = os.path.ismount(mount_point)
    debug_log(f"Checking if {mount_point} is mounted: {'Yes' if mounted else 'No'}")
    return mounted

def send_gotify_notification(title, message):
    debug_log(f"Sending Gotify notification: Title='{title}', Message='{message}'")
    try:
        result = subprocess.run(["gotify", "push", f"--title={title}", message], capture_output=True, text=True)
        debug_log(f"Gotify response: {result.stdout.strip()} (Exit code: {result.returncode})")
    except Exception as e:
        debug_log(f"Error sending Gotify notification: {e}")

def mount_shares():
    debug_log("Attempting to mount all shares using 'mount -a'")
    result = subprocess.run(["mount", "-a"], capture_output=True, text=True)
    debug_log(f"Mount output: {result.stdout.strip()} (Exit code: {result.returncode})")

def start_app(app_name):
    debug_log(f"Starting application: {app_name}")
    original_dir = os.getcwd()
    os.chdir("/root/runtipi")
    result = subprocess.run(["./runtipi-cli", "app", "start", app_name], capture_output=True, text=True)
    debug_log(f"Start output: {result.stdout.strip()} (Exit code: {result.returncode})")
    os.chdir(original_dir)

def stop_app(app_name):
    debug_log(f"Stopping application: {app_name}")
    original_dir = os.getcwd()
    os.chdir("/root/runtipi")
    result = subprocess.run(["./runtipi-cli", "app", "stop", app_name], capture_output=True, text=True)
    debug_log(f"Stop output: {result.stdout.strip()} (Exit code: {result.returncode})")
    os.chdir(original_dir)

def get_app_names_from_config():
    app_names = []
    if os.path.exists(CONFIG_FILE):
        debug_log(f"Reading application names from config file: {CONFIG_FILE}")
        with open(CONFIG_FILE, "r") as f:
            app_names = [line.strip() for line in f.readlines() if line.strip()]
        debug_log(f"Configured applications: {app_names}")
    return app_names

def monitor_mounts():
    debug_log("Starting mount monitoring")
    mount_points = get_mount_points()
    app_names = get_app_names_from_config() or ["sabnzbd", "sonarr", "radarr"]
    hostname = os.uname().nodename

    debug_log(f"Hostname: {hostname}")
    debug_log(f"Monitoring non-system mounts: {mount_points}")
    debug_log(f"Applications to manage: {app_names}")

    while True:
        for mount_point in mount_points:
            if not is_mounted(mount_point):
                debug_log(f"{mount_point} is disconnected.")
                send_gotify_notification(hostname, f"{mount_point} is disconnected.")

                for app_name in app_names:
                    stop_app(app_name)

                while not is_mounted(mount_point):
                    debug_log(f"Retrying mount for {mount_point}")
                    mount_shares()
                    time.sleep(MOUNT_CHECK_INTERVAL)

                debug_log(f"{mount_point} reconnected. Restarting applications.")
                for app_name in app_names:
                    start_app(app_name)

                send_gotify_notification(hostname, f"{mount_point} reconnected.")

        debug_log(f"Sleeping for {MOUNT_CHECK_INTERVAL} seconds before next check.")
        time.sleep(MOUNT_CHECK_INTERVAL)

if __name__ == "__main__":
    args = parse_args()
    monitor_mounts()
