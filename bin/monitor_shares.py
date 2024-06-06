#! /usr/bin/python3

import os
import time
import subprocess

MOUNT_CHECK_INTERVAL = 60  # Seconds between mount checks
GOTIFY_API_URL = "https://example.com/gotify"  # Replace with your Gotify API URL
CONFIG_FILE = "/root/runtipi/etc/monitor_shares.conf"

def get_mount_points():
    with open("/etc/fstab", "r") as f:
        mount_points = [line.split()[1] for line in f.readlines() if line.strip() and not line.startswith("#") and "swap" not in line]
    return mount_points

def is_mounted(mount_point):
    return os.path.ismount(mount_point)

def send_gotify_notification(title, message):
    try:
        subprocess.run(["gotify", "push", f"--title={title}", message])
    except:
        False

def mount_shares():
    subprocess.run(["mount", "-a"])

def start_app(app_name):
    original_dir = os.getcwd()
    os.chdir("/root/runtipi")
    subprocess.run(["./runtipi-cli", "app", "start", app_name])
    os.chdir(original_dir)

def stop_app(app_name):
    original_dir = os.getcwd()
    os.chdir("/root/runtipi")
    subprocess.run(["./runtipi-cli", "app", "stop", app_name])
    os.chdir(original_dir)

def get_app_names_from_config():
    app_names = []
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            app_names = [line.strip() for line in f.readlines() if line.strip()]
    return app_names

def monitor_mounts():
    mount_points = get_mount_points()
    app_names = get_app_names_from_config() or ["sabnzbd", "sonarr", "radarr"]
    hostname = os.uname().nodename

    while True:
        for mount_point in mount_points:
            if not is_mounted(mount_point):
                send_gotify_notification(hostname, f"{mount_point} is disconnected.")
                for app_name in app_names:
                    stop_app(app_name)

                while not is_mounted(mount_point):
                    mount_shares()
                    time.sleep(MOUNT_CHECK_INTERVAL)

                for app_name in app_names:
                    start_app(app_name)
                send_gotify_notification(hostname, f"{mount_point} reconnected.")

        time.sleep(MOUNT_CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_mounts()
