#!/bin/bash

# Define the installation directory
INSTALL_DIR="$HOME/runtipi"

# Check if runtipi-cli exists in the installation directory
if [ ! -f "$INSTALL_DIR/runtipi-cli" ]; then
  echo "Tipi Tricks must be installed in the runtipi directory."
  exit 1
fi

# Check if click is installed, if not install it
if ! pip show click &> /dev/null; then
  echo "Installing 'click'..."
  pip install click
fi

# Download the Tipi-Tricks repository
echo "Downloading Tipi-Tricks..."
cd $INSTALL_DIR
git clone https://github.com/austinsr1/Tipi-Tricks.git

# Set permissions for tipi-tricks and bin directory
echo "Setting permissions..."
chmod 755 $INSTALL_DIR/Tipi-Tricks/tipi-tricks
chmod -R 755 $INSTALL_DIR/Tipi-Tricks/bin

echo "Tipi-Tricks has been successfully installed in $INSTALL_DIR."
