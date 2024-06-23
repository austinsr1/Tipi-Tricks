#!/usr/bin/python3

import subprocess
import re
import time
import argparse
import os
import configparser

CONFIG_FILE_PATH = '../etc/monitor_sensor.conf'
SERVICE_FILE_PATH = '/etc/systemd/system/monitor_sensor.service'

SERVICE_FILE_CONTENT = f"""[Unit]
Description=Monitor Sensor Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 {os.path.abspath(__file__)}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""

def check_and_install_lm_sensors(debug=False):
    check_install_cmd = 'dpkg -l | grep lm-sensors'
    result = subprocess.run(check_install_cmd, shell=True, capture_output=True, text=True)
    
    if 'lm-sensors' not in result.stdout:
        print("lm-sensors not found. Installing and configuring required software...")
        install_cmd = 'apt install lm-sensors -y && sensors-detect --auto && systemctl enable kmod && systemctl start kmod'
        if debug:
            print(f"Running command: {install_cmd}")
        subprocess.run(install_cmd, shell=True, check=True)
        print("lm-sensors installed and configured.")
    else:
        print("lm-sensors is already installed and configured.")

def get_sensor_data(debug=False):
    if debug:
        print("Running command: sensors")
    result = subprocess.run('sensors', shell=True, capture_output=True, text=True)
    return result.stdout

def parse_sensor_data(sensor_data, debug=False):
    sensors = {}
    sensor_lines = sensor_data.splitlines()
    
    current_sensor = None
    sensor_info = []

    for line in sensor_lines:
        if not line.strip() and current_sensor:
            sensors[current_sensor] = sensor_info
            current_sensor = None
            sensor_info = []
        elif not line.strip():
            continue
        elif not current_sensor:
            current_sensor = line.strip()
        else:
            sensor_info.append(line.strip())

    if current_sensor:
        sensors[current_sensor] = sensor_info
    
    if debug:
        print("Parsed sensor data:")
        for sensor, info in sensors.items():
            print(f"{sensor}:")
            for line in info:
                print(f"  {line}")

    return sensors

def display_and_choose_sensors(sensors, debug=False):
    sensor_names = list(sensors.keys())
    for idx, name in enumerate(sensor_names):
        print(f"{idx + 1}: {name}")
    
    chosen_idx = int(input("Enter the number of the sensor you want to monitor: ")) - 1
    chosen_sensor = sensor_names[chosen_idx]
    threshold_temp = float(input("Enter the threshold temperature (°C): "))
    optional_command = input("Enter an optional command to run if the threshold is reached (leave blank for none): ").strip()
    
    if debug:
        print(f"Chosen sensor: {chosen_sensor}")
        print(f"Threshold temperature: {threshold_temp}°C")
        if optional_command:
            print(f"Optional command: {optional_command}")
    
    return chosen_sensor, threshold_temp, optional_command

def save_config(sensor, threshold_temp, optional_command):
    config = configparser.ConfigParser()
    config['SETTINGS'] = {
        'sensor': sensor,
        'threshold_temp': str(threshold_temp)
    }
    if optional_command:
        config['SETTINGS']['optional_command'] = optional_command
    
    os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        config.write(config_file)

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE_PATH):
        config.read(CONFIG_FILE_PATH)
        if 'SETTINGS' in config:
            sensor = config['SETTINGS'].get('sensor')
            threshold_temp = config['SETTINGS'].getfloat('threshold_temp')
            optional_command = config['SETTINGS'].get('optional_command', None)
            return sensor, threshold_temp, optional_command
    return None, None, None

def send_gotify_notification(title, message):
    try:
        subprocess.run(["gotify", "push", f"--title={title}", message])
    except Exception as e:
        print(f"Failed to send Gotify notification: {e}")

def run_optional_command(command, debug=False):
    if command:
        try:
            if debug:
                print(f"Running optional command: {command}")
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to run optional command: {e}")

def monitor_sensor(sensor, threshold_temp, sensors, optional_command=None, debug=False):
    pattern = re.compile(r'\+([\d.]+)°C')
    check_interval = 10  # seconds

    print(f"Monitoring {sensor} for temperatures above {threshold_temp}°C...")

    while True:
        sensor_data = get_sensor_data(debug)
        parsed_sensors = parse_sensor_data(sensor_data, debug)
        
        for line in parsed_sensors[sensor]:
            match = pattern.search(line)
            if match:
                temp = float(match.group(1))
                if debug:
                    print(f"Current temperature of {sensor}: {temp}°C")
                if temp > threshold_temp:
                    alert_message = f"{sensor} temperature is {temp}°C, which is above the threshold of {threshold_temp}°C."
                    print(f"Alert! {alert_message}")
                    send_gotify_notification("Temperature Alert", alert_message)
                    run_optional_command(optional_command, debug)
                    return  # or handle alert accordingly
        
        time.sleep(check_interval)

def install_service(debug=False):
    with open(SERVICE_FILE_PATH, 'w') as service_file:
        service_file.write(SERVICE_FILE_CONTENT)
    
    subprocess.run(['systemctl', 'daemon-reload'], check=True)
    subprocess.run(['systemctl', 'enable', 'monitor_sensor.service'], check=True)
    subprocess.run(['systemctl', 'start', 'monitor_sensor.service'], check=True)
    print("Service installed and started.")

def uninstall_service(debug=False):
    subprocess.run(['systemctl', 'stop', 'monitor_sensor.service'], check=True)
    subprocess.run(['systemctl', 'disable', 'monitor_sensor.service'], check=True)
    
    if os.path.exists(SERVICE_FILE_PATH):
        os.remove(SERVICE_FILE_PATH)
    
    subprocess.run(['systemctl', 'daemon-reload'], check=True)
    print("Service uninstalled.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor system temperature sensors.")
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--install', action='store_true', help='Install as a system service')
    parser.add_argument('--uninstall', action='store_true', help='Uninstall the system service')
    args = parser.parse_args()

    if args.install:
        install_service(args.debug)
    elif args.uninstall:
        uninstall_service(args.debug)
    else:
        check_and_install_lm_sensors(args.debug)

        sensor, threshold_temp, optional_command = load_config()
        sensor_data = get_sensor_data(args.debug)
        sensors = parse_sensor_data(sensor_data, args.debug)
        
        if sensor is None or threshold_temp is None:
            sensor, threshold_temp, optional_command = display_and_choose_sensors(sensors, args.debug)
            save_config(sensor, threshold_temp, optional_command)
        else:
            print(f"Using saved configuration: Sensor={sensor}, Threshold Temperature={threshold_temp}°C")
            if optional_command:
                print(f"Optional command: {optional_command}")

        monitor_sensor(sensor, threshold_temp, sensors, optional_command, args.debug)
