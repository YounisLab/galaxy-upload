#!/usr/bin/env bash

# Uploads all .bw files in given directory to usegalaxy.org

if [ "$#" -ne "3" ]
then
    echo "Not enough parameters..."
    echo "Usage: lftp_upload <username> <password> <dir>"
    echo "IMPORTANT: Uploads all files in given directory."
    exit 1
fi

usr=$1
pwd=$2
dir=$3

for filename in $dir/*.bw; do
    lftp -c "open -u $usr,$pwd usegalaxy.org; put $filename"
done

echo ">>> All files transferred to FTP-server."
exit 0
