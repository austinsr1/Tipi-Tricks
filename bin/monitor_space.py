#!/usr/bin/python3

import os
import shutil
import subprocess
import time
import sys
from configparser import ConfigParser, MissingSectionHeaderError
import argparse

# Default threshold if no config file is found
DEFAULT_THRESHOLD = 95

# Path to the config file
CONFIG_FILE = "/root/runtipi/etc/monitor_space.conf"

# Command to send notification
NOTIFICATION_CMD = "gotify push --title {hostname} drive is {drive_percent_full}"

# Commands to stop and start the process
STOP_CMD = "cd /root/runtipi && ./runtipi-cli stop"
START_CMD = "cd /root/runtipi && ./runtipi-cli start"

def get_drive_usage(debug=False):
    disk_usage = shutil.disk_usage("/")
    total = disk_usage.total
    used = disk_usage.used
    free = disk_usage.free
    drive_percent_full = (used / total) * 100  # Use floating-point division
    if debug:
        print(f"Debug: Disk usage - Total: {total}, Used: {used}, Free: {free}, Percent Full: {drive_percent_full:.2f}%")
    return drive_percent_full

def read_config(debug=False):
    config = ConfigParser()
    try:
        config.read(CONFIG_FILE)
        if debug:
            print(f"Debug: Reading config file {CONFIG_FILE}")
        if "thresholds" in config and "drive_usage" in config["thresholds"]:
            threshold = int(config["thresholds"]["drive_usage"])
            if debug:
                print(f"Debug: Found threshold in config file: {threshold}")
            return threshold
    except MissingSectionHeaderError as e:
        print(f"Error: {e}")
    if debug:
        print(f"Debug: Using default threshold: {DEFAULT_THRESHOLD}")
    return DEFAULT_THRESHOLD

def send_notification(hostname, drive_percent_full, debug=False):
    cmd = NOTIFICATION_CMD.format(hostname=hostname, drive_percent_full=drive_percent_full)
    if debug:
        print(f"Debug: Sending notification with command: {cmd}")
    try:
        subprocess.run(cmd, shell=True)
    except:
        False
def main():
    parser = argparse.ArgumentParser(description="Monitor disk space and manage processes")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    debug = args.debug
    hostname = os.uname().nodename
    if debug:
        print(f"Debug: Hostname is {hostname}")

    threshold = read_config(debug)
    last_notification_time = 0
    process_stopped = False

    while True:
        drive_percent_full = get_drive_usage(debug)

        if drive_percent_full >= threshold:
            current_time = time.time()
            if current_time - last_notification_time >= 600:
                send_notification(hostname, f"{drive_percent_full:.2f}%", debug)
                last_notification_time = current_time

            if drive_percent_full >= 15:
                if debug:
                    print(f"Debug: Drive percent full is {drive_percent_full:.2f}%, stopping the process")
                subprocess.run(STOP_CMD, shell=True)
                process_stopped = True

        if drive_percent_full < 15 and process_stopped:
            if debug:
                print(f"Debug: Drive percent full is {drive_percent_full:.2f}%, restarting the process")
            subprocess.run(START_CMD, shell=True)
            process_stopped = False

        if debug:
            print(f"Debug: Sleeping for 1 minute")
        time.sleep(60)  # Wait for 1 minute

if __name__ == "__main__":
    main()
