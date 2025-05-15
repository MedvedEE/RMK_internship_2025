#!/bin/bash

# This script downloads the GTFS data and stores it in a date-stamped directory.
# Also unzipping the downloaded file.
# It checks if the directory for yesterday's date already exists. If it does, it skips the download.
# If it doesn't, it creates the directory, downloads the GTFS data, and unzips it.
# Usage: ./download_gtfs.sh
# NB: Make sure to give execute permission to the script using chmod +x download_gtfs.sh
# Also check if wget is installed on your system. If not, install it using your package manager.


# Defining variables
DATA_DIR="../data"  # So because data is in the parent directory, we use ../data
YESTERDAY=$(date -d "yesterday" +"%d-%m-%Y")  # Because peatus.ee gives data for yesterday, we're using date for yesterday
YESTERDAY_DIR="$DATA_DIR/$YESTERDAY"
GTFS_URL="http://peatus.ee/gtfs/gtfs.zip"


# Check if yesterday's directory exists
if [ ! -d "$YESTERDAY_DIR" ]; then
  echo "Creating directory: $YESTERDAY_DIR"
  mkdir -p "$YESTERDAY_DIR"
  
  # Download gtfs.zip and rename with yesterday's date
  wget -O "$YESTERDAY_DIR/gtfs_$YESTERDAY.zip" "$GTFS_URL"
  
  # Verify download
  if [ $? -eq 0 ]; then
    echo "Download successful: gtfs_$YESTERDAY.zip"
    echo "Unzipping gtfs_$YESTERDAY.zip"
    # Unzip the downloaded file
    # -q == quiet mote
    unzip -q "$YESTERDAY_DIR/gtfs_$YESTERDAY.zip" -d "$YESTERDAY_DIR"
  else
    echo "Download failed. Cleaning up..."
    rm -rf "$YESTERDAY_DIR"
    exit 1
  fi
else
  echo "Directory already exists: $YESTERDAY_DIR (no download needed)"
fi