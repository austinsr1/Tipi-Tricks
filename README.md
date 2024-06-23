# Tipi-Tricks

Command line utility to enhance functionality for your Tipi Homeserver.

**Requirements:** Python 3.10, Click, and [Tipi](https://runtipi.io/)

---

## Tipi Tricks Documentation

### Introduction

**Tipi Tricks** is a utility designed to streamline the management and maintenance of your Tipi environment. Developed in Python, with Click as the sole dependency, Tipi Tricks automates various tasks to ensure your system remains up-to-date, secure, and efficient. Additional optional monitors may require extra packages to function properly.

**Guides will be available in the wiki: https://github.com/austinsr1/Tipi-Tricks/wiki **
---

## Features

### 1. Automatic Tipi Updates

Tipi Tricks can automatically check for and install updates for Tipi, ensuring you always have the latest features and security enhancements.

### 2. Automatic App Updates

Keep your applications up-to-date effortlessly. Tipi Tricks automates the process of checking for and applying updates to the apps installed within your Tipi environment.

### 3. Automatic System Updates

Maintain system security and performance with automatic system updates. Tipi Tricks ensures that your operating system receives the latest patches and upgrades without manual intervention.

### 4. Automatic Backups

Protect your data with regular, automated backups. Tipi Tricks schedules and performs backups, allowing you to restore your system to a previous state in case of any issues.

### 5. Mountpoint Monitoring

Tipi Tricks monitors your mountpoints from `/etc/fstab`, providing alerts (with gotify-cli) if any mountpoints become unavailable. It can stop Tipi containers that require data from the missing mountpoints and automatically restart them when the mountpoints become available again. Apps that will be stopped can be configured in `runtipi/etc/monitor_shares.conf`.

### 6. Space Monitoring

Stay informed about your system’s storage status. Tipi Tricks monitors disk space usage and alerts you when space is running low, helping you avoid potential system slowdowns or crashes. The notification threshold can be configured in `runtipi/etc/monitor_space.conf`. Tipi is set to stop if the install drive reaches 99% capacity and will resume once space is below 99%.

### 7. Temperature Monitoring

Dynamically scan for temperature sensors and allow the user to choose the sensor to monitor. Tipi Tricks can trigger user-defined actions if the sensor's temperature exceeds the user-defined threshold.

### 8. Clearing Docker Cache

Reclaim valuable disk space by clearing the Docker cache.

### 9. Optional Notifications

Receive timely notifications about system events and statuses if the gotify-cli is installed and configured.

---

## Installation

To install Tipi Tricks:

1. Navigate to your runtipi directory.
2. Run the following command:
   ```sh
   curl -L https://raw.githubusercontent.com/austinsr1/Tipi-Tricks/main/install.sh | bash
   ```
3. Run `./tipi-tricks` as root or with sudo.

---

## Usage

```sh
./tipi-tricks
Usage: tipi-tricks [OPTIONS] COMMAND [ARGS]...

  Tipi tricks command group.

Options:
  --help  Show this message and exit.

Commands:
  backup       Backup submenu.
  clear-cache  Clear Docker cache.
  monitors     Monitors submenu.
  updates      Updates submenu.
```
