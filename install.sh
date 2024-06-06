#!/bin/bash

# Find the correct pip command
if command -v pip &> /dev/null; then
    PIP_CMD=pip
elif command -v pip3 &> /dev/null; then
    PIP_CMD=pip3
else
    echo "pip or pip3 not found. Please install pip to continue."
    exit 1
fi

# Define the installation directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if runtipi-cli exists in the current directory
if [ ! -f "$SCRIPT_DIR/runtipi-cli" ]; then
    echo "Tipi Tricks must be installed in a directory containing runtipi-cli."
    exit 1
fi

INSTALL_DIR="$SCRIPT_DIR"

# Check if click is installed, if not install it
if ! $PIP_CMD show click &> /dev/null; then
    echo "Installing 'click'..."
    $PIP_CMD install click
fi

# Download the Tipi-Tricks repository
echo "Downloading Tipi-Tricks..."
cd $INSTALL_DIR
git clone https://github.com/austinsr1/Tipi-Tricks.git

# Move bin/, etc/, and tipi-tricks to the runtipi directory
echo "Moving files..."
mv Tipi-Tricks/bin $INSTALL_DIR/
mv Tipi-Tricks/etc $INSTALL_DIR/
mv Tipi-Tricks/tipi-tricks $INSTALL_DIR/

# Set permissions for tipi-tricks and bin directory
echo "Setting permissions..."
chmod 755 $INSTALL_DIR/tipi-tricks
chmod -R 755 $INSTALL_DIR/bin

# Remove the git download directory
echo "Cleaning up..."
rm -rf Tipi-Tricks

echo "Tipi-Tricks has been successfully installed in $INSTALL_DIR."
